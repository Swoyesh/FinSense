# def classify_transaction(description, debit, credit, client):
#     prompt = f"""
# You are a financial transaction classifier.
# Classify the following transaction description into one of these categories:
# Groceries & Shopping, Banking & Finance, Dining & Food, Income,
# Subscriptions, Personal Care, Entertainment, Travel, Education.

# Transaction description: "{description}"
# Credit amount (Cr.): {credit}
# Debit amount (Dr.): {debit}

# remember if credit is not 0.0 or 0 and debit is 0 or 0.0 then it is income category

# Only reply with the category name.
# """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0
#         )
#         category = response.choices[0].message.content.strip()
#         return category
#     except Exception as e:
#         print(f"Error classifying '{description}': {e}")
#         return "Error"

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client at module level
GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_transaction(description, debit, credit, client):
    prompt = f"""You are a financial transaction classifier.

Classify this transaction into ONE category:
Groceries & Shopping, Banking & Finance, Dining & Food, Income, Subscriptions, Personal Care, Entertainment, Travel, Education

Transaction: "{description}"
Debit: {debit}, Credit: {credit}

Rule: If Credit > 0 and Debit = 0, classify as "Income"

Reply with ONLY the category name.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error classifying '{description}': {e}")
        return "Error"