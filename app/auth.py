from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "LIBTRACK_SECRET"
security = HTTPBearer()

def create_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(hours=2)

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        # Strip quotes just in case they were accidentally pasted
        raw_token = credentials.credentials.strip('"\'')
        print(f"Attempting to decode token: {raw_token}")
        
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=["HS256"])
        print(f"Successfully decoded payload: {payload}")
        
        return payload.get("username")
    except Exception as e:
        print(f"JWT Verification Failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token Error: {str(e)}")