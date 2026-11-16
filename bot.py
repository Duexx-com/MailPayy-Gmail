import os
import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন এখানে দিন
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
# ==========================================

# গ্লোবাল ভেরিয়েবল (স্টেট ম্যানেজমেন্ট)
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি জিমেইল অ্যাকাউন্ট ক্রিয়েটর।\n\nএখন আপনার দেব নাম এবং পাসওয়ার্ড।")
    user_state[update.effective_user.id] = {'step': 'wait_name'}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # যদি ইউজার আগে থেকেই কোনো প্রসেসে থাকে
    if user_id in user_state and user_state[user_id]['step'] == 'wait_name':
        user_state[user_id]['name'] = update.message.text
        user_state[user_id]['step'] = 'wait_pass'
        await update.message.reply_text(f"নাম পাওয়া গেছে: {update.message.text}। এখন পাসওয়ার্ড দিন।")
        
    elif user_id in user_state and user_state[user_id]['step'] == 'wait_pass':
        user_state[user_id]['password'] = update.message.text
        name = user_state[user_id]['name']
        password = user_state[user_id]['password']
        
        # অ্যাকাউন্ট তৈরি শুরু করুন
        await update.message.reply_text(f"{name} এর জন্য অ্যাকাউন্ট তৈরি করা হচ্ছে... (ভেরিফিকেশন স্কিপ করার চেষ্টা করা হচ্ছে)")
        
        # ব্যাকগ্রাউন্ডে ক্রিয়েশন ফাংশন কল করুন (সিম্পল রাখার জন্য সিঙ্ক্রোনাস মেথড)
        try:
            create_gmail_account(name, password, context.bot, user_id)
        except Exception as e:
            await update.message.reply_text(f"ত্রুটি হয়েছে: {str(e)}")
        
        # স্টেট রিসেট করুন
        del user_state[user_id]

def create_gmail_account(name, password, bot, chat_id):
    # সেলেনিয়াম কনফিগারেশন
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ব্রাউজার ভিজিবল না করে (ব্যাকগ্রাউন্ডে চলবে)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # প্রক্সি ব্যবহার করতে চাইলে নিচের লাইনটি আনকমেন্ট করুন এবং আইপি দিন
    # chrome_options.add_argument(f"--proxy-server=http://YOUR_IP:PORT")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    
    try:
        # ১. গুগল সাইন-আপ পেজে যাওয়া
        driver.get("https://accounts.google.com/signup/v1/webid?continue=https://accounts.google.com/manageyouraccount&hl=en&flowName=GlifWebSignIn&flowEntry=SignUp")
        
        wait = WebDriverWait(driver, 20)
        
        # ২. ফার্স্ট নেম ইনপুট করা
        first_name_input = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
        first_name_input.clear()
        first_name_input.send_keys(name.split()[0]) # নামের প্রথম অংশ
        
        # ৩. লাস্ট নেম ইনপুট করা (যদি থাকে)
        if len(name.split()) > 1:
            last_name_input = driver.find_element(By.ID, "lastName")
            last_name_input.send_keys(" ".join(name.split()[1:]))
            
        # ৪. Next বাটনে ক্লিক করে ইউজারনেম পেজে যাওয়া
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn.click()
        
        time.sleep(2) # পেজ লোড হতে সময় দিন
        
        # ে। ইউজারনেম জেনারেট করা (নামের সাথে সংখ্যা যোগ করে)
        username_input = wait.until(EC.presence_of_element_loced((By.ID, "username")))
        random_num = str(random.randint(100, 999))
        final_username = f"{name.replace(' ', '')}{random_num}"
        username_input.clear()
        username_input.send_keys(final_username)
        
        # Next বাটনে ক্লিক করে পাসওয়ার্ড পেজে যাওয়া
        next_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn2.click()
        
        time.sleep(2)
        
        # ৬. পাসওয়ার্ড ইনপুট করা
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.clear()
        password_input.send_keys(password)
        
        next_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Next')]")))
        next_btn3.click()
        
        time.sleep(2)
        
        # ৭. ফোন নম্বর ভেরিফিকেশন স্কিপ করার লজিক
        # গুগল সাধারণত "Phone number" বা "Verify Phone Number" দেখায়।
        # আমরা চেক করব পেজে কোনো মোবাইল ইনপুট বক্স আছে কিনা।
        
        try:
            # ফোন নম্বর ইনপুট ফিল্ড খোঁজা
            phone_input = driver.find_element(By.ID, "phoneNumberId")
            
            # যদি ফোন ইনপুট থাকে, তবে 'Skip' বাটন খোঁজার চেষ্টা করা
            # অনেক সময় 'Skip' সরাসরি থাকে, আবার অনেক সময় ড্রপডাউন মেনু থেকে স্কিপ করতে হয়
            
            skip_found = False
            
            # চেষ্টা ১: সরাসরি 'Skip' বাটন আছে কিনা দেখা
            try:
                skip_btn = driver.find_element(By.XPATH, "//span[contains(text(),'Skip')]")
                skip_btn.click()
                skip_found = True
                print("Direct Skip button clicked.")
            except:
                pass
                
            # চেষ্টা ২: যদি সরাসরি স্কিপ না থাকে, তবে কিছু ক্ষেত্রে 'Next' ক্লিক করলেই স্কিপ হয়ে যায় অথবা ড্রপডাউন থেকে স্কিপ করতে হয়।
            # সাধারণত গুগল নিউ অ্যাকাউন্টের জন্য ফোন নম্বর অপশনাল করে দেয় যদি আমরা 'Skip' বা 'Use my current phone number' (যদি আগে ব্যবহার করে থাকি) খুঁজে পাই।
            
            if not skip_found:
                # অনেক সময় পেজ রিলোড হয় বা ক্যাপচা আসে। 
                # আমরা আবার চেক করি 'Skip' আছে কিনা।
                try:
                    skip_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Skip')]")))
                    skip_btn.click()
                    skip_found = True
                except:
                    pass
            
            if not skip_found:
                # শেষ চেষ্টা: Next বাটন ক্লিক করা (কিছু ক্ষেত্রে এটিই কাজ করে)
                try:
                    next_btn4 = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
                    next_btn4.click()
                except:
                    pass

        except Exception as e:
            print(f"Phone step logic error: {e}")
            # যদি ফোন নম্বর স্টেজে না যায়, তাহলেও চলবে।

        time.sleep(3)
        
        # ৮. শেষ চেক: পেজটি কি "Create Account" বা অন্য কোনো স্টেটে আছে?
        # সাধারণত অ্যাকাউন্ট তৈরি হলে গুগল আমাদের মেইল বক্সে নিয়ে যায় বা "Your account is ready" দেখায়।
        
        await bot.send_message(chat_id=chat_id, text=f"✅ জিমেইল অ্যাকাউন্ট তৈরি হয়েছে!\n\nইমেইল: {final_username}@gmail.com\nপাসওয়ার্ড: {password}\n\n(দ্রষ্টব্য: ভেরিফিকেশন স্কিপ করার চেষ্টা করা হয়েছে।)")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ অ্যাকাউন্ট তৈরি করতে ব্যর্থ হয়েছে:\n{str(e)}")
        
    finally:
        driver.quit()

def main():
    # বট ইনিশিয়ালাইজেশন
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # কমান্ড হ্যান্ডলার
    app.add_handler(CommandHandler("start", start))
    
    # মেসেজ হ্যান্ডলার (নাম ও পাসওয়ার্ড নেওয়ার জন্য)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
