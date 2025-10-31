import math
import asyncio
from fastapi import FastAPI, Request, UploadFile, Form, File, APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import traceback
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from Modelling.converter import l_t_id_converter, id_t_l_converter
from Modelling.preprocessing import cleanTextPipeline
from collections import defaultdict
import os
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi.templating import Jinja2Templates
from datetime import datetime
from io import BytesIO
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
# from backend.Visualize.vis_trend import analyze_trends

model_path = os.path.abspath("backend/saved_model")
unique_labels = ['Personal Care', 'Income', 'Banking & Finance', 'Dining & Food', 'Groceries & Shopping', 'Subscriptions', 'others', 'Entertainment', 'Travel', 'Education']

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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = None
tokenizer = None
label_to_id = None
id_to_label = None

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
    global model, tokenizer, label_to_id, id_to_label, classifier
    label_to_id = l_t_id_converter(unique_labels)
    id_to_label = id_t_l_converter(label_to_id)

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    classifier = lightWeightIntentClassifier(method = "hybrid")
    BASE_DIR = Path(__file__).resolve().parent
    MODEL_PATH = BASE_DIR / "intent_classfier" / "intentClassifier.pkl"
    classifier.loadModel(filepath = str(MODEL_PATH))

    await db_setup()

@app.get("/")
async def form_load(request: Request):
    return templates.TemplateResponse("index.html",{
        "request": request
    })

app.include_router(auth_router, prefix = '/auth', tags = ["Authentication"])

@app.post("/chat")
async def answer(input_data: InputText, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    user_query = input_data.text
    user_id = current_user.id if current_user else "guest"

    history = conversation_memory[user_id][-3:]
    combined_text = " ".join([f"{msg['role']}: {msg['text']}" for msg in history])
    combined_input = f"{combined_text}\nUser: {user_query}"

    intent, confidence = classifier.predictQuery(user_query)
    
    if intent == "general" and confidence >=0.6:
        try:
            store = load_general_index()
            if not store:
                docs = await asyncio.to_thread(knowledge_base_creation, data = "materials")
                store = await asyncio.to_thread(create_general_index, docs)
                
            response = await asyncio.to_thread(general_chat, input = combined_input, store = store)
    
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
            return {"intent": intent, "confidence": confidence, "response": f"Error occurred: {str(e)}"}
        
    elif intent == "personal":
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for personal chat")
        
        user_id = current_user.id
        p_classifier = PersonalIntentClassifier()
        final_intent = await asyncio.to_thread(p_classifier.classify, user_query)
        if final_intent[0] == "personal_rag":
            try:
                store = load_user_index(user_id = current_user.id)
                if not store:
                    docs = await get_user_docs(db, user_id)
                    store = await asyncio.to_thread(create_user_index, docs = docs, user_id = user_id)
                    
                response = await asyncio.to_thread(personal_chat, input = combined_input, store = store)
                
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
    
                return {"intent": intent, "confidence": confidence, "response": f"Error occurred: {str(e)}"}
            
        elif final_intent[0] == "personal_sql":

            try:
                t_sql = test_sql(db_config=data_db, openai_api_key=OPENAI_API_KEY)
                await t_sql.initialize()
                result_dict, sql_query = await t_sql.sql_query_answer(user_id = user_id, query = combined_input)
    
                response = await t_sql._generate_response_with_llm(query = user_query, results = result_dict, sql_query = sql_query)

                memory_update(user_id, "user", user_query)
                memory_update(user_id, "bot", response)
                await save_memory(db, current_user.id, "user", user_query)
                await save_memory(db, current_user.id, "bot", response)
    
                return {
                'response': response,
                'sql_query': sql_query,
                'success': True,
                'data': result_dict
                }

            except Exception as e:
                print(f"❌ LLM Response Generation Error: {e}")
    return {
    "intent": intent,
    "confidence": confidence,
    "response": "I'm not confident enough to answer that right now. Could you please rephrase your question or ask another question?"
    }

@app.post("/predict_budget")
async def predict(request: Request,  income: int = Form(), saving_amt: int = Form(), files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    global model, tokenizer, label_to_id, id_to_label

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
    
        results = []
        categories = []
    
        cleaned_text = [cleanTextPipeline(text) for text in df['Description']]

        final_inputs = tokenizer(
            cleaned_text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = model(**final_inputs)
            probs = F.softmax(outputs.logits, dim=1)
            predicted_classes = torch.argmax(probs, dim=1)

        for i, text in enumerate(df['Description']):
            pred_class = predicted_classes[i].item()
            confidence = probs[i][pred_class].item()
        
            results.append({
                "text": text,
                "category": id_to_label[pred_class],
                "confidence": f"{confidence:.2f}"
            })
        
            categories.append(id_to_label[pred_class])
    
        df['Category'] = categories
        txn_stream = BytesIO()
        df.to_excel(txn_stream, index = False)
    
        txn_stream.seek(0)
    
        request.app.state.txn_stream = txn_stream
    
        await deleteBudget(db)
    
        await insertTransaction(current_user.id, df, db)
    
        cleaned_df = cleaner_function(df)
    
        monthly_data = reshaping(cleaned_df)

        forecast_month = None

        print(f"\n\nMonthly data shape: {monthly_data.shape[0]}\n\n")

        # If monthly_data has less than 3 rows overall -> skip budget forecasting.
        if monthly_data.shape[0] < 3:
            print("⚠️ Monthly data has fewer than 3 periods — skipping budget forecast.")
            # still prepare the transaction excel and return classification results
            forecast = {}
            summary = None
            budget = {}
            final_fig1 = None  # no image


        else:
            last_month = monthly_data.index[-1]
            forecast_month = last_month + pd.DateOffset(months = 1)
        
            # call the forecast function (it is now safer)
            forecast, summary, budget = create_budget_forecast(monthly_data, income, saving_amt)
        
            # If create_budget_forecast returns None/empty budget (e.g., per-category insufficient),
            # handle it gracefully:
            if not forecast:
                print("⚠️ Forecast returned empty. Skipping image generation.")
                final_fig1 = None
            else:
                # visualize only if forecast and monthly_data okay
                try:
                    fig1 = visualize_forecast(monthly_data, forecast, summary)
                    final_fig1 = fig_to_base64(fig1)
                except Exception as e:
                    print(f"⚠️ Visualization failed: {e}")
                    final_fig1 = None
    
        print(f"\n\nBudget: {budget}\n\n")
        print(f"\n\Figure: {final_fig1}\n\n")
        if budget:
            final_dict = {"Category": [], "Budget_Amount": [], "Forecasted_Amount": []}
            for key, value in budget.items():
                final_dict['Category'].append(key)
                final_dict['Budget_Amount'].append(value)
            for value in forecast.values():
                final_dict['Forecasted_Amount'].append(value)
            bf_df = pd.DataFrame(final_dict)
            budget_stream = BytesIO()
            bf_df.to_excel(budget_stream, index = False)
            budget_stream.seek(0)
            request.app.state.budget_stream = budget_stream
            await forecastTransactions(current_user.id, forecast_month, bf_df, db)
        else:
            # clear previous streams if any
            request.app.state.budget_stream = None
    
        fig1 = visualize_forecast(monthly_data, forecast, summary)
        # fig2 = analyze_trends(monthly_data)
    
        final_fig1 = fig_to_base64(fig1)
        # final_fig2 = fig_to_base64(fig2)
    
        docs = await get_user_docs(db, current_user.id)
    
        # create_user_index(docs, current_user.id)

        forecast = clean_floats(forecast) if forecast else {}
        summary = clean_floats(summary) if summary else None
        budget = clean_floats(budget) if budget else {}
        
        return {
            "results": results,
            "forecast": forecast,
            "summary": summary,
            "budget": budget,
            "image_data": final_fig1
        }
    
    except Exception as e:
        traceback.print_exc()  # log full traceback to console
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

# @app.post("/budget")
# async def budget(request: Request, files: List[UploadFile] = File(...)):
#     results = []
#     for file in files:
#         contents = await file.read()
#         try:
#             df = pd.read_excel(BytesIO(contents), skiprows=8)
#         except Exception:
#             return {"Error": "Invalid Format"}
        
#         df = df.dropna(subset = "Description")
        
#         results.append(df.to_html)

#     for result in results:
#         print(result)

#     return templates.TemplateResponse("index.html",{
#         "request": request,
#         "bud_results": results
#     })

@app.post("/download/classification")
async def donwload_classification():
    buffer = getattr(app.state, "txn_stream", None)

    if not buffer:
        return {"error": "Classification could not be performed."}
    
    buffer.seek(0)

    response =  StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=transaction_classifiction.xlsx"}
    )

    app.state.txn_stream = None
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