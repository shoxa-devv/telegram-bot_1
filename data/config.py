import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Comma-separated list of admin IDs in env: "123,456"
ADMIN_IDS = [
    int(cid) for cid in (os.getenv("ADMIN_IDS", "") or "").split(",") if cid.strip().isdigit()
]

# Ensure explicit admin ID requested by project
if 1897652450 not in ADMIN_IDS:
    ADMIN_IDS.append(1897652450)

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("BOT_TOKEN or OPENAI_API_KEY is not set")

