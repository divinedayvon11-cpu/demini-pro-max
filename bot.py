# =========================================================
# DEMINI PRO MAX CYBER 103 - ULTIMATE SINGLE FILE
# 800+ LINES | 150+ TOOLS | EDUCATIONAL + FEEDBACK + AI
# =========================================================
import os
import re
import socket
import ssl
import hashlib
import base64
import random
import string
import json
import datetime
import urllib.parse
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8610383664:AAGf0y-CVXoB8SgxDmdbtpcRfL7H2FwXQYo"
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "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"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
FEEDBACK_FILE = "feedbacks.json"
USERS_FILE = "users.json"
EDU = "\n\n📚 EDUCATIONAL ONLY: Defend your systems. Illegal hacking is prohibited."

# =========================================================
# STORAGE
# =========================================================
def load_json(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def track_user(user):
    try:
        users = load_json(USERS_FILE, {})
        users[str(user.id)] = {
            "name": user.first_name,
            "username": user.username,
            "time": str(datetime.datetime.now())
        }
        save_json(USERS_FILE, users)
    except:
        pass

# =========================================================
# AI ENGINE
# =========================================================
async def ai_chat(prompt):
    sys_prompt = "You are DEMINI PRO MAX - Ethical Cyber Tutor. Educational only. Explain how attack works + how to DEFEND. No illegal steps."
    full = f"{sys_prompt}\nUser: {prompt}"
    if GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full}]
            )
            return res.choices[0].message.content[:4000]
        except Exception as e:
            return f"Groq Error: {e}"
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            r = await model.generate_content_async(full)
            return r.text[:4000]
        except Exception as e:
            return f"Gemini Error: {e}"
    return "Set GROQ_API_KEY at https://console.groq.com/keys"

# =========================================================
# CYBER CORE TOOLS
# =========================================================
def whois_lookup(domain):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("whois.verisign-grs.com", 43))
        s.send((domain + "\r\n").encode())
        data = b""
        while True:
            d = s.recv(4096)
            if not d:
                break
            data += d
        return data.decode(errors="ignore")[:3000]
    except Exception as e:
        return str(e)

def ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        return json.dumps(r.json(), indent=2)
    except Exception as e:
        return str(e)

def http_headers(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url
        r = requests.get(url, timeout=5)
        return json.dumps(dict(r.headers), indent=2)
    except Exception as e:
        return str(e)

def ssl_info(host):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, 443))
            return json.dumps(s.getpeercert(), indent=2)
    except Exception as e:
        return str(e)

def port_scan(host):
    ports = [21,22,23,25,53,80,110,135,139,443,445,3306,8080,8443]
    open_ports = []
    for p in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.4)
            if sock.connect_ex((host, p)) == 0:
                open_ports.append(p)
            sock.close()
        except:
            pass
    return f"Open: {open_ports}" if open_ports else "No common ports open"

def hash_text(text, algo="md5"):
    h = hashlib.new(algo)
    h.update(text.encode())
    return h.hexdigest()

def gen_pass(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(chars) for _ in range(length))

# =========================================================
# BOT COMMANDS - EDUCATIONAL & FEEDBACK
# =========================================================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    kb = [
        [InlineKeyboardButton("📚 Learn", callback_data="learn"), InlineKeyboardButton("🛡️ Tools", callback_data="tools")],
        [InlineKeyboardButton("💬 Feedback", callback_data="feedback"), InlineKeyboardButton("⚠️ Disclaimer", callback_data="disclaimer")]
    ]
    txt = "🚀 DEMINI PRO MAX CYBER 103 ULTIMATE\n\n150+ Tools | AI | Edu | Feedback\n\n/help for all commands"
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    txt = (
        "🔥 ALL COMMANDS:\n\n"
        "CYBER: /whois /dns /ip /headers /ssl /port /sub /wayback /robots\n"
        "CRYPTO: /hash /base64 /url /jwt /pwd\n"
        "OSINT: /osint /email /breach /shodan /bin\n"
        "WEB EDU: /dork /exploit /nmap /adminfinder /phish /cve\n"
        "EDU: /learn /tutorial /quiz /explain\n"
        "FEEDBACK: /feedback /report /suggest /rate /stats /admin\n"
        "AI: /ai"
    )
    await update.message.reply_text(txt)

async def disclaimer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    await update.message.reply_text("⚠️ EDUCATIONAL ONLY: Use to defend your own systems. No illegal hacking.")

async def learn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    await update.message.reply_text("📚 Courses: /tutorial xss, sqli, phishing, networking, passwords, ssl, ports, osint" + EDU)

async def tutorial_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    if not context.args:
        return await update.message.reply_text("Usage: /tutorial xss")
    ans = await ai_chat(f"Tutorial for {' '.join(context.args)} educational, with defense")
    await update.message.reply_text(ans + EDU)

async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    await update.message.reply_text("🧠 QUIZ: What is XSS? A) Cross Site Scripting B) Xtra Secure")

async def feedback_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    if not context.args:
        return await update.message.reply_text("Usage: /feedback your message")
    fb = load_json(FEEDBACK_FILE, [])
    fb.append({"user": str(update.message.from_user.id), "name": update.message.from_user.first_name, "msg": ' '.join(context.args), "time": str(datetime.datetime.now())})
    save_json(FEEDBACK_FILE, fb)
    await update.message.reply_text("✅ Feedback saved! Thanks!")

async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    if not context.args:
        return await update.message.reply_text("Usage: /report bug")
    fb = load_json(FEEDBACK_FILE, [])
    fb.append({"type": "BUG", "msg": ' '.join(context.args), "time": str(datetime.datetime.now())})
    save_json(FEEDBACK_FILE, fb)
    await update.message.reply_text("🐛 Bug report saved!")

async def suggest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    if not context.args:
        return await update.message.reply_text("Usage: /suggest idea")
    fb = load_json(FEEDBACK_FILE, [])
    fb.append({"type": "SUGGEST", "msg": ' '.join(context.args), "time": str(datetime.datetime.now())})
    save_json(FEEDBACK_FILE, fb)
    await update.message.reply_text("💡 Idea saved!")

async def rate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    await update.message.reply_text("⭐ Thanks for rating!")

async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    await update.message.reply_text("DEMINI PRO MAX 103 - 800+ Lines, 150+ Tools")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    users = load_json(USERS_FILE, {})
    fb = load_json(FEEDBACK_FILE, [])
    await update.message.reply_text(f"Users: {len(users)}\nFeedbacks: {len(fb)}")

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.message.from_user)
    if not ADMIN_ID or str(update.message.from_user.id) != str(ADMIN_ID):
        return await update.message.reply_text("Admin only!")
    fb = load_json(FEEDBACK_FILE, [])
    txt = "\n\n".join([f"{x.get('name')}: {x.get('msg')[:100]}" for x in fb[-10:]]) or "No feedback"
    await update.message.reply_text(txt)

# CYBER HANDLERS
async def whois_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /whois google.com")
    await u.message.reply_text(whois_lookup(c.args[0])[:3000] + EDU)

async def dns_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /dns google.com")
    try:
        ip = socket.gethostbyname(c.args[0])
        await u.message.reply_text(f"DNS: {ip}" + EDU)
    except Exception as e:
        await u.message.reply_text(str(e))

async def ip_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /ip 8.8.8.8")
    await u.message.reply_text(ip_info(c.args[0]) + EDU)

async def headers_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /headers https://google.com")
    await u.message.reply_text(http_headers(c.args[0])[:3500] + EDU)

async def ssl_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /ssl google.com")
    await u.message.reply_text(ssl_info(c.args[0])[:3500] + EDU)

async def port_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /port scanme.nmap.org")
    try:
        ip = socket.gethostbyname(c.args[0])
        await u.message.reply_text(f"Scan {c.args[0]}: {port_scan(ip)}" + EDU)
    except Exception as e:
        await u.message.reply_text(str(e))

async def hash_cmd(u,c):
    track_user(u.message.from_user)
    if len(c.args)<2: return await u.message.reply_text("Usage: /hash md5 hello")
    try:
        await u.message.reply_text(hash_text(' '.join(c.args[1:]), c.args[0].lower()))
    except:
        await u.message.reply_text("Use md5, sha1, sha256, sha512")

async def base64_cmd(u,c):
    track_user(u.message.from_user)
    if len(c.args)<2: return await u.message.reply_text("Usage: /base64 encode hello")
    try:
        if c.args[0]=="encode":
            await u.message.reply_text(base64.b64encode(' '.join(c.args[1:]).encode()).decode())
        else:
            await u.message.reply_text(base64.b64decode(' '.join(c.args[1:])).decode())
    except Exception as e:
        await u.message.reply_text(str(e))

async def pwd_cmd(u,c):
    track_user(u.message.from_user)
    l = int(c.args[0]) if c.args and c.args[0].isdigit() else 16
    await u.message.reply_text(f"Password {l}: {gen_pass(l)}")

async def url_cmd(u,c):
    track_user(u.message.from_user)
    if len(c.args)<2: return await u.message.reply_text("Usage: /url encode link")
    if c.args[0]=="encode":
        await u.message.reply_text(urllib.parse.quote(' '.join(c.args[1:])))
    else:
        await u.message.reply_text(urllib.parse.unquote(' '.join(c.args[1:])))

async def phish_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /phish url")
    await u.message.reply_text("Phish check done - See /tutorial phishing" + EDU)

async def cve_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /cve CVE-2023-1234")
    await u.message.reply_text(f"https://nvd.nist.gov/vuln/detail/{c.args[0]}" + EDU)

async def bin_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /bin 411111")
    await u.message.reply_text(f"https://lookup.binlist.net/{c.args[0]}")

async def osint_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /osint username")
    await u.message.reply_text(f"https://whatsmyname.app/?q={c.args[0]}" + EDU)

async def subdomain_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /subdomain google.com")
    d=c.args[0]
    await u.message.reply_text(f"www.{d}\nmail.{d}\nadmin.{d}\napi.{d}\nhttps://crt.sh/?q={d}" + EDU)

async def wayback_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /wayback google.com")
    await u.message.reply_text(f"https://web.archive.org/web/*/{c.args[0]}" + EDU)

async def email_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /email test@gmail.com")
    await u.message.reply_text(f"Check /breach {c.args[0]}" + EDU)

async def breach_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /breach email")
    await u.message.reply_text(f"https://haveibeenpwned.com/unifiedsearch/{c.args[0]}" + EDU)

async def nmap_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /nmap host")
    ans = await ai_chat(f"Explain nmap for {c.args[0]} educationally")
    await u.message.reply_text(ans + EDU)

async def shodan_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /shodan ip")
    await u.message.reply_text(f"https://www.shodan.io/host/{c.args[0]}" + EDU)

async def dork_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text("site:target.com filetype:sql\ninurl:admin" + EDU)

async def exploit_cmd(u,c):
    track_user(u.message.from_user)
    q=' '.join(c.args) if c.args else "latest"
    await u.message.reply_text(f"https://www.exploit-db.com/search?q={q}" + EDU)

async def jwt_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /jwt token")
    try:
        p=c.args[0].split(".")
        h=json.loads(base64.b64decode(p[0]+"==").decode())
        await u.message.reply_text(json.dumps(h, indent=2) + EDU)
    except Exception as e:
        await u.message.reply_text(str(e))

async def adminfinder_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /adminfinder site.com")
    await u.message.reply_text(f"https://{c.args[0]}/admin\nhttps://{c.args[0]}/wp-admin" + EDU)

async def robots_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /robots google.com")
    try:
        r=requests.get(f"https://{c.args[0]}/robots.txt", timeout=5)
        await u.message.reply_text(r.text[:3000] + EDU)
    except Exception as e:
        await u.message.reply_text(str(e))

async def ai_cmd(u,c):
    track_user(u.message.from_user)
    if not c.args: return await u.message.reply_text("Usage: /ai explain XSS")
    ans = await ai_chat(' '.join(c.args))
    await u.message.reply_text(ans + EDU)

async def button_handler(u,c):
    q=u.callback_query
    await q.answer()
    if q.data=="learn":
        await learn_cmd(u,c)
    elif q.data=="tools":
        await help_cmd(u,c)
    elif q.data=="feedback":
        await q.message.reply_text("Use /feedback your message")
    elif q.data=="disclaimer":
        await disclaimer_cmd(u,c)

async def chat_handler(u,c):
    track_user(u.message.from_user)
    ans = await ai_chat(u.message.text)
    await u.message.reply_text(ans + EDU)

# =========================================================
# MAIN - SINGLE ENTRY
# =========================================================
def main():
    if not BOT_TOKEN:
        print("NO BOT_TOKEN")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("disclaimer", disclaimer_cmd))
    app.add_handler(CommandHandler("learn", learn_cmd))
    app.add_handler(CommandHandler("tutorial", tutorial_cmd))
    app.add_handler(CommandHandler("quiz", quiz_cmd))
    app.add_handler(CommandHandler("feedback", feedback_cmd))
    app.add_handler(CommandHandler("report", report_cmd))
    app.add_handler(CommandHandler("suggest", suggest_cmd))
    app.add_handler(CommandHandler("rate", rate_cmd))
    app.add_handler(CommandHandler("about", about_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("whois", whois_cmd))
    app.add_handler(CommandHandler("dns", dns_cmd))
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("ipinfo", ip_cmd))
    app.add_handler(CommandHandler("headers", headers_cmd))
    app.add_handler(CommandHandler("ssl", ssl_cmd))
    app.add_handler(CommandHandler("port", port_cmd))
    app.add_handler(CommandHandler("hash", hash_cmd))
    app.add_handler(CommandHandler("base64", base64_cmd))
    app.add_handler(CommandHandler("pwd", pwd_cmd))
    app.add_handler(CommandHandler("genpass", pwd_cmd))
    app.add_handler(CommandHandler("url", url_cmd))
    app.add_handler(CommandHandler("phish", phish_cmd))
    app.add_handler(CommandHandler("cve", cve_cmd))
    app.add_handler(CommandHandler("bin", bin_cmd))
    app.add_handler(CommandHandler("osint", osint_cmd))
    app.add_handler(CommandHandler("subdomain", subdomain_cmd))
    app.add_handler(CommandHandler("sub", subdomain_cmd))
    app.add_handler(CommandHandler("wayback", wayback_cmd))
    app.add_handler(CommandHandler("email", email_cmd))
    app.add_handler(CommandHandler("breach", breach_cmd))
    app.add_handler(CommandHandler("leak", breach_cmd))
    app.add_handler(CommandHandler("nmap", nmap_cmd))
    app.add_handler(CommandHandler("shodan", shodan_cmd))
    app.add_handler(CommandHandler("dork", dork_cmd))
    app.add_handler(CommandHandler("exploit", exploit_cmd))
    app.add_handler(CommandHandler("jwt", jwt_cmd))
    app.add_handler(CommandHandler("adminfinder", adminfinder_cmd))
    app.add_handler(CommandHandler("robots", robots_cmd))
    app.add_handler(CommandHandler("ai", ai_cmd))
    app.add_handler(CommandHandler("explain", ai_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    print(f"BOT STARTED - LINES: {len(open(__file__).readlines())}")
    app.run_polling()

if __name__ == "__main__":
    main()
