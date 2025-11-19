import math
import asyncio
from fastapi import FastAPI, Request, UploadFile, Form, File, APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import traceback
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from Modelling.converter import l_t_id_converter, id_t_l_converter
from Modelling.preprocessing import cleanTextPipeline
from collections import defaultdict
from openai import OpenAI
import os
from groq import Groq
import time
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi.templating import Jinja2Templates
from datetime import datetime
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from backend.forecast.cleaner_shaping import cleaner_function, reshaping
from backend.forecast.model import create_budget_forecast
from backend.Visualize.img_converter import fig_to_base64
from backend.Visualize.vis_forecast import visualize_forecast
from fastapi.middleware.cors import CORSMiddleware
from backend.database import db_setup
from backend.auth import router as auth_router
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database import User
from backend.database import Transaction
from backend.database import get_db
from backend.auth import get_current_user, get_current_user_optional
from backend.transaction import insertTransaction
from backend.budget import forecastTransactions
from backend.budget import deleteBudget
from backend.intent_classfier.classifier_class import lightWeightIntentClassifier
from backend.chatbots.general.knowledge_base_loader import knowledge_base_creation
from backend.chatbots.general.pinecone_store import create_general_index, load_general_index
from backend.chatbots.general.general_chat import general_chat
from backend.chatbots.personal.personal_docs import get_user_docs
from backend.chatbots.personal.pinecone_store import create_user_index, load_user_index
from backend.chatbots.personal.personal_chat import personal_chat
from backend.chatbots.personal.personal_intent import PersonalIntentClassifier
from backend.chatbots.personal.text_sql.llm_sql_chatbot import test_sql 
from backend.chatbots.personal.text_sql.config import data_db
from backend.chatbots.general.clean_transaction import clean_transactions, read_excel_dynamic
from backend.chatbots.chat_memory import save_memory, memory_update, conversation_memory
from backend.classification_helper import classify_transaction
from backend.Visualize.vis_trend import analyze_trends

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],  
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = None
tokenizer = None

class InputText(BaseModel):
    text: str

templates = Jinja2Templates(directory="backend/templates")

def clean_floats(data):
    """Recursively replace NaN/Inf/-Inf values with 0 or None."""
    if isinstance(data, dict):
        return {k: clean_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_floats(i) for i in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return 0.0
        return data
    return data

@app.on_event("startup")
async def load_model():
    global model, tokenizer, label_encoder, classifier

    model_path = Path("backend/transaction_classification/minilm/minilm_transaction_cpu_model").resolve()
    if not model_path.exists():
        raise FileNotFoundError(f"Model path not found: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path), local_files_only=True)

    label_encoder_path = Path("backend/transaction_classification/minilm/label_encoder_minilm.pkl").resolve()
    if not label_encoder_path.exists():
        raise FileNotFoundError(f"Label encoder not found: {label_encoder_path}")
    label_encoder = joblib.load(label_encoder_path)

    classifier = lightWeightIntentClassifier(method = "hybrid")
    BASE_DIR = Path(__file__).resolve().parent
    MODEL_PATH = BASE_DIR / "intent_classfier" / "intentClassifier.pkl"
    classifier.loadModel(filepath = str(MODEL_PATH))

    await db_setup()

app.include_router(auth_router, prefix = '/auth', tags = ["Authentication"])

@app.post("/chat")
async def answer(input_data: InputText, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    user_query = input_data.text
    user_id = current_user.id if current_user else "guest"

    history = conversation_memory[user_id][-3:]
    combined_text = " ".join([f"{msg['role']}: {msg['text']}" for msg in history])
    combined_input = f"{combined_text}\nUser: {user_query}"
    last_bot_message = history[-1]['text'] if history and history[-1]['role'] == 'bot' else ""
    is_followup = any(keyword in last_bot_message.lower() for keyword in [
        'spent', 'transactions', 'expenses', 'npr', 'rupees', 'income', 
        'category', 'breakdown', 'total', 'per day', 'per week'
    ])

    intent, confidence = classifier.predictQuery(user_query)
    
    # Override intent for follow-up questions about personal data
    if is_followup and current_user and any(keyword in user_query.lower() for keyword in [
        'break', 'detail', 'more', 'show', 'list', 'what', 'which', 'how'
    ]):
        print(f"🔄 Overriding intent to 'personal' (follow-up detected)")
        intent = "personal"
        confidence = 0.9

    print(f"Intent: {intent}, Confidence: {confidence}, Is Follow-up: {is_followup}")
    
    if intent == "general" and confidence >= 0.5:
        try:
            store = load_general_index()
            if not store:
                docs = await asyncio.to_thread(knowledge_base_creation, data="materials")
                store = await asyncio.to_thread(create_general_index, docs)
                
            response = await asyncio.to_thread(general_chat, input_text=combined_input, store=store)
    
            if isinstance(response, dict):
                text = response.get("answer")
            else:
                text = response

            memory_update(user_id, "user", user_query)
            memory_update(user_id, "bot", text)

            if current_user:
                await save_memory(db, current_user.id, "user", user_query)
                await save_memory(db, current_user.id, "bot", text)
    
            return {"intent": intent, "confidence": confidence, "response": text}
        
        except Exception as e:
            print(f"Error in general chat: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"intent": intent, "confidence": confidence, "response": f"Error occurred: {str(e)}"}
        
    elif intent == "personal":
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for personal chat")
        
        user_id = current_user.id
        p_classifier = PersonalIntentClassifier()
        
        final_intent = await asyncio.to_thread(
            p_classifier.classify, 
            user_query,
            context=combined_text  
        )
        print(f"Personal intent: {final_intent}")
        
        if final_intent[0] == "personal_rag":
            try:
                store = load_user_index(user_id=current_user.id)
                if not store:
                    docs = await get_user_docs(db, user_id)
                    store = await asyncio.to_thread(create_user_index, docs=docs, user_id=user_id)
                    
                response = await asyncio.to_thread(personal_chat, input_text=combined_input, store=store)
                
                if isinstance(response, dict):
                    text = response.get("answer")
                else:
                    text = response

                memory_update(user_id, "user", user_query)
                memory_update(user_id, "bot", text)
                await save_memory(db, current_user.id, "user", user_query)
                await save_memory(db, current_user.id, "bot", text)
    
                return {"intent": intent, "confidence": confidence, "response": text}
            
            except Exception as e:
                print(f"Error in personal RAG: {str(e)}")
                import traceback
                traceback.print_exc()
                return {"intent": intent, "confidence": confidence, "response": f"Error occurred: {str(e)}"}
            
        elif final_intent[0] == "personal_sql":
            try:
                print(f"🔍 Personal SQL Intent Triggered")
                print(f"User ID: {user_id}")
                print(f"Query: {combined_input}")
                
                t_sql = test_sql(
                    db_config=data_db, 
                    groq_api_key=os.getenv("GROQ_API_KEY")
                )
                await t_sql.initialize()
                
                print("📊 Executing SQL query...")
                result_dict, sql_query = await t_sql.sql_query_answer(user_id=user_id, query=combined_input)
                
                print(f"✅ SQL Query: {sql_query}")
                print(f"✅ Results: {result_dict}")
        
                print("🤖 Generating response with LLM...")
                response = await t_sql._generate_response_with_llm(
                    query=user_query, 
                    results=result_dict, 
                    sql_query=sql_query
                )
                
                print(f"✅ Final Response: {response}")
                
                memory_update(user_id, "user", user_query)
                memory_update(user_id, "bot", response)
                
                if current_user:
                    await save_memory(db, current_user.id, "user", user_query)
                    await save_memory(db, current_user.id, "bot", response)
        
                return {
                    'intent': intent,
                    'confidence': confidence,
                    'response': response,
                    'sql_query': sql_query,
                    'success': True,
                    'data': result_dict
                }
            except Exception as e:
                print(f"❌ SQL Query Error: {e}")
                import traceback
                traceback.print_exc()
                return {
                    'intent': intent,
                    'confidence': confidence,
                    'response': f"I encountered an error while analyzing your transactions: {str(e)}",
                    'success': False
                }
        
        else:
            return {
                "intent": intent,
                "confidence": confidence,
                "response": "I'm not sure how to help with that personal query. Could you rephrase?"
            }
    
    else:
        return {
            "intent": intent,
            "confidence": confidence,
            "response": f"I'm not confident I understood your question correctly (confidence: {confidence:.2f}). Could you please rephrase or ask something about general finance or your personal transactions?"
        }

# @app.post("/predict_accuracy")
# async def predict_accuracy(request: Request, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     client = OpenAI(api_key=OPENAI_API_KEY)
#     try: 
#         df_results = []
#         for file in files:
#             contents = await file.read()
    
#             try:
#                 df = read_excel_dynamic(contents)
#             except Exception:
#                 return {"Error": "Invalid Format"}
            
#             df = df.dropna(subset="Description")
    
#             df_results.append(df)
    
#         df = pd.concat(df_results, ignore_index=True)
#         df = clean_transactions(df)
#         categories = []
    
#         df['processedDescription'] = [cleanTextPipeline(text) for text in df['Description']]

#         for index, row in df.iterrows():
#             category = classify_transaction(row['processedDescription'], row['Dr.'], row['Cr.'], client)
#             categories.append(category)
#             time.sleep(1)

#         df['Category'] = categories
#         txn_acc_stream = BytesIO()
#         df.to_excel(txn_acc_stream, index = False)
    
#         txn_acc_stream.seek(0)
    
#         request.app.state.txn_acc_stream = txn_acc_stream
    
#         await insertTransaction(current_user.id, df, db)

#         data_json = df.to_dict(orient="records")
#         return JSONResponse(content=data_json)

#     except Exception as e:
#         traceback.print_exc() 
#         raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/predict_accuracy")
async def predict_accuracy(request: Request, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    try: 
        df_results = []
        for file in files:
            contents = await file.read()
    
            try:
                df = read_excel_dynamic(contents)
            except Exception:
                return {"Error": "Invalid Format"}
            
            df = df.dropna(subset="Description")
    
            df_results.append(df)
    
        df = pd.concat(df_results, ignore_index=True)
        df = clean_transactions(df)
        categories = []
    
        df['processedDescription'] = [cleanTextPipeline(text) for text in df['Description']]

        for index, row in df.iterrows():
            category = classify_transaction(row['processedDescription'], row['Dr.'], row['Cr.'], client)
            categories.append(category)
            time.sleep(1)

        df['Category'] = categories
        txn_acc_stream = BytesIO()
        df.to_excel(txn_acc_stream, index = False)
    
        txn_acc_stream.seek(0)
    
        request.app.state.txn_acc_stream = txn_acc_stream
    
        await insertTransaction(current_user.id, df, db)

        df_copy = df.copy()
        for col in df_copy.select_dtypes(include=['datetime64']).columns:
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        data_json = df_copy.to_dict(orient="records")
        return JSONResponse(content=data_json)

    except Exception as e:
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
    
@app.post("/predict_speed")
async def predict_speed(request: Request, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    global model, tokenizer, label_encoder
    print('hello')
    try:
        print(f'Number of files received: {len(files)}')
        df_results = []
        for i, file in enumerate(files):
            print(f'Processing file {i+1}: {file.filename}')
            contents = await file.read()
            print(f'File {i+1} size: {len(contents)} bytes')
            
            try:
                df = read_excel_dynamic(contents)
                print(f'File {i+1} read successfully, shape: {df.shape}')
            except Exception as e:
                print(f'Error reading file {i+1}: {str(e)}')
                return {"Error": "Invalid Format"}
            
            print(f'Before dropna: {len(df)} rows')
            df = df.dropna(subset="Description")
            print(f'After dropna: {len(df)} rows')
            df_results.append(df)
        
        print('Concatenating dataframes...')
        df = pd.concat(df_results, ignore_index=True)
        print(f'After concat: {df.shape}')
        
        print('Cleaning transactions...')
        df = clean_transactions(df)
        print(f'After cleaning: {df.shape}')
        print(df)
        
        print('Cleaning text...')
        cleaned_text = [cleanTextPipeline(text) for text in df['Description']]
        print(f'Cleaned {len(cleaned_text)} texts')
        print(cleaned_text[:3])  
        
        print('Tokenizing...')
        final_inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, padding=True, max_length=64)
        print('Tokenization complete')
        
        print('Running model inference...')
        with torch.no_grad():
            outputs = model(**final_inputs)
            preds = torch.argmax(outputs.logits, dim=1).tolist()
        print(f'Predictions: {len(preds)} items')
        
        print('Inverse transforming labels...')
        df['Category'] = label_encoder.inverse_transform(preds)
        print('Categories assigned')
        
        print('Creating Excel stream...')
        txn_spd_stream = BytesIO()
        df.to_excel(txn_spd_stream, index=False)
        txn_spd_stream.seek(0)
        request.app.state.txn_spd_stream = txn_spd_stream
        print('Excel stream created')
        
        print('Inserting transactions to database...')
        await insertTransaction(current_user.id, df, db)
        print('Transactions inserted')
        
        print('Converting to JSON...')
        df_copy = df.copy()
        for col in df_copy.select_dtypes(include=['datetime64']).columns:
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        data_json = df_copy.to_dict(orient="records")
        print(f'Returning {len(data_json)} records')
        
        return JSONResponse(content=data_json)
        
    except Exception as e:
        print(f'EXCEPTION CAUGHT: {str(e)}')
        print(f'Exception type: {type(e).__name__}')
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
    
@app.post("/budget")
async def budget(request: Request, income: int = Form(), saving_amt: int = Form(), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        transactions_df = await get_user_transactions(db, current_user.id)
        
        if transactions_df is None or transactions_df.empty:
            raise HTTPException(
                status_code=404, 
                detail="No transaction history found. Please classify transactions first."
            )
        
        if 'category' not in transactions_df.columns:
            raise HTTPException(
                status_code=400,
                detail="Transaction data missing category information"
            )
        
        cleaned_df = cleaner_function(transactions_df)
        monthly_data = reshaping(cleaned_df)

        forecast_month = None
        
        print(f"\n\nMonthly data shape: {monthly_data.shape[0]}\n\n")

        if monthly_data.shape[0] < 3:
            print("⚠️ Monthly data has fewer than 3 periods — skipping budget forecast.")
            return {
                "message": "Insufficient data for budget forecasting. Need at least 3 months of transaction history.",
                "forecast": {},
                "summary": None,
                "budget": {},
                "image_data": None
            }

        last_month = monthly_data.index[-1]
        forecast_month = last_month + pd.DateOffset(months=1)
        
        forecast, summary, budget = create_budget_forecast(monthly_data, income, saving_amt)
        
        if not forecast:
            print("⚠️ Forecast returned empty.")
            return {
                "message": "Unable to generate forecast with current data",
                "forecast": {},
                "summary": None,
                "budget": {},
                "image_data": None
            }
        
        final_fig1 = None
        try:
            fig1 = visualize_forecast(monthly_data, forecast, summary)
            final_fig1 = fig_to_base64(fig1)
            print('nice')
        except Exception as e:
            print(f"⚠️ Visualization failed: {e}")
            final_fig1 = None
        
        print(f"\n\nBudget: {budget}\n\n")
        
        if budget:
            final_dict = {
                "Category": [],
                "Budget_Amount": [],
                "Forecasted_Amount": []
            }
            
            for key, value in budget.items():
                final_dict['Category'].append(key)
                final_dict['Budget_Amount'].append(value)
            
            for value in forecast.values():
                final_dict['Forecasted_Amount'].append(value)
            
            bf_df = pd.DataFrame(final_dict)
            
            budget_stream = BytesIO()
            bf_df.to_excel(budget_stream, index=False)
            budget_stream.seek(0)
            request.app.state.budget_stream = budget_stream
            
            await forecastTransactions(current_user.id, forecast_month, bf_df, db)
        else:
            request.app.state.budget_stream = None
        
        docs = await get_user_docs(db, current_user.id)
        
        forecast = clean_floats(forecast) if forecast else {}
        summary = clean_floats(summary) if summary else None
        budget = clean_floats(budget) if budget else {}
        
        return {
            "message": "Budget generated successfully",
            "forecast": forecast,
            "summary": summary,
            "budget": budget,
            "image_data": final_fig1,
            "forecast_month": str(forecast_month) if forecast_month else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Budget generation failed: {str(e)}")


async def get_user_transactions(db: AsyncSession, user_id: int) -> pd.DataFrame:
    from sqlalchemy import select
    
    try:
        stmt = select(Transaction).filter(Transaction.user_id == user_id)
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        if not transactions:
            return pd.DataFrame()
        
        data = []
        for txn in transactions:
            data.append({
                'description': txn.description,
                'amount': txn.amount,
                'date_time': txn.date_time,
                'category': txn.category,
                'type': txn.type
            })
        
        df = pd.DataFrame(data)
        return df
        
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        raise
    
@app.post("/download/accurate_classification")
async def donwload_accurate_classification():
    buffer = getattr(app.state, "txn_acc_stream", None)

    if not buffer:
        return {"error": "Classification could not be performed."}
    
    buffer.seek(0)

    response =  StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=transaction_classifiction.xlsx"}
    )

    app.state.txn_acc_stream = None
    return response

@app.post("/download/speed_classification")
async def donwload_speed_classification():
    buffer = getattr(app.state, "txn_spd_stream", None)

    if not buffer:
        return {"error": "Classification could not be performed."}
    
    buffer.seek(0)

    response =  StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=transaction_classifiction.xlsx"}
    )

    app.state.txn_spd_stream = None
    return response

@app.post("/download/budget")
async def download_budget():
    buffer = getattr(app.state, "budget_stream", None)

    if not buffer:
        return{"error": "Budget information was not sufficient."}
    
    buffer.seek(0)

    response = StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=budget.xlsx"}
    )
    app.state.budget_stream = None
    return response