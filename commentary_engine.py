"""
CodeCast Desi Aunty Taunts Engine
Turns every Claude Code terminal action into hilarious, passive-aggressive Desi Aunty taunts.
Sharma ji ka beta comparisons, shaadi reminders, and subah jaldi uthne ke faayde!
"""

import os
import json
import random
import urllib.request
import urllib.error

def load_dotenv():
    """Zero-dependency .env loader."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"\'')
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_dotenv()

# Iconic Desi Aunty Taunts for Every Developer Action
DESI_AUNTY_TAUNTS = {
    "FILE_EDITED": [
        "Sharma ji ke bete ko dekho, Google mein hai aur tum abhi tak CSS theek kar rahe ho.",
        "Kitni baar bola tha coding mat karo, ab baith ke semi-colon dhoondo.",
        "Itna dhyan padhai mein lagaya hota toh aaj shaadi ho gayi hoti beta.",
        "Ek file theek nahi ho rahi tumse, kal ko parivaar kaise sambhaloge?",
        "Itna backspace dabane se kismat nahi badal jayegi beta.",
        "Sharma ji ka beta do ghante mein app bana leta hai, aur tum ek file pe atke ho.",
        "Code mein itna badlav kar rahe ho, thoda dhyan apni sehat pe bhi de do.",
        "Pados wali aunty pooch rahi thi tumhara beta din bhar laptop pe kya karta hai."
    ],
    "TESTS_PASSED": [
        "Chalo ek baar toh pass hue, Sharma ji ka beta toh hamesha topper rehta hai.",
        "Nazar na lage kisi ki, pehle kaala teeka lagao phir git push karo beta.",
        "Test toh pass ho gaya beta, par rishtedaar abhi bhi package pooch rahe hain.",
        "Chamatkar ho gaya! Pehli baar test pass hua hai bina kisi rone ke.",
        "Pass hone pe itna khush mat ho, shaadi ke biodata mein kya likhenge?",
        "Sharma ji ke bete ke saare tests pehli baar mein green ho jaate hain."
    ],
    "TOOL_FAILED": [
        "Dekha! Humne pehle hi kaha tha subah jaldi utha karo, sab theek ho jayega.",
        "Yeh sab uss phone ka nateeja hai. 24 ghante bas phone aur laptop.",
        "Arre Ram Ram! Itna bada error? Sharma ji ko pata chala toh kya sochenge?",
        "Ek program toh dhang se chalta nahi, chale hain engineer banne!",
        "Error toh aayega hi beta, dhyan toh bas reels dekhne mein laga rehta hai.",
        "Stack trace dekh rahe ho? Kabhi apne lakshan bhi dekh liya karo.",
        "Tumse na ho payega beta, pados ke Verma ji ki tarah dukaan sambhalo ab."
    ],
    "GIT_STATUS": [
        "Git status baar baar dekhne se kya hoga? Rishtedaar toh status pehle hi dekh chuke hain.",
        "Sharma ji ka beta roz 10 commit karta hai, aur tum bas status check kar rahe ho.",
        "Terminal mein git status chalane se ghar ka kharcha nahi nikalta beta.",
        "Subah gunguna paani piya karo, terminal ke saare bugs apne aap theek ho jayenge.",
        "Itna time git status mein lagane se achha rishtedaaron ko phone kar lete."
    ],
    "BASH_COMMAND": [
        "Terminal mein command chalane se engineer nahi bante beta, package dikhana padta hai.",
        "Itna fast type kar rahe ho jaise koi NASA ka satellite launch kar rahe ho.",
        "Roz wahi kaale screen pe enter dabate rehte ho, kuch dhang ka kaam seekho.",
        "Sharma ji ka beta aath figure kama raha hai, aur tum terminal saaf kar rahe ho."
    ],
    "FIELD_SCOUTING": [
        "Sharma ji ka beta bina dekhe code likhta hai, aur tum 400 lines dhoondh rahe ho.",
        "Code dhoondh rahe ho ya apni khoyi hui engineering degree?",
        "Itni files khol ke baith gaye ho, jaise koi dahej ki list bana rahe ho.",
        "Itna dhyan agar rishto mein lagaya hota toh kab ka roka ho chuka hota."
    ],
    "PERMISSION_REQUIRED": [
        "Har baat pe permission chahiye? Sharma ji ka beta toh khud saare faisle leta hai.",
        "Bina mummy-papa ke aashirwaad ke yeh command mat chalana beta.",
        "Terminal se permission mang rahe ho, pehle mummy se aashirwaad le lo."
    ],
    "TASK_COMPLETED": [
        "Kaam khatam ho gaya? Chalo ab jaao dahi le aao dukaan se.",
        "Khatam toh kar diya, par Sharma ji ke bete jaisa package kab aayega?",
        "Yeh sab theek hai beta, par shaadi ke biodata mein kya likhein?",
        "Sharma ji ki beti ne isse aadhe time mein kar diya tha beta."
    ],
    "DEFAULT": [
        "Beta coding chhoro, thoda bahar ghoom aao, chehre pe noor hi chala gaya hai.",
        "Sharma ji ke bete ki nayi promotion ho gayi, aur tum bas enter daba rahe ho.",
        "Subah jaldi utho, yoga karo, saare syntax error gayab ho jayenge.",
        "Kuch kha liya karo beta, computer ke aage sookh ke kaanta ho gaye ho."
    ]
}

def clean_taunt(text):
    """Strip all quotation marks and clean whitespace."""
    if not text:
        return ""
    return text.replace('"', '').replace("'", '').replace('“', '').replace('”', '').replace('‘', '').replace('’', '').strip()

def get_random_commentary(event_type, context=""):
    ctx_lower = context.lower()
    
    # Specific taunts for git status and git commands
    if "git status" in ctx_lower or "git diff" in ctx_lower:
        taunt = random.choice(DESI_AUNTY_TAUNTS["GIT_STATUS"])
    elif event_type == "FILE_EDITED":
        taunt = random.choice(DESI_AUNTY_TAUNTS["FILE_EDITED"])
    elif event_type == "TESTS_PASSED":
        taunt = random.choice(DESI_AUNTY_TAUNTS["TESTS_PASSED"])
    elif event_type == "TOOL_FAILED":
        taunt = random.choice(DESI_AUNTY_TAUNTS["TOOL_FAILED"])
    elif event_type == "PERMISSION_REQUIRED":
        taunt = random.choice(DESI_AUNTY_TAUNTS["PERMISSION_REQUIRED"])
    elif event_type == "FIELD_SCOUTING":
        taunt = random.choice(DESI_AUNTY_TAUNTS["FIELD_SCOUTING"])
    elif event_type == "TASK_COMPLETED":
        taunt = random.choice(DESI_AUNTY_TAUNTS["TASK_COMPLETED"])
    elif "bash" in ctx_lower or event_type == "TOOL_EXECUTION":
        taunt = random.choice(DESI_AUNTY_TAUNTS["BASH_COMMAND"])
    else:
        taunt = random.choice(DESI_AUNTY_TAUNTS["DEFAULT"])

    return clean_taunt(taunt)

def generate_commentary(event_type, context="", title="", raw_data=None):
    """
    Generates hilarious Desi Aunty Taunt:
    1. Agent Router / OpenAI / Gemini LLM if configured and authorized
    2. Zero-latency Desi Aunty Taunts Matrix fallback
    """
    load_dotenv()
    agentrouter_key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    agentrouter_model = os.environ.get("AGENTROUTER_MODEL", "deepseek-v4-flash").strip()
    agentrouter_base = os.environ.get("AGENTROUTER_BASE_URL", "https://agentrouter.org/v1").rstrip("/")

    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    prompt = f"""You are an iconic, dramatic, passive-aggressive Indian Desi Aunty taunting someone who is coding in the terminal.
Action: {event_type} - {context}

CRITICAL RULES:
1. Roasting them with classic desi aunty taunts in Hindi/Hinglish (mention Sharma ji ka beta, shaadi, subah jaldi uthna, rishtedaar, package, phone ki galti, dahi lana).
2. Hilarious, sarcastic, sharp.
3. Length: Strictly 6 to 14 words in ONE sentence.
4. DO NOT use quotation marks. Absolutely no double quotes or single quotes. Output ONLY raw text."""

    # 1. Agent Router (if authorized)
    if agentrouter_key:
        try:
            url = f"{agentrouter_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {agentrouter_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            payload = json.dumps({
                "model": agentrouter_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a hilarious Desi Aunty taunting someone coding. Output strictly one short 6-14 word taunt in Hinglish without any quotes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 40,
                "temperature": 0.85
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "").strip()
                    if text:
                        return clean_taunt(text)
        except Exception:
            pass

    # 2. OpenAI / Gemini fallbacks
    if openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            }
            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 40
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if text:
                    return clean_taunt(text)
        except Exception:
            pass

    # 3. Pure Desi Aunty Taunts Matrix Fallback
    return get_random_commentary(event_type, context)
