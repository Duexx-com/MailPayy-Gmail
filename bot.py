import os
import random
import string
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন এখানে দিন
BOT_TOKEN = "8888654131:AAHSI87X19w9mQxG4EFCF7Q6PY2O9Z1z94Q"
# ==========================================

# র‍্যান্ডম নাম এবং পাসওয়ার্ড জেনারেট করার ফাংশন
def generate_random_credentials():
    first_names = ["Arif", "Sabbir", "Tanvir", "Nayeem", "Rafi", "Shakil", "Mehedi", "Tariq", "Jayed", "Rakib", "Sumon", "Farhan", "Ayan", "Zayan", "Irfan"]
    last_names = ["Ahmed", "Hasan", "Islam", "Hossain", "Rahman", "Khan", "Chowdhury", "Sarker", "Uddin", "Mahmud", "Siddiqui", "Talukder"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # ইউজারনেমের জন্য র‍্যান্ডম সংখ্যা যোগ করা
    random_digits = str(random.randint(1000, 99999))
    username = f"{first_name.lower()}{last_name.lower()}{random_digits}"
    
    # ১২ ডিজিটের শক্তিশালী র‍্যান্ডম পাসওয়ার্ড তৈরি
    chars = string.ascii_letters + string.digits + "@#$!"
    password = ''.join(random.choice(chars) for _ in range(12))
    
    return first_name, last_name, username, password

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "হ্যালো! আমি অটোমেটিক জিমেইল ক্রিয়েটর বট।\n\n"
        "নতুন একটি র‍্যান্ডম জিমেইল অ্যাকাউন্ট তৈরি করতে /create কমান্ডটি দিন।"
    )

async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name, last_name, username, password = generate_random_credentials()
    
    await update.message.reply_text(
        f"⏳ অটোমেটিক অ্যাকাউন্ট তৈরি শুরু হয়েছে...\n\n"
        f"নির্বাচিত নাম: {first_name} {last_name}\n"
        f"অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন..."
    )
    
    try:
        await create_gmail_account(first_name, last_name, username, password, context.bot, user_id)
    except Exception as e:
        await update.message.reply_text(f"❌ ত্রুটি হয়েছে: {str(e)}")

async def create_gmail_account(first_name, last_name, final_username, password, bot, chat_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://accounts.google.com/signup/v1/webid?continue=https://accounts.google.com/manageyouraccount&hl=en&flowName=GlifWebSignIn&flowEntry=SignUp")
        
        wait = WebDriverWait(driver, 20)
        
        # ১. ফার্স্ট নেম ইনপুট করা
        first_name_input = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
        first_name_input.clear()
        first_name_input.send_keys(first_name)
        
        # ২. লাস্ট নেম ইনপুট করা
        last_name_input = driver.find_element(By.ID, "lastName")
        last_name_input.clear()
        last_name_input.send_keys(last_name)
            
        # Next বাটন
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn.click()
        
        time.sleep(2)
        
        # ৩. ইউজারনেম ইনপুট করা
        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_input.clear()
        username_input.send_keys(final_username)
        
        next_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn2.click()
        
        time.sleep(2)
        
        # ৪. পাসওয়ার্ড ইনপুট করা
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.clear()
        password_input.send_keys(password)
        
        next_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn3.click()
        
        time.sleep(3)
        
        # ফোন নম্বর ভেরিফিকেশন স্কিপ করার চেষ্টা
        try:
            skip_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Skip')]")))
            skip_btn.click()
            time.sleep(2)
        except:
            pass
            
        await bot.send_message(
            chat_id=chat_id, 
            text=(
                f"✅ প্রসেস সম্পন্ন হয়েছে!\n\n"
                f"👤 নাম: {first_name} {last_name}\n"
                f"📧 জিমেইল: `{final_username}@gmail.com`\n"
                f"🔑 পাসওয়ার্ড: `{password}`"
            ),
            parse_mode="Markdown"
        )

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ অ্যাকাউন্ট তৈরি করতে ব্যর্থ হয়েছে:\n{str(e)}")
        
    finally:
        driver.quit()

def main():
    custom_request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    
    app = ApplicationBuilder().token(BOT_TOKEN).request(custom_request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_command))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
