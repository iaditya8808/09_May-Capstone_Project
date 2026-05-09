from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from bson import ObjectId

from models import (
    Book,
    Member,
    Borrow,
    User
)

from database import (
    books_collection,
    members_collection,
    borrow_collection,
    users_collection,
    logs_collection
)

from auth import create_token, verify_token
from csv_upload import read_csv
from logger import log_action

router = APIRouter()

# -----------------------------
# HOME
# -----------------------------

@router.get("/")
async def home():

    return {
        "message": "LibTrack API Running"
    }

# -----------------------------
# REGISTER USER
# -----------------------------

@router.post("/register")
async def register(user: User):

    existing_user = await users_collection.find_one(
        {"username": user.username}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    await users_collection.insert_one(user.dict())

    await log_action(
        f"New user registered: {user.username}"
    )

    return {"message": "User registered"}

# -----------------------------
# LOGIN
# -----------------------------

@router.post("/login")
async def login(user: User):

    db_user = await users_collection.find_one(
        {"username": user.username}
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    if db_user["password"] != user.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_token({
        "username": user.username
    })

    await log_action(
        f"User login: {user.username}"
    )

    return {
        "access_token": token
    }

# -----------------------------
# ADD BOOK
# -----------------------------

@router.post("/books")
async def add_book(book: Book, username: str = Depends(verify_token)):

    existing_book = await books_collection.find_one(
        {"isbn": book.isbn}
    )

    if existing_book:
        raise HTTPException(
            status_code=400,
            detail="Book already exists"
        )

    result = await books_collection.insert_one(
        book.dict()
    )

    await log_action(
        f"Book added: {book.title}"
    )

    return {
        "message": "Book added",
        "id": str(result.inserted_id)
    }

# -----------------------------
# GET BOOKS
# -----------------------------

@router.get("/books")
async def get_books(username: str = Depends(verify_token)):

    books = []

    async for book in books_collection.find():

        book["_id"] = str(book["_id"])

        books.append(book)

    return books

# -----------------------------
# GET SINGLE BOOK
# -----------------------------

@router.get("/books/{book_id}")
async def get_single_book(book_id: str, username: str = Depends(verify_token)):

    book = await books_collection.find_one(
        {"_id": ObjectId(book_id)}
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    book["_id"] = str(book["_id"])

    return book

# -----------------------------
# UPDATE BOOK
# -----------------------------

@router.put("/books/{book_id}")
async def update_book(
    book_id: str,
    updated_book: Book,
    username: str = Depends(verify_token)
):

    await books_collection.update_one(
        {"_id": ObjectId(book_id)},
        {
            "$set": updated_book.dict()
        }
    )

    await log_action("Book updated")

    return {"message": "Book updated"}

# -----------------------------
# DELETE BOOK
# -----------------------------

@router.delete("/books/{book_id}")
async def delete_book(book_id: str, username: str = Depends(verify_token)):

    await books_collection.delete_one(
        {"_id": ObjectId(book_id)}
    )

    await log_action("Book deleted")

    return {"message": "Book deleted"}

# -----------------------------
# ADD MEMBER
# -----------------------------

@router.post("/members")
async def add_member(member: Member, username: str = Depends(verify_token)):

    existing_member = await members_collection.find_one(
        {"email": member.email}
    )

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="Member with this email already exists"
        )

    result = await members_collection.insert_one(
        member.dict()
    )

    await log_action(
        f"Member added: {member.name}"
    )

    return {
        "message": "Member added",
        "id": str(result.inserted_id)
    }

# -----------------------------
# GET MEMBERS
# -----------------------------

@router.get("/members")
async def get_members(username: str = Depends(verify_token)):

    members = []

    async for member in members_collection.find():

        member["_id"] = str(member["_id"])

        members.append(member)

    return members

# -----------------------------
# BORROW BOOK
# -----------------------------

@router.post("/borrow")
async def borrow_book(data: Borrow, username: str = Depends(verify_token)):

    book = await books_collection.find_one(
        {"title": data.book_title}
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    if book["available_copies"] <= 0:
        raise HTTPException(
            status_code=400,
            detail="Book unavailable"
        )

    active_borrow = await borrow_collection.find_one({
        "member_name": data.member_name,
        "book_title": data.book_title,
        "status": "BORROWED"
    })

    if active_borrow:
        raise HTTPException(
            status_code=400,
            detail="User has already borrowed this book"
        )

    await books_collection.update_one(
        {"title": data.book_title},
        {
            "$inc": {
                "available_copies": -1
            }
        }
    )

    await borrow_collection.insert_one({
        "member_name": data.member_name,
        "book_title": data.book_title,
        "status": "BORROWED"
    })

    await log_action(
        f"Book borrowed: {data.book_title}"
    )

    return {"message": "Book borrowed"}

# -----------------------------
# RETURN BOOK
# -----------------------------

@router.post("/return")
async def return_book(data: Borrow, username: str = Depends(verify_token)):

    active_borrow = await borrow_collection.find_one({
        "member_name": data.member_name,
        "book_title": data.book_title,
        "status": "BORROWED"
    })

    if not active_borrow:
        raise HTTPException(
            status_code=400,
            detail="Active borrow record not found"
        )

    await books_collection.update_one(
        {"title": data.book_title},
        {
            "$inc": {
                "available_copies": 1
            }
        }
    )

    await borrow_collection.update_one(
        {
            "_id": active_borrow["_id"]
        },
        {
            "$set": {
                "status": "RETURNED"
            }
        }
    )

    await log_action(
        f"Book returned: {data.book_title}"
    )

    return {"message": "Book returned"}

# -----------------------------
# BORROW HISTORY
# -----------------------------

@router.get("/borrow-history")
async def borrow_history(username: str = Depends(verify_token)):

    records = []

    async for item in borrow_collection.find():

        item["_id"] = str(item["_id"])

        records.append(item)

    return records

# -----------------------------
# CSV BOOK UPLOAD
# -----------------------------

@router.post("/upload-books")
async def upload_books(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):

    books = read_csv(file.file)

    inserted_count = 0
    if books:
        for book_data in books:
            existing_book = await books_collection.find_one(
                {"isbn": str(book_data.get("isbn"))}
            )
            if not existing_book:
                await books_collection.insert_one(book_data)
                inserted_count += 1

    await log_action(
        f"CSV books uploaded: {inserted_count} new books added"
    )

    return {
        "message": "Books processed",
        "total_new_books": inserted_count,
        "total_in_csv": len(books) if books else 0
    }

# -----------------------------
# ANALYTICS
# -----------------------------

@router.get("/analytics")
async def analytics(username: str = Depends(verify_token)):

    total_books = await books_collection.count_documents({})

    total_members = await members_collection.count_documents({})

    total_borrows = await borrow_collection.count_documents({})

    return {
        "total_books": total_books,
        "total_members": total_members,
        "total_borrows": total_borrows
    }

# -----------------------------
# LOGS
# -----------------------------

@router.get("/logs")
async def get_logs(username: str = Depends(verify_token)):

    logs = []

    async for log in logs_collection.find():

        log["_id"] = str(log["_id"])

        logs.append(log)

    return logs