from backend.database import ChatHistory
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession

conversation_memory = defaultdict(list)

async def save_memory(db: AsyncSession, user_id: int, role: str, text: str):
    if not user_id:
        return
    new_entry = ChatHistory(
        user_id = user_id,
        role = role,
        text = text
    )

    db.add(new_entry)
    await db.commit()

def memory_update(user_id: int, role: str, text: str):
    conversation_memory[user_id].append({"role": role, "text": text})
    if len(conversation_memory[user_id]) > 5:
        conversation_memory[user_id] = conversation_memory[user_id][-5:]