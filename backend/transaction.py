from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import Transaction
import pandas as pd
import traceback

async def insertTransaction(user_id: int, df: pd.DataFrame, db: AsyncSession):
    for _, row in df.iterrows():
        txn = Transaction(
            user_id = user_id,
            reference_code = str(row['Reference Code']),
            date_time = pd.to_datetime(row['Date Time']),
            description = str(row['Description']),
            amount = float(row['Dr.'] if row['Dr.'] > 0 else row['Cr.']),
            type = "expense" if row['Dr.'] > 0 else "income",
            status = str(row['Status']),
            balance = float(row['Balance (NPR)']),
            channel = str(row['Channel']),
            category = str(row['Category'])
        )

        db.add(txn)

    try:
        await db.flush() 
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"\nCommit failed: {e}\n")
        traceback.print_exc()
        raise