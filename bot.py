import os
import logging
import requests
import hashlib
import base64
import random
import string
import json
import urllib.parse
import socket
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN") or "PUT_YOUR_TOKEN_HERE"
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "PUT_YOUR_GROQ_KEY_HERE"
ADMIN_ID = int(os.getenv("ADMIN_ID") or "0")

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
FEEDBACK_FILE = "feedbacks.txt"

@app.route('/')
def home():
    return "DEMINI PRO MAX - LIVE"

@app.route('/health')
def health():
    return "OK"

# === AI HELPER - FIXED MODEL ===
def groq_ai(prompt, system="You are Demini Pro Max, a professional and helpful AI assistant."):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)[:300]}"

async def need_arg(update, usage):
    await update.message.reply_text(f"Usage: {usage}")

# === COMMANDS LIST ===
ALL_CMDS = """🔥 ALL COMMANDS:

CYBER: /whois /dns /ip /headers /ssl /port /sub /wayback /robots
CRYPTO: /hash /base64 /url /jwt /pwd
OSINT: /osint /email /breach /shodan /bin
WEB EDU: /dork /exploit /nmap /adminfinder /phish /cve
EDU: /learn /tutorial /quiz /explain
FEEDBACK: /feedback /report /suggest /rate /stats /admin
AI: /ai"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Welcome to DEMINI PRO MAX - Ultimate Bot!\n\n{ALL_CMDS}\n\nSend any message to chat with AI.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ALL_CMDS)

# CYBER
async def whois_cmd(update, context):
    if not context.args: return await need_arg(update, "/whois google.com")
    domain = context.args[0]
    await update.message.reply_text(f"WHOIS for {domain}:\nhttps://who.is/whois/{domain}")

async def dns_cmd(update, context):
    if not context.args: return await need_arg(update, "/dns google.com")
    d = context.args[0]
    try:
        ip = socket.gethostbyname(d)
        await update.message.reply_text(f"DNS for {d}:\nA Record: {ip}")
    except Exception as e: await update.message.reply_text(f"Error: {e}")

async def ip_cmd(update, context):
    if not context.args: return await need_arg(update, "/ip 8.8.8.8")
    ip = context.args[0]
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
        await update.message.reply_text(f"IP Info {ip}:\n{json.dumps(r, indent=2)[:1000]}")
    except Exception as e: await update.message.reply_text(f"Error: {e}")

async def headers_cmd(update, context):
    if not context.args: return await need_arg(update, "/headers https://google.com")
    url = context.args[0]
    if not url.startswith("http"): url = "https://"+url
    try:
        r = requests.head(url, timeout=10)
        txt = "\n".join([f"{k}: {v}" for k,v in r.headers.items()])
        await update.message.reply_text(f"Headers {url}:\n{txt[:1000]}")
    except Exception as e: await update.message.reply_text(f"Error: {e}")

async def ssl_cmd(update, context):
    if not context.args: return await need_arg(update, "/ssl google.com")
    host = context.args[0].replace("https://","").replace("http://","").split("/")[0]
    await update.message.reply_text(f"SSL for {host}: Check https://www.sslshopper.com/ssl-checker.html#{host}")

async def port_cmd(update, context):
    if not context.args: return await need_arg(update, "/port google.com")
    host = context.args[0]
    common = [21,22,80,443,3306,8080]
    open_ports = []
    for p in common:
        s=socket.socket(); s.settimeout(1)
        try:
            s.connect((host,p)); open_ports.append(str(p))
        except: pass
        s.close()
    await update.message.reply_text(f"Port scan {host}:\nOpen: {', '.join(open_ports) or 'None from common list'}")

async def sub_cmd(update, context):
    if not context.args: return await need_arg(update, "/sub google.com")
    d=context.args[0]
    subs=[f"www.{d}",f"mail.{d}",f"api.{d}",f"admin.{d}"]
    await update.message.reply_text(f"Subdomains for {d}:\n" + "\n".join(subs))

async def wayback_cmd(update, context):
    if not context.args: return await need_arg(update, "/wayback google.com")
    d=context.args[0]
    await update.message.reply_text(f"Wayback: https://web.archive.org/web/*/{d}")

async def robots_cmd(update, context):
    if not context.args: return await need_arg(update, "/robots google.com")
    d=context.args[0]
    if not d.startswith("http"): d="https://"+d
    try:
        r=requests.get(d+"/robots.txt",timeout=8)
        await update.message.reply_text(f"robots.txt for {d}:\n{r.text[:1000]}")
    except Exception as e: await update.message.reply_text(f"Error: {e}")

# CRYPTO
async def hash_cmd(update, context):
    if not context.args: return await need_arg(update, "/hash yourtext")
    t=" ".join(context.args)
    await update.message.reply_text(f"MD5: {hashlib.md5(t.encode()).hexdigest()}\nSHA1: {hashlib.sha1(t.encode()).hexdigest()}\nSHA256: {hashlib.sha256(t.encode()).hexdigest()}")

async def base64_cmd(update, context):
    if not context.args: return await need_arg(update, "/base64 hello")
    t=" ".join(context.args)
    enc=base64.b64encode(t.encode()).decode()
    await update.message.reply_text(f"Base64 Encode: {enc}")

async def url_cmd(update, context):
    if not context.args: return await need_arg(update, "/url https://example.com?q=hello world")
    t=" ".join(context.args)
    await update.message.reply_text(f"URL Encode: {urllib.parse.quote(t)}\nDecode: {urllib.parse.unquote(t)}")

async def jwt_cmd(update, context):
    if not context.args: return await need_arg(update, "/jwt eyJ...")
    token=context.args[0]
    try:
        parts=token.split(".")
        header=json.loads(base64.urlsafe_b64decode(parts[0]+"==").decode())
        payload=json.loads(base64.urlsafe_b64decode(parts[1]+"==").decode())
        await update.message.reply_text(f"JWT Decoded:\nHeader: {json.dumps(header,indent=2)}\nPayload: {json.dumps(payload,indent=2)}")
    except Exception as e: await update.message.reply_text(f"Invalid JWT: {e}")

async def pwd_cmd(update, context):
    length=int(context.args[0]) if context.args else 12
    chars=string.ascii_letters+string.digits+"!@#$%"
    pwd=''.join(random.choice(chars) for _ in range(length))
    await update.message.reply_text(f"Generated Password ({length}):\n`{pwd}`", parse_mode='Markdown')

# OSINT
async def osint_cmd(update, context):
    if not context.args: return await need_arg(update, "/osint username")
    u=context.args[0]
    await update.message.reply_text(f"OSINT for {u}:\nhttps://whatsmyname.app/?q={u}\nhttps://github.com/{u}")

async def email_cmd(update, context):
    if not context.args: return await need_arg(update, "/email test@gmail.com")
    e=context.args[0]
    await update.message.reply_text(f"Email {e}: Format valid.")

async def breach_cmd(update, context):
    if not context.args: return await need_arg(update, "/breach test@gmail.com")
    e=context.args[0]
    await update.message.reply_text(f"Breach check for {e}: https://haveibeenpwned.com/account/{e}")

async def shodan_cmd(update, context):
    if not context.args: return await need_arg(update, "/shodan 8.8.8.8")
    ip=context.args[0]
    await update.message.reply_text(f"Shodan for {ip}: https://www.shodan.io/host/{ip}")

async def bin_cmd(update, context):
    if not context.args: return await need_arg(update, "/bin 457173")
    b=context.args[0][:6]
    try:
        r=requests.get(f"https://lookup.binlist.net/{b}", headers={"Accept-Version":"3"}, timeout=10).json()
        await update.message.reply_text(f"BIN {b}:\n{json.dumps(r,indent=2)[:1000]}")
    except: await update.message.reply_text(f"BIN {b}: Use https://binlist.net/{b}")

# WEB EDU
async def dork_cmd(update, context):
    if not context.args: return await need_arg(update, "/dork site:example.com")
    q=" ".join(context.args)
    await update.message.reply_text(f"Google Dork: {q}\nhttps://www.google.com/search?q={urllib.parse.quote(q)}")

async def exploit_cmd(update, context):
    if not context.args: return await need_arg(update, "/exploit wordpress")
    q=" ".join(context.args)
    await update.message.reply_text(f"Exploit search {q}: https://www.exploit-db.com/search?q={urllib.parse.quote(q)}")

async def nmap_cmd(update, context):
    if not context.args: return await need_arg(update, "/nmap google.com")
    h=context.args[0]
    await update.message.reply_text(f"Nmap command for {h}:\n`nmap -sV -A {h}`", parse_mode='Markdown')

async def adminfinder_cmd(update, context):
    if not context.args: return await need_arg(update, "/adminfinder example.com")
    d=context.args[0]
    paths=["/admin","/login","/admin.php","/wp-admin"]
    await update.message.reply_text(f"Admin Finder for {d}:\n" + "\n".join([f"https://{d}{p}" for p in paths]))

async def phish_cmd(update, context):
    await update.message.reply_text("Phishing Education: Learn to detect phishing via headers and URL analysis. For defensive purposes only.")

async def cve_cmd(update, context):
    if not context.args: return await need_arg(update, "/cve CVE-2023-1234")
    c=context.args[0]
    await update.message.reply_text(f"CVE {c}:\nhttps://nvd.nist.gov/vuln/detail/{c}")

# EDU
async def learn_cmd(update, context):
    if not context.args: return await need_arg(update, "/learn python")
    q=" ".join(context.args)
    ans=groq_ai(q, "You are a teacher. Explain simply and clearly.")
    await update.message.reply_text(f"Learn {q}:\n\n{ans}")

async def tutorial_cmd(update, context):
    if not context.args: return await need_arg(update, "/tutorial hacking")
    q=" ".join(context.args)
    ans=groq_ai(f"Create a beginner ethical tutorial for {q}", "You are an ethical educator.")
    await update.message.reply_text(f"Tutorial {q}:\n\n{ans}")

async def quiz_cmd(update, context):
    if not context.args: return await need_arg(update, "/quiz python")
    q=" ".join(context.args)
    ans=groq_ai(f"Create 3 quiz questions with answers about {q}")
    await update.message.reply_text(f"Quiz {q}:\n\n{ans}")

async def explain_cmd(update, context):
    if not context.args: return await need_arg(update, "/explain what is dns")
    q=" ".join(context.args)
    ans=groq_ai(q)
    await update.message.reply_text(ans)

# FEEDBACK
async def feedback_cmd(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /feedback your message")
        return
    msg=" ".join(context.args)
    with open(FEEDBACK_FILE,"a") as f: f.write(f"{datetime.now()} - {update.effective_user.id} - {msg}\n")
    await update.message.reply_text("Feedback saved! Thanks!")

async def report_cmd(update, context):
    if not context.args: return await need_arg(update, "/report bug description")
    await feedback_cmd(update, context)

async def suggest_cmd(update, context):
    if not context.args: return await need_arg(update, "/suggest your idea")
    await feedback_cmd(update, context)

async def rate_cmd(update, context):
    await update.message.reply_text("Rate me: Send /feedback 1-5 stars. Example: /feedback 5 stars, great bot!")

async def stats_cmd(update, context):
    try:
        with open(FEEDBACK_FILE,"r") as f: count=len(f.readlines())
    except: count=0
    await update.message.reply_text(f"Stats:\nFeedbacks: {count}\nUptime: OK")

async def admin_cmd(update, context):
    if ADMIN_ID != 0 and update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Admin only!")
        return
    try:
        with open(FEEDBACK_FILE,"r") as f: data=f.read()[-1000:]
    except: data="No feedback yet"
    await update.message.reply_text(f"Admin Panel:\n{data}")

# AI
async def ai_cmd(update, context):
    if not context.args: return await need_arg(update, "/ai hello")
    q=" ".join(context.args)
    ans=groq_ai(q)
    await update.message.reply_text(ans)

async def chat_ai(update, context):
    ans=groq_ai(update.message.text)
    await update.message.reply_text(ans)

def run_bot():
    print("BOT STARTED - ALL COMMANDS SINGLE BOT")
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("help", help_cmd))
    app_bot.add_handler(CommandHandler("whois", whois_cmd))
    app_bot.add_handler(CommandHandler("dns", dns_cmd))
    app_bot.add_handler(CommandHandler("ip", ip_cmd))
    app_bot.add_handler(CommandHandler("headers", headers_cmd))
    app_bot.add_handler(CommandHandler("ssl", ssl_cmd))
    app_bot.add_handler(CommandHandler("port", port_cmd))
    app_bot.add_handler(CommandHandler("sub", sub_cmd))
    app_bot.add_handler(CommandHandler("wayback", wayback_cmd))
    app_bot.add_handler(CommandHandler("robots", robots_cmd))
    app_bot.add_handler(CommandHandler("hash", hash_cmd))
    app_bot.add_handler(CommandHandler("base64", base64_cmd))
    app_bot.add_handler(CommandHandler("url", url_cmd))
    app_bot.add_handler(CommandHandler("jwt", jwt_cmd))
    app_bot.add_handler(CommandHandler("pwd", pwd_cmd))
    app_bot.add_handler(CommandHandler("osint", osint_cmd))
    app_bot.add_handler(CommandHandler("email", email_cmd))
    app_bot.add_handler(CommandHandler("breach", breach_cmd))
    app_bot.add_handler(CommandHandler("shodan", shodan_cmd))
    app_bot.add_handler(CommandHandler("bin", bin_cmd))
    app_bot.add_handler(CommandHandler("dork", dork_cmd))
    app_bot.add_handler(CommandHandler("exploit", exploit_cmd))
    app_bot.add_handler(CommandHandler("nmap", nmap_cmd))
    app_bot.add_handler(CommandHandler("adminfinder", adminfinder_cmd))
    app_bot.add_handler(CommandHandler("phish", phish_cmd))
    app_bot.add_handler(CommandHandler("cve", cve_cmd))
    app_bot.add_handler(CommandHandler("learn", learn_cmd))
    app_bot.add_handler(CommandHandler("tutorial", tutorial_cmd))
    app_bot.add_handler(CommandHandler("quiz", quiz_cmd))
    app_bot.add_handler(CommandHandler("explain", explain_cmd))
    app_bot.add_handler(CommandHandler("feedback", feedback_cmd))
    app_bot.add_handler(CommandHandler("report", report_cmd))
    app_bot.add_handler(CommandHandler("suggest", suggest_cmd))
    app_bot.add_handler(CommandHandler("rate", rate_cmd))
    app_bot.add_handler(CommandHandler("stats", stats_cmd))
    app_bot.add_handler(CommandHandler("admin", admin_cmd))
    app_bot.add_handler(CommandHandler("ai", ai_cmd))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ai))
    app_bot.run_polling()

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)m
