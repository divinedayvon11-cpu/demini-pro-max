# DEMINI PRO MAX PART 1 - CORE
import os, random, hashlib, base64, re, requests, socket, ssl, string, datetime
from flask import Flask
import threading
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER = "@GeeSavage"
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home(): return "DEMINI PRO MAX LIVE"
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

def gen_pass(n=20):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(n))

USERS_FILE = "users.txt"
FEED_FILE = "feedbacks.txt"

def track_user(u):
    try:
        uid=str(u.id)
        try:
            with open(USERS_FILE,"r",encoding="utf-8") as f:
                if uid in f.read(): return
        except: pass
        name=f"@{u.username}" if u.username else u.first_name
        with open(USERS_FILE,"a",encoding="utf-8") as f:
            f.write(f"{uid} | {name} | {datetime.datetime.now()}\n")
    except: pass

def count_users():
    try:
        with open(USERS_FILE,"r") as f: return len([l for l in f if l.strip()])
    except: return 0
def count_feed():
    try:
        with open(FEED_FILE,"r") as f: return len([l for l in f if l.strip()])
    except: return 0

async def start_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text(f"DEMINI PRO MAX\n103 Tools | Users: {count_users()}\n/help | Owner: {OWNER}")

async def help_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text("ALL TOOLS: /scanlink /sslcheck /dns /whois /headers /myip /safebrowse /unshort /iplookup /subnet /portinfo /siteinfo /trace /ping /vpncheck /breach /password /hash /b64 /feedback /users /stats")

async def owner_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text(f"Owner: {OWNER}\nUsers: {count_users()}")

async def about_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text(f"DEMINI PRO MAX 103 SINGLE")

async def ai_cmd(u,c):
    track_user(u.message.from_user)
    q=" ".join(c.args) or "secure?"
    await u.message.reply_text(f"AI: {q} -> 2FA, 16+ pass, VPN")

async def feedback_cmd(u,c):
    track_user(u.message.from_user)
    msg=" ".join(c.args)
    if not msg: return await u.message.reply_text("Usage: /feedback msg")
    user=u.message.from_user
    with open(FEED_FILE,"a",encoding="utf-8") as f: f.write(f"{datetime.datetime.now()} | {user.id}: {msg}\n")
    if OWNER_CHAT_ID:
        try: await c.bot.send_message(chat_id=int(OWNER_CHAT_ID), text=f"FEEDBACK @{user.username}: {msg}")
        except: pass
    await u.message.reply_text("✅ Feedback sent!")

async def feedbacks_cmd(u,c):
    if OWNER_CHAT_ID and str(u.message.from_user.id)!=str(OWNER_CHAT_ID): return await u.message.reply_text("Owner only")
    try:
        with open(FEED_FILE,"r",encoding="utf-8") as f: data=f.read()[-3500:]
        await u.message.reply_text(f"FEEDBACKS:\n{data}")
    except: await u.message.reply_text("No feedbacks")

async def users_cmd(u,c):
    if OWNER_CHAT_ID and str(u.message.from_user.id)!=str(OWNER_CHAT_ID): return await u.message.reply_text(f"Total: {count_users()}")
    try:
        with open(USERS_FILE,"r",encoding="utf-8") as f: data=f.read()[-3500:]
        await u.message.reply_text(f"TOTAL: {count_users()}\n{data}")
    except: await u.message.reply_text(f"Users: {count_users()}")

async def stats_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text(f"Users: {count_users()} | Feedbacks: {count_feed()} | Funcs: 103")

async def rate_cmd(u,c):
    track_user(u.message.from_user)
    await u.message.reply_text("Rate: /feedback 5 stars")

async def scanlink_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Scan {' '.join(c.args)} via VirusTotal")
async def sslcheck_cmd(u,c):
    track_user(u.message.from_user)
    d=" ".join(c.args).replace("https://","").split("/")[0]
    if not d: return await u.message.reply_text("Usage: /sslcheck google.com")
    try:
        ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=d) as s:
            s.settimeout(5); s.connect((d,443)); cert=s.getpeercert()
            await u.message.reply_text(f"SSL {d} valid {cert.get('notAfter')}")
    except Exception as e: await u.message.reply_text(f"Error {e}")

async def dns_cmd(u,c):
    track_user(u.message.from_user)
    d=" ".join(c.args)
    try: await u.message.reply_text(f"{d} -> {socket.gethostbyname(d)}")
    except Exception as e: await u.message.reply_text(f"Error {e}")
      async def whois_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"WHOIS who.is/whois/{' '.join(c.args)}")
async def headers_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Headers: HSTS CSP X-Frame")
async def myip_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"IP: {requests.get('https://api.ipify.org',timeout=5).text}")
async def safebrowse_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Safe: transparencyreport.google.com/safe-browsing/search?url={' '.join(c.args)}")
async def unshort_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"{requests.head(' '.join(c.args),allow_redirects=True,timeout=5).url}")
async def iplookup_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("ipinfo.io")
async def subnet_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("/24=256")
async def portinfo_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("80 443 22")
async def siteinfo_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"virustotal.com/gui/domain/{' '.join(c.args)}")
async def trace_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Trace hops")
async def ping_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Ping {' '.join(c.args)}")
async def vpncheck_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Check ipleak.net")
async def breach_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"haveibeenpwned.com { ' '.join(c.args)}")
async def password_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Pass: {gen_pass(20)}")
async def passstrength_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Use 16+ chars")
async def hash_cmd(u,c): track_user(u.message.from_user); t=" ".join(c.args); await u.message.reply_text(f"MD5 {hashlib.md5(t.encode()).hexdigest()}")
async def hmac_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("HMAC hash+key")
async def b64_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(base64.b64encode(" ".join(c.args).encode()).decode())
async def b64d_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(base64.b64decode(" ".join(c.args).encode()).decode())
async def qr_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("QR verify")
async def totpinfo_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("TOTP 2FA")
async def aesinfo_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("AES encryption")
async def rsainfo_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("RSA encryption")
async def salt_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Salt {gen_pass(8)}")
async def checksum_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Checksum file")
async def filehash_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("FileHash verify")
async def exifinfo_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("EXIF remove GPS")
async def yubikey_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("YubiKey best")
async def passmanager_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Bitwarden")
async def emailcheck_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Valid {bool(re.match(r'[^@]+@[^@]+\\.[^@]+', ' '.join(c.args)))}")
async def phoneformat_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Phone {' '.join(c.args)}")
async def urlcheck_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("https check")
async def ipvalid_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Valid IP check")
async def domaincheck_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"who.is/whois/{' '.join(c.args)}")
async def cookies_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Secure HttpOnly SameSite")
async def secureme_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("2FA 16+ VPN backup")
  async def darkwebtips_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("DarkWeb change pass 2FA")
async def securitynews_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("TheHackerNews")
async def phishquiz_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Check sender hover links")
async def hackhistory_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Yahoo Equifax")
async def bugbounty_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("HackerOne Bugcrowd")
async def expose_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text(f"Expose {' '.join(c.args)}")
async def vpn101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("VPN encrypts hides IP")
async def firewall101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Firewall blocks ports")
async def malware101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Malware AV")
async def social101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Social verify")
async def password101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("16+ unique")
async def fa101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Auth not SMS")
async def wifi101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("WiFi VPN")
async def email101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Email don't click unknown")
async def scam101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Too good = scam")
async def ransom101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Backup offline")
async def ddos101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("DDoS flood")
async def xss101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("XSS CSP sanitize")
async def sql101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("SQL param query")
async def wipeguide_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Wipe overwrite")
async def backupguide_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Backup 3-2-1")
async def incognito_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Incognito not ISP")
async def browsercheck_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Update remove ext")
async def osint101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Limit public info")
async def opsec_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Protect routine")
async def tor101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Tor privacy")
async def cors_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("CORS cross origin")
async def csp_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("CSP prevents XSS")
async def csrf101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("CSRF token")
async def ssrf101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("SSRF whitelist")
async def idor101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("IDOR access control")
async def lfi101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("LFI no user path")
async def rfi101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("RFI disable include")
async def xxe101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("XXE disable entities")
async def openredirect_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Whitelist redirect")
async def clickjacking_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("X-Frame DENY")
async def bruteforce101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Rate limit 2FA")
async def credentialstuffing_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Unique pass")
async def sessionhijack_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("HTTPS HttpOnly")
async def mitm101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("VPN HTTPS")
async def spoofing101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("SPF DKIM DMARC")
async def smishing_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("SMS phishing")
async def vishing_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Voice phishing")
async def whaling_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("CEO spear")
async def keylogger101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("AV 2FA")
async def spyware101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Avoid cracked apps")
async def adware101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Remove ext")
async def rootkit101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Reinstall OS")
async def trojan101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Official source")
async def worm101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Patch")
async def botnet101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Secure IoT")
async def zeroday_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Patch fast")
async def pentest101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Legal hack")
async def siem101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("Logs monitor")
async def js101_cmd(u,c): track_user(u.message.from_user); await u.message.reply_text("CSP sanitize")

def main():
    app_tele = Application.builder().token(BOT_TOKEN).build()
    app_tele.add_handler(CommandHandler("start", start_cmd))
    app_tele.add_handler(CommandHandler("help", help_cmd))
    app_tele.add_handler(CommandHandler("owner", owner_cmd))
    app_tele.add_handler(CommandHandler("about", about_cmd))
    app_tele.add_handler(CommandHandler("ai", ai_cmd))
    app_tele.add_handler(CommandHandler("feedback", feedback_cmd))
    app_tele.add_handler(CommandHandler("feedbacks", feedbacks_cmd))
    app_tele.add_handler(CommandHandler("users", users_cmd))
    app_tele.add_handler(CommandHandler("stats", stats_cmd))
    app_tele.add_handler(CommandHandler("rate", rate_cmd))
    app_tele.add_handler(CommandHandler("scanlink", scanlink_cmd))
    app_tele.add_handler(CommandHandler("sslcheck", sslcheck_cmd))
    app_tele.add_handler(CommandHandler("dns", dns_cmd))
    app_tele.add_handler(CommandHandler("whois", whois_cmd))
    app_tele.add_handler(CommandHandler("headers", headers_cmd))
    app_tele.add_handler(CommandHandler("myip", myip_cmd))
    app_tele.add_handler(CommandHandler("safebrowse", safebrowse_cmd))
    app_tele.add_handler(CommandHandler("unshort", unshort_cmd))
    app_tele.add_handler(CommandHandler("iplookup", iplookup_cmd))
    app_tele.add_handler(CommandHandler("subnet", subnet_cmd))
    app_tele.add_handler(CommandHandler("portinfo", portinfo_cmd))
    app_tele.add_handler(CommandHandler("siteinfo", siteinfo_cmd))
    app_tele.add_handler(CommandHandler("trace", trace_cmd))
    app_tele.add_handler(CommandHandler("ping", ping_cmd))
    app_tele.add_handler(CommandHandler("vpncheck", vpncheck_cmd))
    app_tele.add_handler(CommandHandler("breach", breach_cmd))
    app_tele.add_handler(CommandHandler("password", password_cmd))
    app_tele.add_handler(CommandHandler("passstrength", passstrength_cmd))
    app_tele.add_handler(CommandHandler("hash", hash_cmd))
    app_tele.add_handler(CommandHandler("hmac", hmac_cmd))
    app_tele.add_handler(CommandHandler("b64", b64_cmd))
    app_tele.add_handler(CommandHandler("b64d", b64d_cmd))
    app_tele.add_handler(CommandHandler("qr", qr_cmd))
    app_tele.add_handler(CommandHandler("totpinfo", totpinfo_cmd))
    app_tele.add_handler(CommandHandler("aesinfo", aesinfo_cmd))
    app_tele.add_handler(CommandHandler("rsainfo", rsainfo_cmd))
    app_tele.add_handler(CommandHandler("salt", salt_cmd))
    app_tele.add_handler(CommandHandler("checksum", checksum_cmd))
    app_tele.add_handler(CommandHandler("filehash", filehash_cmd))
    app_tele.add_handler(CommandHandler("exifinfo", exifinfo_cmd))
    app_tele.add_handler(CommandHandler("yubikey", yubikey_cmd))
    app_tele.add_handler(CommandHandler("passmanager", passmanager_cmd))
    app_tele.add_handler(CommandHandler("emailcheck", emailcheck_cmd))
    app_tele.add_handler(CommandHandler("phoneformat", phoneformat_cmd))
    app_tele.add_handler(CommandHandler("urlcheck", urlcheck_cmd))
    app_tele.add_handler(CommandHandler("ipvalid", ipvalid_cmd))
    app_tele.add_handler(CommandHandler("domaincheck", domaincheck_cmd))
    app_tele.add_handler(CommandHandler("cookies", cookies_cmd))
    app_tele.add_handler(CommandHandler("secureme", secureme_cmd))
    app_tele.add_handler(CommandHandler("darkwebtips", darkwebtips_cmd))
    app_tele.add_handler(CommandHandler("securitynews", securitynews_cmd))
    app_tele.add_handler(CommandHandler("phishquiz", phishquiz_cmd))
    app_tele.add_handler(CommandHandler("hackhistory", hackhistory_cmd))
    app_tele.add_handler(CommandHandler("bugbounty", bugbounty_cmd))
    app_tele.add_handler(CommandHandler("expose", expose_cmd))
    app_tele.add_handler(CommandHandler("vpn101", vpn101_cmd))
    app_tele.add_handler(CommandHandler("firewall101", firewall101_cmd))
    app_tele.add_handler(CommandHandler("malware101", malware101_cmd))
    app_tele.add_handler(CommandHandler("social101", social101_cmd))
    app_tele.add_handler(CommandHandler("password101", password101_cmd))
    app_tele.add_handler(CommandHandler("2fa101", fa101_cmd))
    app_tele.add_handler(CommandHandler("wifi101", wifi101_cmd))
    app_tele.add_handler(CommandHandler("email101", email101_cmd))
    app_tele.add_handler(CommandHandler("scam101", scam101_cmd))
    app_tele.add_handler(CommandHandler("ransom101", ransom101_cmd))
    app_tele.add_handler(CommandHandler("ddos101", ddos101_cmd))
    app_tele.add_handler(CommandHandler("xss101", xss101_cmd))
    app_tele.add_handler(CommandHandler("sql101", sql101_cmd))
    app_tele.add_handler(CommandHandler("wipeguide", wipeguide_cmd))
    app_tele.add_handler(CommandHandler("backupguide", backupguide_cmd))
    app_tele.add_handler(CommandHandler("incognito", incognito_cmd))
    app_tele.add_handler(CommandHandler("browsercheck", browsercheck_cmd))
    app_tele.add_handler(CommandHandler("osint101", osint101_cmd))
    app_tele.add_handler(CommandHandler("opsec", opsec_cmd))
    app_tele.add_handler(CommandHandler("tor101", tor101_cmd))
    app_tele.add_handler(CommandHandler("cors", cors_cmd))
    app_tele.add_handler(CommandHandler("csp", csp_cmd))
    app_tele.add_handler(CommandHandler("csrf101", csrf101_cmd))
    app_tele.add_handler(CommandHandler("ssrf101", ssrf101_cmd))
    app_tele.add_handler(CommandHandler("idor101", idor101_cmd))
    app_tele.add_handler(CommandHandler("lfi101", lfi101_cmd))
    app_tele.add_handler(CommandHandler("rfi101", rfi101_cmd))
    app_tele.add_handler(CommandHandler("xxe101", xxe101_cmd))
    app_tele.add_handler(CommandHandler("openredirect", openredirect_cmd))
    app_tele.add_handler(CommandHandler("clickjacking", clickjacking_cmd))
    app_tele.add_handler(CommandHandler("bruteforce101", bruteforce101_cmd))
    app_tele.add_handler(CommandHandler("credentialstuffing", credentialstuffing_cmd))
    app_tele.add_handler(CommandHandler("sessionhijack", sessionhijack_cmd))
    app_tele.add_handler(CommandHandler("mitm101", mitm101_cmd))
    app_tele.add_handler(CommandHandler("spoofing101", spoofing101_cmd))
    app_tele.add_handler(CommandHandler("smishing", smishing_cmd))
    app_tele.add_handler(CommandHandler("vishing", vishing_cmd))
    app_tele.add_handler(CommandHandler("whaling", whaling_cmd))
    app_tele.add_handler(CommandHandler("keylogger101", keylogger101_cmd))
    app_tele.add_handler(CommandHandler("spyware101", spyware101_cmd))
    app_tele.add_handler(CommandHandler("adware101", adware101_cmd))
    app_tele.add_handler(CommandHandler("rootkit101", rootkit101_cmd))
    app_tele.add_handler(CommandHandler("trojan101", trojan101_cmd))
    app_tele.add_handler(CommandHandler("worm101", worm101_cmd))
    app_tele.add_handler(CommandHandler("botnet101", botnet101_cmd))
    app_tele.add_handler(CommandHandler("zeroday", zeroday_cmd))
    app_tele.add_handler(CommandHandler("pentest101", pentest101_cmd))
    app_tele.add_handler(CommandHandler("siem101", siem101_cmd))
    app_tele.add_handler(CommandHandler("js101", js101_cmd))
    app_tele.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_cmd))
    print("DEMINI PRO MAX SINGLE 103 LIVE")
    app_tele.run_polling()

if __name__ == "__main__":
    main()
