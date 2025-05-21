from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from database import connect, initialize_db
import bcrypt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS to allow requests from your React Native app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = None
cursor = None

@app.on_event("startup")
async def startup_event():
    global conn, cursor
    print("Connecting to database...")
    conn = connect()
    cursor = conn.cursor()
    print("Connected.")
    initialize_db()

# Signup schema aligned with frontend
class SignupModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    address: str = ""

@app.post("/signup/")
async def signup(user: SignupModel):

    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT * FROM signup WHERE email = %s", (user.email,))
        
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Split the name into first_name and last_name
        name_parts = user.name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Extract username from email if needed
        username = user.email.split('@')[0]
        
        # Insert user into database
        insert_query = """
        INSERT INTO signup (email, username, password, first_name, last_name, phone_number)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            user.email,
            username,
            hashed_password.decode('utf-8'),
            first_name,
            last_name,
            user.phone
        ))
        conn.commit()
        
        # Get the newly created user_id to return to the frontend
        cursor.execute("SELECT id FROM signup WHERE email = %s", (user.email,))
        new_user = cursor.fetchone()
        user_id = new_user[0] if new_user else None
        
        conn.close()
        
        # Return a response that matches what the frontend expects
        return {
            "message": "Signup successful!",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
