from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

SECRET_KEY = "your_secret_key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM, headers = {"alg": "HS256", "typ": "JWT"})
    print(f"createTOKEN = {encoded_token}")
    print(jwt.decode(encoded_token, SECRET_KEY, algorithms=[ALGORITHM]))
    return encoded_token
    

def decode_access_token(token: str):
    print(f"token = {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    

    



