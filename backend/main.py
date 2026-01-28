from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel, Field , field_validator
import time
app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Request comes in
    start_time = time.time()

    print(f"Incoming Request → {request.method} {request.url.path}")

    # Pass request to the actual endpoint
    response = await call_next(request)

    # After endpoint finishes, calculate time taken
    process_time = time.time() - start_time

    print(
        f"Completed Response → Status: {response.status_code} "
        f"in {process_time:.4f} seconds"
    )

    return response

# temporary  database
library_db = {}


# Books BluePrints with Validation
class Book(BaseModel):
    id: int
    title: str = Field(..., min_length=1)
    author: str
    year: int = Field(..., ge=1000, le=2026)
    isbn: str = Field(..., min_length=10, max_length=13)

    @field_validator("year")
    def validate_year(cls, value):
        if value > 2026:
            raise ValueError("Year must not exceed 2026")
        if value < 1000:
            raise ValueError("Year must be at least 1000")
        return value

# Root Route
@app.get(
    "/",
    summary="Check API status",
    description="This endpoint confirms that the Digital Library FastAPI service is running properly."
)
def home():
    return {"message": "FastAPI Digital Library Service is running"}


# Add Books
@app.post(
    "/books",
    tags=["Library"],
    summary="Add a new book",
    description="Use this endpoint to add a new book into the digital library system. Each book must have a unique ID."
)
def add_book(book: Book):
    if book.id in library_db:
        raise HTTPException(
            status_code=400,
            detail="Book with this ID already exists"
        )

    library_db[book.id] = book
    return {"message": "Book added successfully", "book": book}



# Getting Books
@app.get(
    "/books",
    tags=["Library"],
    summary="Get all books",
    description="This endpoint retrieves the complete list of all books currently stored in the digital library."
)
def get_all_books():
    return list(library_db.values())



# Taking Book by ID
@app.get(
    "/books/{book_id}",
    tags=["Library"],
    summary="Get book by ID",
    description="This endpoint fetches a specific book using its unique ID. If the book does not exist, it returns a 404 error."
)
def get_book(book_id: int):
    if book_id not in library_db:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return library_db[book_id]


#Update Book
@app.put(
    "/books/{book_id}",
    tags=["Library"],
    summary="Update book details",
    description="This endpoint updates an existing book's information. If the book ID does not exist, it returns a 404 error."
)
def update_book(book_id: int, updated_book: Book):

    if book_id not in library_db:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    library_db[book_id] = updated_book
    return {"message": "Book updated successfully", "book": updated_book}


# Remove Books
@app.delete(
    "/books/{book_id}",
    tags=["Library"],
    summary="Delete a book",
    description="This endpoint removes a book from the library system using its ID. If the book is not found, it returns a 404 error."
)
def delete_book(book_id: int):

    if book_id not in library_db:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    del library_db[book_id]
    return {"message": "Book deleted successfully"}

