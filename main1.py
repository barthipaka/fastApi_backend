from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStrz
from jose import jwt, JWTError
from typing import List, Dict
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import get_database_connection
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bearer = HTTPBearer()
templates = Jinja2Templates(directory="templates")

# Secret key for signing JWT tokens
SECRET_KEY = "1234123123"
ALGORITHM = "HS256"

class User(BaseModel):
    ename: str
    epassword: str
    email: EmailStr
    phone: int

class LoginRequest(BaseModel):
    email: EmailStr
    epassword: str

class UserResponse(BaseModel):
    name: str
    email: EmailStr
    phone: int
    password: str  # Added password field

# Function to generate JWT token
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/protected/")
async def protected_route(credentials: HTTPAuthorizationCredentials = Security(bearer)):
    return {"token": credentials.credentials}

async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(bearer), cursor=Depends(get_database_connection)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid JWT Token")
    try:
        token = authorization.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = "SELECT email FROM employeesData WHERE email = %s"
    values = (email,)
    await cursor.execute(query, values)
    user = await cursor.fetchone()

    if user is None:
        raise credentials_exception

    return user

@app.get("/user_details/", response_class=HTMLResponse)
async def get_user_details(request: Request, user: Dict = Depends(get_current_user), cursor=Depends(get_database_connection)):
    email = user['email']
    query = "SELECT ename, email, phone, epassword FROM employeesData WHERE email = %s"
    values = (email,)

    try:
        await cursor.execute(query, values)
        user_record = await cursor.fetchone()

        if user_record:
            return templates.TemplateResponse("user_details.html", {"request": request, "user": user_record})
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/", response_class=HTMLResponse)
async def get_all_users(request: Request, cursor=Depends(get_database_connection)):
    query = "SELECT ename, email, phone, epassword FROM employeesData"

    try:
        await cursor.execute(query)
        users = await cursor.fetchall()

        return templates.TemplateResponse("all_users.html", {"request": request, "users": users})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_user/")
async def create_user(user: User, cursor=Depends(get_database_connection)):
    # Check if the email already exists
    check_query = "SELECT email FROM employeesData WHERE email = %s"
    values = (user.email,)
    
    await cursor.execute(check_query, values)
    existing_user = await cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_password = bcrypt.hashpw(user.epassword.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    insert_query = "INSERT INTO employeesData (ename, email, epassword, phone) VALUES (%s, %s, %s, %s)"
    values = (user.ename, user.email, hashed_password, user.phone)

    try:
        await cursor.execute(insert_query, values)
        await cursor.connection.commit()

        # Send account creation notification email
        await send_account_creation_email(user.email)

        return {"message": "User created successfully"}
    except Exception as e:
        await cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Function to send an account creation email
async def send_account_creation_email(email: str):
    body = "Your account has been created successfully."

    message = MIMEMultipart()
    message["From"] = "rakeshbarthipaka@gmail.com"
    message["To"] = email
    message["cc"]="rakeshbarthipaka@gmail.com"
    message["Subject"] = "Account Creation Notification"

    message.attach(MIMEText(body, "html"))

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="rakeshbarthipaka@gmail.com",
        password="mohcccndmtntsbdi",
    )

# Function to send a login notification email
async def send_login_email(email: str):
    body = "You have successfully logged in."

    message = MIMEMultipart()
    message["From"] = "rakeshbarthipaka@gmail.com"
    message["To"] = email
    message["Subject"] = "Login Notification"

    message.attach(MIMEText(body, "html"))

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="rakeshbarthipaka@gmail.com",
        password="maihuiknlexftaon",
    )

@app.post("/login/")
async def login(login_request: LoginRequest, cursor=Depends(get_database_connection)):
    query = "SELECT * FROM employeesData WHERE email = %s"
    values = (login_request.email,)

    try:
        await cursor.execute(query, values)
        user = await cursor.fetchone()

        if user and bcrypt.checkpw(login_request.epassword.encode('utf-8'), user['epassword'].encode('utf-8')):
            access_token = create_access_token({"email": user['email']})

            # Send login notification email
            await send_login_email(user['email'])

            return {"message": "Login successfully completed", "access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
