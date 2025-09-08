# import jwt
# import os
import uvicorn
# from typing import Annotated
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
# from fastapi_simple_cache.backends.inmemory import InMemoryBackend
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from cachetools import LRUCache, TTLCache
from cachetools import TTLCache
from supabase import create_client, Client

# set up cache line
userCacheLine = TTLCache(maxsize=100, ttl=300)  # tigher bounds on on ttl

# Supabase initial
url: str = "https://yzpyartgzbqngicfpjgd.supabase.co/"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6cHlhcnRnemJxbmdpY2ZwamdkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxMTYzNzEsImV4cCI6MjA3MjY5MjM3MX0.Eg8lHbid-tZYi9uyknTMlngBKhLjg9_CzLxrUT9unVI"
supabase: Client = create_client(url, key)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sign-in")

# ====== start of application and cors policy modifications
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Class Models
class SignUp(BaseModel):
    First_name: str
    Last_name: str
    Phone: str
    DOB: str
    email: str
    password: str
    gender: str
    address: str
    Ten_lvl: str
    PB_lvl: str


class Sign_in(BaseModel):
    email: str | None = None
    password: str



@app.post("/sign-in")
async def sign_in(user: Sign_in):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        cur_session = response.session
        cur_user = response.user

        # stick user in cache
        '''
        cleanToken = cur_session.access_token.strip()
        userCacheLine[cleanToken] = cur_user
        '''

        return {
            "access_token": cur_session.access_token,
            "refresh_token": cur_session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": cur_user.id,
                "email": user.email,
                "message": cur_user.user_metadata["email_verified"]
            }
        }

    except Exception as e:
        return {
            "error": str(e),
            "code": "01AU"
        }


@app.post("/sign-up")
async def sign_up(user: SignUp):
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        # user ID that gets a response back, has to encase in try and catches
        user_id = response.user.id
        supabase.table("Users").insert({
            "id": user_id,
            "First_name": user.First_name,
            "Last_name": user.Last_name,
            "phone_number": user.Phone,
            "DOB": user.DOB,
            "Tennis_Level": user.Ten_lvl,
            "Pb_level": user.PB_lvl,
            "gender": user.gender,
            "address": user.address,
        }).execute()
        return {
            "id": user_id
        }
    except Exception as e:
        return {"error": str(e)}

# Main Function
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

