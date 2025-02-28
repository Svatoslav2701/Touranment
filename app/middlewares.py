from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from .auth import decode_access_token


SECRET_KEY = "your_secret_key"  
ALGORITHM = "HS256"  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
         raise HTTPException(status_code=401, detail="Токен не передано або некоректний формат")
    print(auth_header)
    
    token = auth_header.split(" ")[1]  

    decoded_token = decode_access_token(token)
    if not decoded_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    request.state.user = decoded_token.get("sub")
    return decoded_token

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/login", "/docs", "/openapi.json"]:
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Токен не передано")
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Невалідний токен")

        return await call_next(request)
    


