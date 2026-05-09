from datetime import datetime
from database import logs_collection

async def log_action(action: str):

    await logs_collection.insert_one({
        "action": action,
        "time": str(datetime.utcnow())
    })