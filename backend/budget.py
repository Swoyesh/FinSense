from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from backend.database import Budget
import traceback
from datetime import datetime
from sqlalchemy import delete

async def forecastTransactions(user_id: int, forecast_month: str, df: pd.DataFrame, db: AsyncSession):
    for _, row in df.iterrows():
        bdt = Budget(
            user_id = int(user_id),
            month = str(forecast_month),
            allocated = float(row['B_Amount']),
            forecast = float(row['F_Amount']),
            category = str(row['Category']),
        )

        db.add(bdt)

        try:
            await db.flush()
            await db.commit()
        
        except Exception as e:
            await db.rollback()
            print(f"\nCommit failed: {e}\n")
            traceback.print_exc()
            raise

async def deleteBudget(db: AsyncSession):
    today = datetime.today().replace(day = 1)
    cutoff_date = (today.replace(day = 1) - pd.DateOffset(months = 3)).strftime("%Y-%m")

    stmt = delete(Budget).where(Budget.month < cutoff_date)
    await db.execute(stmt)
    await db.commit()