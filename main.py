import os
import re
import ssl
import time
import json
import socket
import hashlib
import sqlite3
import logging
import ipaddress
import asyncio
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DATABASE_PATH", "demini.db")
VT_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
SAFE_KEY = os.getenv("GOOGLE_SAFE_BROWSING_KEY", "")
NVD_KEY = os.getenv("NVD_API_KEY", "")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")

ADMINS = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("DEMINI")
START_TIME = time.time()


def now():
    return datetime.now(timezone.utc).isoformat()


def database():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def setup_database():
    with database() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            banned INTEGER DEFAULT 0,
            joined TEXT
        );

        CREATE TABLE IF NOT EXISTS settings(
            name TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            details TEXT,
            status TEXT DEFAULT 'open',
            created_by INTEGER,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS sites(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner INTEGER,
            url TEXT,
            last_status TEXT,
            UNIQUE(owner, url)
        );

        CREATE TABLE IF NOT EXISTS playlists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner INTEGER,
            title TEXT,
            url TEXT
        );

        CREATE TABLE IF NOT EXISTS audit(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor INTEGER,
            action TEXT,
            created_at TEXT
        );

        INSERT OR IGNORE INTO settings(name,value)
        VALUES('maintenance','0');
        """)


def record(actor, action):
    with database() as con:
        con.execute(
            "INSERT INTO audit(actor,action,created_at) VALUES(?,?,?)",
            (actor, action[:300], now()),
        )


def is_admin(uid):
    return uid in ADMINS


def in_maintenance():
    with database() as con:
        row = con.execute(
            "SELECT value FROM settings WHERE name='maintenance'"
        ).fetchone()
    return bool(row and row["value"] == "1")


async def check_access(update, admin=False):
    user = update.effective_user
    msg = update.effective_message

    if not user or not msg:
        return False

    with database() as con:
        con.execute("""
            INSERT OR IGNORE INTO users(user_id,username,joined)
            VALUES(?,?,?)
        """, (user.id, user.username or "", now()))

        con.execute(
            "UPDATE users SET username=? WHERE user_id=?",
            (user.username or "", user.id),
        )

        row = con.execute(
            "SELECT banned FROM users WHERE user_id=?",
            (user.id,),
        ).fetchone()

    if row and row["banned"]:
        await msg.reply_text("⛔ Access denied.")
        return False

    if admin and not is_admin(user.id):
        await msg.reply_text("⛔ Admin access required.")
        return False

    if in_maintenance() and not is_admin(user.id):
        await msg.reply_text("🛠 Bot is under maintenance.")
        return False

    return True


def validate_url(value):
    value = value.strip()
    parsed = urlparse(
        value if "://" in value else "https://" + value
    )

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS URL.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    host = parsed.hostname.lower().rstrip(".")
    host = host.encode("idna").decode("ascii")

    if host == "localhost" or host.endswith((".local", ".localhost")):
        raise ValueError("Local destinations are not allowed.")

    try:
        address = ipaddress.ip_address(host)
        if not address.is_global:
            raise ValueError("Private IP addresses are not allowed.")
    except ValueError as exc:
        if "not allowed" in str(exc):
            raise

    return parsed, host


async def public_request(url):
    parsed, host = validate_url(url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    addresses = await asyncio.wait_for(
        asyncio.get_running_loop().getaddrinfo(
            host, port, type=socket.SOCK_STREAM
        ),
        timeout=10,
    )

    if not addresses:
        raise ValueError("Hostname could not be resolved.")

    for address in addresses:
        if not ipaddress.ip_address(address[4][0]).is_global:
            raise ValueError("Private network destinations are blocked.")

    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=False,
        headers={"User-Agent": "DEMINI-CyberBot/1.0"},
    ) as client:
        return await client.get(url)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return

    await update.effective_message.reply_text(
        "🛡 DEMINI CYBER BOT PRO\n\n"
        "CYBERSECURITY\n"
        "/urlcheck <url>\n"
        "/reputation <url>\n"
        "/filehash <sha256>\n"
        "/hash <text>\n"
        "/headers <url>\n"
        "/tlscheck <hostname>\n"
        "/ipinfo <public_ip>\n"
        "/cve <keyword or CVE-ID>\n"
        "/tip\n\n"
        "MONITORING\n"
        "/monitor <url>\n"
        "/sites\n"
        "/report\n"
        "/alerts\n\n"
        "INCIDENTS\n"
        "/incident <title> | <details>\n"
        "/incidents\n"
        "/resolve <id>\n\n"
        "MUSIC\n"
        "/artist <name>\n"
        "/track <name>\n"
        "/playlist <title> | <url>\n"
        "/playlistlist\n\n"
        "ADMIN\n"
        "/admin /stats /users\n"
        "/ban <user_id> /unban <user_id>\n"
        "/announce <message>\n"
        "/logs /maintenance on|off /backup\n\n"
        "/help - Help\n"
        "/id - Your Telegram ID"
    )


async def help_command(update, context):
    if await check_access(update):
        await start(update, context)


async def get_id(update, context):
    if await check_access(update):
        await update.effective_message.reply_text(
            f"Your Telegram ID: {update.effective_user.id}"
        )


async def hash_command(update, context):
    if not await check_access(update):
        return

    text = " ".join(context.args)
    if not text:
        await update.effective_message.reply_text(
            "Usage: /hash some_text"
        )
        return

    digest = hashlib.sha256(text.encode()).hexdigest()
    await update.effective_message.reply_text(
        f"SHA-256:\n{digest}"
    )


async def urlcheck(update, context):
    if not await check_access(update):
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /urlcheck https://example.com"
        )
        return

    try:
        parsed, host = validate_url(context.args[0])
        warnings = []

        if parsed.scheme != "https":
            warnings.append("Website does not use HTTPS.")

        if host.count("-") >= 3:
            warnings.append("Hostname contains many hyphens.")

        if host.startswith("xn--") or ".xn--" in host:
            warnings.append("Internationalized domain encoding detected.")

        if any(word in (host + parsed.path).lower()
               for word in ("login", "verify", "wallet", "password")):
            warnings.append("Contains common phishing-related terms.")

        if not warnings:
            warnings.append("No basic warning signs detected.")

        await update.effective_message.reply_text(
            "🔎 URL ANALYSIS\n\n"
            f"Hostname: {host}\n\n"
            + "\n".join("⚠️ " + item for item in warnings)
            + "\n\nThis heuristic check cannot prove a site is safe."
        )
    except Exception as exc:
        await update.effective_message.reply_text(str(exc))


async def reputation(update, context):
    if not await check_access(update):
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /reputation https://example.com"
        )
        return

    try:
        parsed, host = validate_url(context.args[0])
        url = parsed.geturl()
        results = []

        if SAFE_KEY:
            payload = {
                "client": {
                    "clientId": "DEMINI",
                    "clientVersion": "1.0",
                },
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE",
                        "SOCIAL_ENGINEERING",
                        "UNWANTED_SOFTWARE",
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}],
                },
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    "https://safebrowsing.googleapis.com/v4/"
                    "threatMatches:find",
                    params={"key": SAFE_KEY},
                    json=payload,
                )

            if response.is_success:
                matches = response.json().get("matches", [])
                results.append(
                    "Google Safe Browsing: "
                    + ("Threat match found!" if matches else "No match returned.")
                )
            else:
                results.append(f"Safe Browsing API: HTTP {response.status_code}")

        if VT_KEY:
            import base64
            url_id = base64.urlsafe_b64encode(
                url.encode()
            ).decode().rstrip("=")

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/urls/{url_id}",
                    headers={"x-apikey": VT_KEY},
                )

            if response.is_success:
                stats = response.json()["data"]["attributes"].get(
                    "last_analysis_stats", {}
                )
                results.append("VirusTotal: " + json.dumps(stats))
            else:
                results.append(f"VirusTotal API: HTTP {response.status_code}")

        if not results:
            results.append("Configure a Safe Browsing or VirusTotal API key.")

        await update.effective_message.reply_text(
            "🧪 THREAT INTELLIGENCE\n\n"
            + "\n".join(results)
            + "\n\nNo match does not guarantee safety."
        )
    except Exception as exc:
        await update.effective_message.reply_text(
            f"Lookup error: {exc}"
        )


async def filehash(update, context):
    if not await check_access(update):
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /filehash <SHA-256>"
        )
        return

    digest = context.args[0].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        await update.effective_message.reply_text("Invalid SHA-256 hash.")
        return

    if not VT_KEY:
        await update.effective_message.reply_text(
            "Configure VIRUSTOTAL_API_KEY."
        )
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"https://www.virustotal.com/api/v3/files/{digest}",
                headers={"x-apikey": VT_KEY},
            )

        if response.status_code == 404:
            message = "No record found for this hash."
        elif response.is_success:
            stats = response.json()["data"]["attributes"].get(
                "last_analysis_stats", {}
            )
            message = "File reputation:\n" + json.dumps(stats, indent=2)
        else:
            message = f"VirusTotal error: HTTP {response.status_code}"

        await update.effective_message.reply_text(message)
    except Exception as exc:
        await update.effective_message.reply_text(str(exc))


async def headers_command(update, context):
    if not await check_access(update):
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /headers https://your-site.example"
        )
        return

    try:
        response = await public_request(context.args[0])
        names = [
            "strict-transport-security",
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
            "permissions-policy",
        ]

        report = "\n".join(
            f"{name}: {response.headers.get(name, 'MISSING')}"
            for name in names
        )

        await update.effective_message.reply_text(
            f"HTTP status: {response.status_code}\n\n"
            f"{report}\n\n"
            "Review missing headers in context; not every header is "
            "required on every response."
        )
    except Exception as exc:
        await update.effective_message.reply_text(str(exc))


async def tlscheck(update, context):
    if not await check_access(update):
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /tlscheck example.com"
        )
        return

    host = context.args[0].lower().strip()
    if "://" in host or "/" in host or ":" in host:
        await update.effective_message.reply_text(
            "Enter a hostname only."
        )
        return

    try:
        addresses = await asyncio.to_thread(
            socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM
        )
        if not addresses or any(
            not ipaddress.ip_address(x[4][0]).is_global
            for x in addresses
        ):
            raise ValueError("Private destination blocked.")

        def inspect():
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as secure:
                    return secure.getpeercert(), secure.version()

        cert, version = await asyncio.to_thread(inspect)
        await update.effective_message.reply_text(
            f"TLS: {version}\n"
            f"Issuer: {cert.get('issuer')}\n"
            f"Valid from: {cert.get('notBefore')}\n"
            f"Valid until: {cert.get('notAfter')}"
        )
    except Exception as exc:
        await update.effective_message.reply_text(str(exc))


async def ipinfo(update, context):
    if not await check_access(update):
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /ipinfo <public_ip>"
        )
        return

    try:
        address = ipaddress.ip_address(context.args[0])
        if not address.is_global:
            raise ValueError("Only public IP addresses are supported.")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"https://ipinfo.io/{address}/json",
                params={"token": IPINFO_TOKEN} if IPINFO_TOKEN else {},
            )

        if response.is_success:
            data = response.json()
            await update.effective_message.reply_text(
                "IP INFORMATION\n\n"
                f"IP: {data.get('ip')}\n"
                f"Hostname: {data.get('hostname', 'Unknown')}\n"
                f"City: {data.get('city', 'Unknown')}\n"
                f"Region: {data.get('region', 'Unknown')}\n"
                f"Country: {data.get('country', 'Unknown')}\n"
                f"Organization: {data.get('org', 'Unknown')}"
            )
        else:
            await update.effective_message.reply_text(
                f"IP lookup failed: HTTP {response.status_code}"
            )
    except Exception as exc:
        await update.effective_message.reply_text(str(exc))


async def cve_command(update, context):
    if not await check_access(update):
        return
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text(
            "Usage: /cve CVE-2024-12345 or /cve OpenSSL"
        )
        return

    try:
        params = {"resultsPerPage": 5}
        if re.fullmatch(r"CVE-\d{4}-\d{4,}", query, re.I):
            params["cveId"] = query.upper()
        else:
            params["keywordSearch"] = query

        headers = {"apiKey": NVD_KEY} if NVD_KEY else {}

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params=params,
                headers=headers,
            )

        response.raise_for_status()
        items = response.json().get("vulnerabilities", [])

        if not items:
            result = "No CVE records found."
        else:
            lines = []
            for item in items:
                cve = item["cve"]
                descriptions = cve.get("descriptions", [])
                description = next(
                    (d["value"] for d in descriptions if d.get("lang") == "en"),
                    "No description",
                )
                lines.append(
                    f"{cve.get('id')}\n{description[:400]}"
                )
            result = "\n\n".join(lines)

        await update.effective_message.reply_text(result[:3900])
    except Exception as exc:
        await update.effective_message.reply_text(f"CVE lookup failed: {exc}")


async def tip_command(update, context):
    if not await check_access(update):
        return
    index = int(time.time() // 60) % len(TIPS)
    await update.effective_message.reply_text("💡 " + TIPS[index])


async def create_incident(update, context):
    if not await check_access(update):
        return
    raw = " ".join(context.args)
    if "|" not in raw:
        await update.effective_message.reply_text(
            "Usage: /incident Login alert | Investigate the unusual login"
        )
        return

    title, details = [x.strip() for x in raw.split("|", 1)]
    if not title or not details:
        await update.effective_message.reply_text(
            "Provide both a title and details."
        )
        return

    with database() as con:
        cur = con.execute(
            "INSERT INTO incidents(title,details,created_by,created_at) "
            "VALUES(?,?,?,?)",
            (title[:150], details[:2000], update.effective_user.id, now()),
        )
        incident_id = cur.lastrowid

    await update.effective_message.reply_text(
        f"Incident #{incident_id} created."
    )


async def incidents_command(update, context):
    if not await check_access(update):
        return

    with database() as con:
        rows = con.execute(
            "SELECT * FROM incidents ORDER BY id DESC LIMIT 10"
        ).fetchall()

    if not rows:
        await update.effective_message.reply_text("No incidents recorded.")
        return

    result = "\n\n".join(
        f"#{r['id'
