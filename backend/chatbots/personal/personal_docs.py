from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import SessionLocal, Transaction, Budget 

async def get_user_docs(db: AsyncSession, user_id: int):
    txns = await db.execute(select(Transaction).where(Transaction.user_id == user_id))
    budgets = await db.execute(select(Budget).where(Budget.user_id == user_id))

    docs = []

    for txn in txns.scalars(): 
        docs.append({
            "text": f"Transaction on {txn.date_time}: {txn.description}. Amount: {txn.amount} ({txn.type}), Category: {txn.category}, Balance: {txn.balance}",
            "metadata": {"table": "transactions", "id": txn.id, "user_id": user_id}
        })

    for budget in budgets.scalars():
        docs.append({
            "text": f"Budget for {budget.category}: allocation {budget.allocated}, prediction {budget.forecast}",
            "metadata": {"table": "budgets", "id": budget.id, "user_id": user_id}
        })

    return docs

if __name__ == "__main__":
    import asyncio

    async def main():
        async with SessionLocal() as session: 
            docs = await get_user_docs(session, user_id=1)
            for doc in docs:
                print(doc)

    asyncio.run(main())