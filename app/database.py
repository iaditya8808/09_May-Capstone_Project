import os
from dotenv import load_dotenv
load_dotenv()
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)

db = client.libtrack

books_collection = db.books
members_collection = db.members
borrow_collection = db.borrows
users_collection = db.users
logs_collection = db.logs