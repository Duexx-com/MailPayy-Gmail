import os
import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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

# গ্লোবাল ভেরিয়েবল (স্টেট ম্যানেজমেন্ট)
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি জিমেইল অ্যাকাউন্ট ক্রিয়েটর।\n\nএখন আপনার নাম দিন।")
    user_state[update.effective_user.id] = {'step': 'wait_name'}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_state and user_state[user_id]['step'] == 'wait_name':
        user_state[user_id]['name'] = update.message.text
        user_state[user_id]['step'] = 'wait_pass'
        await update.message.reply_text(f"নাম পাওয়া গেছে: {update.message.text}। এখন পাসওয়ার্ড দিন।")
        
    elif user_id in user_state and user_state[user_id]['step'] == 'wait_pass':
        user_state[user_id]['password'] = update.message.text
        name = user_state[user_id]['name']
        password = user_state[user_id]['password']
        
        await update.message.reply_text(f"{name} এর জন্য অ্যাকাউন্ট তৈরি করা হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন।")
        
        try:
            await create_gmail_account(name, password, context.bot, user_id)
        except Exception as e:
            await update.message.reply_text(f"ত্রুটি হয়েছে: {str(e)}")
        
        # স্টেট রিসেট করুন
        del user_state[user_id]

async def create_gmail_account(name, password, bot, chat_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # সার্ভারে চালানোর জন্য হেডলেস মোড আবশ্যক
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://accounts.google.com/signup/v1/webid?continue=https://accounts.google.com/manageyouraccount&hl=en&flowName=GlifWebSignIn&flowEntry=SignUp")
        
        wait = WebDriverWait(driver, 20)
        
        # ফার্স্ট নেম
        first_name_input = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
        first_name_input.clear()
        first_name_input.send_keys(name.split()[0])
        
        # লাস্ট নেম
        if len(name.split()) > 1:
            last_name_input = driver.find_element(By.ID, "lastName")
            last_name_input.send_keys(" ".join(name.split()[1:]))
            
        # Next বাটন
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn.click()
        
        time.sleep(2)
        
        # ইউজারনেম
        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        random_num = str(random.randint(100, 999))
        final_username = f"{name.replace(' ', '').lower()}{random_num}"
        username_input.clear()
        username_input.send_keys(final_username)
        
        next_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn2.click()
        
        time.sleep(2)
        
        # পাসওয়ার্ড
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.clear()
        password_input.send_keys(password)
        
        next_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn3.click()
        
        time.sleep(3)
        
        await bot.send_message(chat_id=chat_id, text=f"✅ প্রসেস সম্পন্ন হয়েছে!\n\nইউজারনেম: {final_username}@gmail.com\nপাসওয়ার্ড: {password}")

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
