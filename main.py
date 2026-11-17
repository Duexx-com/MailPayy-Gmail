from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string

app = FastAPI()

# সব ডোমেইন থেকে রিকোয়েস্ট অ্যালাউ করার জন্য CORS সেটআপ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# আপনার এবং আপনার ইউজারদের বৈধ API Key গুলোর তালিকা
VALID_API_KEYS = {
    "admin_master_key_12345": "Admin",
    "user_key_abc987": "User1",
    "user_key_xyz456": "User2"
}

class AccountRequest(BaseModel):
    name: str

@app.post("/api/create-account")
async def create_account(data: AccountRequest, authorization: str = Header(None)):
    # API Key চেক করা
    if not authorization or authorization not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="ভুল বা অবৈধ API Key!")
    
    # নাম থেকে জিমেইল ফরম্যাট তৈরি
    clean_name = data.name.replace(" ", "").lower()
    random_num = random.randint(1000, 9999)
    email = f"{clean_name}{random_num}@gmail.com"
    
    # ১০ ডিজিটের শক্তিশালী পাসওয়ার্ড তৈরি
    chars = string.ascii_letters + string.digits + "@#$"
    password = ''.join(random.choice(chars) for _ in range(10))
    
    return {
        "success": True,
        "email": email,
        "password": password,
        "message": "অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!"
    }

@app.get("/")
def home():
    return {"status": "Gmail Mini Bot API is running successfully!"}
