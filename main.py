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

    @app.post("/lost_pet/")
def report_lost_pet(data: LostPetReport):
    conn = connect()
    cursor = conn.cursor()
    query = """
    INSERT INTO lost_pets (pet_id, location, last_seen, description)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (data.pet_id, data.location, data.last_seen, data.description))
    conn.commit()
    conn.close()
    return {"message": "Lost pet reported"}


    @app.post("/found_pet/")
def report_found_pet(data: FoundPetReport):
    conn = connect()
    cursor = conn.cursor()
    query = """
    INSERT INTO found_pets (pet_id, found_location, found_date, description)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (data.pet_id, data.found_location, data.found_date, data.description))
    conn.commit()
    conn.close()
    return {"message": "Found pet reported"}

    @app.get("/adoptable_pets/")
def get_adoptable_pets():
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT * FROM adoptable_pets WHERE status = 'Available'"
    cursor.execute(query)
    pets = cursor.fetchall()
    conn.close()
    return {"adoptable_pets": pets}


    @app.get("/pet_matches/")
def get_matching_pets():
    conn = connect()
    cursor = conn.cursor()
    query = """
    SELECT * FROM pet_matches
    JOIN lost_pets ON pet_matches.lost_pet_id = lost_pets.id
    JOIN found_pets ON pet_matches.found_pet_id = found_pets.id
    """
    cursor.execute(query)
    matches = cursor.fetchall()
    conn.close()
    return {"matches": matches}



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
