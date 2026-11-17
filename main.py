from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
import string

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# আপনার এবং ইউজারদের বৈধ API Key গুলোর তালিকা
VALID_API_KEYS = {
    "admin_master_key_12345": "Admin",
    "user_key_abc987": "User1",
    "user_key_xyz456": "User2"
}

class AccountRequest(BaseModel):
    name: str

# রেন্ডার লিংক ওপেন করলেই ওয়েব ইন্টারফেস শো করবে
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gmail Creator Mini App</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f6f9;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background: #ffffff;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
            }
            h2 { text-align: center; color: #333; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #0088cc;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover { background: #006699; }
            #result {
                margin-top: 20px;
                padding: 10px;
                background: #eef9ff;
                border-left: 4px solid #0088cc;
                display: none;
                word-break: break-all;
            }
        </style>
    </head>
    <body>

    <div class="container">
        <h2>Gmail Generator</h2>
        
        <div class="form-group">
            <label for="apiKey">আপনার API Key:</label>
            <input type="text" id="apiKey" placeholder="এখানে API Key দিন">
        </div>
        
        <div class="form-group">
            <label for="name">নাম (যেমন: Arif Ahmed):</label>
            <input type="text" id="name" placeholder="নাম লিখুন">
        </div>
        
        <button onclick="createAccount()">অ্যাকাউন্ট তৈরি করুন</button>
        
        <div id="result"></div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        async function createAccount() {
            const apiKey = document.getElementById("apiKey").value.trim();
            const name = document.getElementById("name").value.trim();
            const resultDiv = document.getElementById("result");

            if (!apiKey || !name) {
                alert("দয়া করে API Key এবং নাম উভয়ই দিন!");
                return;
            }

            resultDiv.style.display = "block";
            resultDiv.innerHTML = "⏳ প্রসেস হচ্ছে, অপেক্ষা করুন...";

            try {
                const response = await fetch("/api/create-account", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": apiKey
                    },
                    body: JSON.stringify({ name: name })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    resultDiv.innerHTML = `
                        <b>✅ সফলভাবে তৈরি হয়েছে!</b><br>
                        📧 ইমেইল: <code>${data.email}</code><br>
                        🔑 পাসওয়ার্ড: <code>${data.password}</code>
                    `;
                } else {
                    resultDiv.innerHTML = `❌ ত্রুটি: ${data.detail || "অবৈধ API Key বা সার্ভার সমস্যা!"}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `❌ সার্ভারের সাথে সংযোগ স্থাপন করা যায়নি!`;
            }
        }
    </script>

    </body>
    </html>
    """
    return html_content

@app.post("/api/create-account")
async def create_account(data: AccountRequest, authorization: str = Header(None)):
    if not authorization or authorization not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="ভুল বা অবৈধ API Key!")
    
    clean_name = data.name.replace(" ", "").lower()
    random_num = random.randint(1000, 9999)
    email = f"{clean_name}{random_num}@gmail.com"
    
    chars = string.ascii_letters + string.digits + "@#$"
    password = ''.join(random.choice(chars) for _ in range(10))
    
    return {
        "success": True,
        "email": email,
        "password": password,
        "message": "অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!"
    }
