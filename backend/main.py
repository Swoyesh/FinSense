from fastapi import FastAPI, Request, UploadFile, Form, File, APIRouter, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from Modelling.converter import l_t_id_converter, id_t_l_converter
from Modelling.preprocessing import cleanTextPipeline
import os
import pandas as pd
from fastapi.templating import Jinja2Templates
from io import BytesIO
from backend.forecast.cleaner_shaping import cleaner_function, reshaping
from backend.forecast.model import create_budget_forecast
from backend.Visualize.img_converter import fig_to_base64
from backend.Visualize.vis_forecast import visualize_forecast
from backend.database import db_setup
from backend.auth import router as auth_router
from typing import List
from sqlalchemy.orm import Session
from backend.database import User
from backend.database import get_db
from backend.auth import get_current_user
from backend.transaction import insertTransaction
from backend.budget import forecastTransactions
from backend.budget import deleteBudget
# from backend.Visualize.vis_trend import analyze_trends

model_path = os.path.abspath("backend/saved_model")
unique_labels = ['Personal Care', 'Income', 'Banking & Finance', 'Dining & Food', 'Groceries & Shopping', 'Subscriptions', 'others', 'Entertainment', 'Travel', 'Education']

app = FastAPI()

model = None
tokenizer = None
label_to_id = None
id_to_label = None

class InputText(BaseModel):
    text: str

templates = Jinja2Templates(directory="backend/templates")

@app.on_event("startup")
async def load_model():
    global model, tokenizer, label_to_id, id_to_label
    label_to_id = l_t_id_converter(unique_labels)
    id_to_label = id_t_l_converter(label_to_id)

    print(f'ids: {id_to_label}')

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    await db_setup()

@app.get("/")
async def form_load(request: Request):
    return templates.TemplateResponse("index.html",{
        "request": request
    })

app.include_router(auth_router, prefix = '/auth', tags = ["Authentication"])

@app.post("/predict_budget")
async def predict(request: Request, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    global model, tokenizer, label_to_id, id_to_label

    df_results = []
    for file in files:
        contents = await file.read()

        try:
            df = pd.read_excel(BytesIO(contents), skiprows=8)
        except Exception:
            return {"Error": "Invalid Format"}
        
        df = df.dropna(subset="Description")

        df_results.append(df)

    df = pd.concat(df_results, ignore_index=True)

    results = []
    categories = []

    for inputs in df["Description"]:

        cleaned_inputs = cleanTextPipeline(inputs)

        final_inputs = tokenizer(cleaned_inputs, return_tensors = 'pt', padding = True, truncation = True, max_length = 128)

        with torch.no_grad():
            outputs = model(**final_inputs)
            probs = F.softmax(outputs.logits, dim = 1)
            predicted_class = torch.argmax(probs, dim = 1).item()
            confidence = probs[0][predicted_class].item()

        results.append({
            "text": inputs,  
            "category": id_to_label[predicted_class],
            "confidence": f"{confidence:.2f}"
        })

        categories.append(id_to_label[predicted_class])

    df['Category'] = categories

    await deleteBudget(db)

    await insertTransaction(current_user.id, df, db)

    cleaned_df = cleaner_function(df)

    monthly_data = reshaping(cleaned_df)

    last_month = monthly_data.index[-1]
    forecast_month = last_month + pd.DateOffset(months = 1)

    forecast, summary, budget = create_budget_forecast(monthly_data, 500000, 90000)

    final_dict = {"Category": [], "B_Amount": [], "F_Amount": []}

    for key, value in budget.items():
        final_dict['Category'].append(key)
        final_dict['B_Amount'].append(value)

    for value in forecast.values():
        final_dict['F_Amount'].append(value)

    bf_df = pd.DataFrame(final_dict)

    await forecastTransactions(current_user.id, forecast_month, bf_df, db)

    fig1 = visualize_forecast(monthly_data, forecast, summary)
    # fig2 = analyze_trends(monthly_data)

    final_fig1 = fig_to_base64(fig1)
    # final_fig2 = fig_to_base64(fig2)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": results,
        "forecast": forecast,
        "summary": summary,
        "budget": budget,
        "image_data": final_fig1,
        # "image_data_trend": final_fig2
    })

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