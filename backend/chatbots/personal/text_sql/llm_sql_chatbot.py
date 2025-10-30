import asyncpg
from datetime import datetime
import json
from openai import OpenAI
from typing import Dict, List, Optional
import asyncio
from .config import data_db
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class test_sql:
    def __init__(self, db_config: dict, openai_api_key: str):
        self.db_config = db_config
        self.client = OpenAI(api_key=openai_api_key)
        self.conn = None
        self.schema = """
DATABASE SCHEMA FOR PERSONAL FINANCE APPLICATION:

Table: transactions
Columns:
  - id (integer): Unique transaction identifier
  - user_id (integer): User ID (ALWAYS filter by this!)
  - reference_code (text): Transaction reference code (e.g., '0W8EFGH')
  - date_time (timestamp): Transaction date and time
  - description (text): Transaction description (e.g., 'Ordered food from Foodmandu')
  - amount (numeric): Transaction amount (positive number)
  - type (text): Transaction type - either 'expense' or 'income'
  - status (text): Transaction status (e.g., 'COMPLETE')
  - balance (numeric): Account balance after this transaction
  - channel (text): Transaction channel (e.g., 'App', 'THIRDPARTY')
  - category (text): Transaction category (e.g., 'Dining & Food', 'Travel', 'Groceries & Shopping', 'Personal Care', 'Banking & Finance', 'Entertainment', 'Education', 'Subscriptions', 'Income')

Table: budgets
Columns:
  - id (integer): Unique budget identifier
  - user_id (integer): User ID (ALWAYS filter by this!)
  - month (timestamp): Budget month
  - allocated (numeric): Allocated/recommended budget amount
  - forecast (numeric): Forecasted spending for the category
  - category (text): Budget category name

CRITICAL RULES:
1. ALWAYS include WHERE user_id = {user_id} in every query
2. For spending/expense queries: use WHERE type = 'expense' AND amount > 0
3. For income queries: use WHERE type = 'income' AND amount > 0
4. Categories have spaces and special characters - use ILIKE '%keyword%' for matching
5. Use COALESCE(SUM(...), 0) to handle NULL values in aggregations
6. The date/time column is called 'date_time' (not 'date')
7. Use CAST(date_time AS DATE) when comparing dates only

DATE FILTERS (using date_time column):
- Last month: CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')::date AND CAST(date_time AS DATE) < DATE_TRUNC('month', CURRENT_DATE)::date
- This month: CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE)::date
- Last week: CAST(date_time AS DATE) >= CURRENT_DATE - INTERVAL '7 days'
- Today: CAST(date_time AS DATE) = CURRENT_DATE
- Yesterday: CAST(date_time AS DATE) = CURRENT_DATE - INTERVAL '1 day'

BUDGET TABLE NOTES:
- 'allocated' is the recommended/allocated budget
- 'forecast' is the predicted spending
- Compare actual spending (from transactions) with allocated budget
"""

    async def initialize(self):
        try:
            self.conn = await asyncpg.connect(**self.db_config)

            print("Database connected successfully!!")

        except Exception as e:
            print(f"The following error has occured: {e}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            print("Database disconnected")    

    async def sql_query_answer(self, user_id: int, query: str):

        sql_query = await self.generate_sql_query(user_id, query)

        if not sql_query or sql_query == "CANNOT_ANSWER":
            print("SQL code could not be generated for this query!!")

            return{
                'response': "I can help you with questions about your spending, income, transactions, budgets, and account balance. Could you rephrase your question?",
                'success': False
            }        
        print(f"Generated query: {sql_query}")

        try:
            results = await self.conn.fetch(sql_query)
            result_dict = [dict(row) for row in results]
            print(f"The query returned {len(result_dict)} rows!!")

        except Exception as e:
            print(f"❌ SQL Execution Error: {e}")
            return {
                'response': f"I encountered an error processing your query. Please try rephrasing it.",
                'sql_query': sql_query,
                'success': False,
                'error': str(e)
            }
        
        return result_dict, sql_query
        
    async def generate_sql_query(self, user_id: int, query: str):
        prompt = f"""You are a PostgreSQL expert specializing in personal finance queries.

{self.schema}

CURRENT USER ID: {user_id}
CURRENT DATE: {datetime.now().strftime('%Y-%m-%d')}

USER QUESTION: "{query}"

TASK: Generate a PostgreSQL query to answer this question.

CRITICAL REQUIREMENTS:
1. ALWAYS include WHERE user_id = {user_id}
2. For spending/expense queries: use WHERE type = 'expense' AND amount > 0
3. For income queries: use WHERE type = 'income' AND amount > 0
4. Use ILIKE for case-insensitive category matching
5. Use proper date filters with date_time column (see schema for examples)
6. Return ONLY the SQL query, no explanations
7. If question is NOT about personal finances, return exactly: CANNOT_ANSWER

EXAMPLE QUERIES:

Q: "How much did I spend on groceries last month?"
SQL: SELECT COALESCE(SUM(amount), 0) as total_spending FROM transactions WHERE user_id = {user_id} AND category ILIKE '%groceries%' AND category ILIKE '%shopping' AND type = 'expense' AND amount > 0 AND CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')::date AND CAST(date_time AS DATE) < DATE_TRUNC('month', CURRENT_DATE)::date

Q: "Show my last 10 transactions"
SQL: SELECT date_time, description, amount, type, category, balance FROM transactions WHERE user_id = {user_id} ORDER BY date_time DESC LIMIT 10

Q: "What's my budget status?"
SQL: SELECT b.category, b.allocated as budget_amount, COALESCE(SUM(t.amount), 0) as spent_amount, (b.allocated - COALESCE(SUM(t.amount), 0)) as remaining, b.forecast FROM budgets b LEFT JOIN transactions t ON t.user_id = b.user_id AND t.category = b.category AND t.type = 'expense' AND EXTRACT(MONTH FROM t.date_time) = EXTRACT(MONTH FROM b.month) AND EXTRACT(YEAR FROM t.date_time) = EXTRACT(YEAR FROM b.month) WHERE b.user_id = {user_id} GROUP BY b.category, b.allocated, b.forecast

Q: "How much did I earn last month?"
SQL: SELECT COALESCE(SUM(amount), 0) as total_income FROM transactions WHERE user_id = {user_id} AND type = 'income' AND amount > 0 AND CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')::date AND CAST(date_time AS DATE) < DATE_TRUNC('month', CURRENT_DATE)::date

Q: "My account balance"
SQL: SELECT balance FROM transactions WHERE user_id = {user_id} ORDER BY date_time DESC, id DESC LIMIT 1

Q: "Total spending this month"
SQL: SELECT COALESCE(SUM(amount), 0) as total_spending FROM transactions WHERE user_id = {user_id} AND type = 'expense' AND amount > 0 AND CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE)::date

Q: "How much did I spend on food?"
SQL: SELECT COALESCE(SUM(amount), 0) as total_spending FROM transactions WHERE user_id = {user_id} AND category ILIKE '%food%' AND type = 'expense' AND amount > 0

Q: "Show my travel expenses this month"
SQL: SELECT date_time, description, amount, balance FROM transactions WHERE user_id = {user_id} AND category ILIKE '%travel%' AND type = 'expense' AND CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE)::date ORDER BY date_time DESC

Q: "What did I spend at Foodmandu?"
SQL: SELECT date_time, description, amount, category FROM transactions WHERE user_id = {user_id} AND description ILIKE '%foodmandu%' AND type = 'expense' ORDER BY date_time DESC

Q: "My spending breakdown this month"
SQL: SELECT category, COALESCE(SUM(amount), 0) as total, COUNT(*) as transaction_count FROM transactions WHERE user_id = {user_id} AND type = 'expense' AND CAST(date_time AS DATE) >= DATE_TRUNC('month', CURRENT_DATE)::date GROUP BY category ORDER BY total DESC

NOW GENERATE SQL FOR THE USER'S QUESTION:"""
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a PostgreSQL expert. Generate ONLY the SQL query, nothing else. No markdown, no explanations."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=400
            )

            sql = response.choices[0].message.content.strip()

            sql = sql.replace("```sql", "").replace("```", "").strip()
            
            sql = sql.split(';')[0].strip()

            return sql
            
        except Exception as e:
            print(f"❌ LLM SQL Generation Error: {e}")
            return None
        
    async def _generate_response_with_llm(self, query: str, results: List[Dict], sql_query: str) -> str:
        """Use LLM to generate natural language response from SQL results"""
        
        results_str = json.dumps(results, indent=2, default=str)
        
        prompt = f"""You are a friendly and helpful personal finance assistant.

USER QUESTION: "{query}"

SQL QUERY EXECUTED:
{sql_query}

QUERY RESULTS:
{results_str}

TASK: Generate a natural, conversational response to answer the user's question.

GUIDELINES:
1. Answer directly and naturally in a friendly tone
2. Use EXACT numbers from the results - don't approximate
3. Format currency as "NPR X,XXX.XX" (Nepalese Rupees)
4. If results are empty, say so politely
5. For transaction lists: format with dates, descriptions, amounts, and categories
6. For budget status: show spent vs budget (allocated) with percentages
7. For comparisons: highlight differences clearly
8. Keep response concise (under 200 words) unless listing many transactions
9. Add helpful context when relevant (e.g., "That's about NPR 890 per week")
10. Use emojis sparingly for visual appeal (💰 📅 ✅ ⚠️)

RESPONSE:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a friendly personal finance assistant. Be concise, accurate, and helpful."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ LLM Response Generation Error: {e}")
            # Fallback: basic formatting
            if results:
                return f"Here are the results: {results_str}"
            else:
                return "No data found for your query."
            
if __name__ == "__main__":
    async def main():
        tsql = test_sql(db_config=data_db, openai_api_key=OPENAI_API_KEY)
        await tsql.initialize()
        user_id = 9
        user_query = "How much did i spend in total last month?"
        result_dict, sql_query = await tsql.sql_query_answer(user_query, user_id)
        response = await tsql._generate_response_with_llm(user_query, result_dict, sql_query)
        print(response)

    asyncio.run(main())