#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                         PROFESSIONAL GUEST GENERATOR API v18.0                       ║
║                    Full Details | Real Working | Professional Output                ║
║                          All 13 Servers | Fast & Powerful                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time
import random
import json
import base64
import hashlib
import hmac
import re
import string
import codecs
import warnings
import urllib3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================
HEX_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
KEY = bytes.fromhex(HEX_KEY)

REGISTER_URL = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
TOKEN_URL = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
MAJOR_REGISTER_URL = "https://loginbp.ggpolarbear.com/MajorRegister"
MAJOR_LOGIN_URL = "https://loginbp.ggpolarbear.com/MajorLogin"

# ==================== ALL 13 REGIONS ====================
ALL_REGIONS = ["IND", "ID", "TH", "VN", "ME", "BD", "PK", "TW", "EU", "CIS", "NA", "SAC", "BR"]

REGION_NAMES = {
    "IND": "🇮🇳 India", "ID": "🇮🇩 Indonesia", "TH": "🇹🇭 Thailand", "VN": "🇻🇳 Vietnam",
    "ME": "🌍 Middle East", "BD": "🇧🇩 Bangladesh", "PK": "🇵🇰 Pakistan", "TW": "🇹🇼 Taiwan",
    "EU": "🇪🇺 Europe", "CIS": "🇷🇺 Russia/CIS", "NA": "🇺🇸 North America", "SAC": "🇧🇷 South America",
    "BR": "🇧🇷 Brazil"
}

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th",
    "BD": "bn", "PK": "ur", "TW": "zh", "EU": "en", "CIS": "ru",
    "NA": "en", "SAC": "es", "BR": "pt"
}

# ==================== CRYPTO FUNCTIONS ====================
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    return EnC_Vr((field_number << 3) | 0) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    encoded = value.encode() if isinstance(value, str) else value
    return EnC_Vr((field_number << 3) | 2) + EnC_Vr(len(encoded)) + encoded

def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            packet.extend(CrEaTe_LenGTh(field, CrEaTe_ProTo(value)))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        else:
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet

def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(Z, AES.block_size))

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(plain_text, AES.block_size)).hex()

def decode_jwt_token(jwt):
    try:
        payload = jwt.split('.')[1]
        payload += '=' * ((4 - len(payload) % 4) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return str(data.get('account_id') or data.get('external_id', 'N/A'))
    except:
        return "N/A"

def generate_exponent_number():
    exponent_digits = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
    number = random.randint(1, 99999)
    number_str = f"{number:05d}"
    return ''.join(exponent_digits[d] for d in number_str)

def generate_random_name(base_name):
    suffixes = ['ツ', '★', '☆', '🔥', '⚡', '💀', '👑', '✨', '⭐', '💫', '♥️']
    return f"{base_name[:10]}{random.choice(suffixes)}{generate_exponent_number()}"

def generate_custom_password(user_prefix):
    """Generate password in format: PREFIX_BY_SULAV_GAMING_RANDOM"""
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{user_prefix}_BY_SULAV_GAMING_{random_suffix}"

def encode_string(orig):
    ks = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
          0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
    return {"open_id": orig, "field_14": ''.join(chr(ord(orig[i]) ^ ks[i%32]) for i in range(len(orig)))}

def to_unicode_escaped(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

# ==================== ACCOUNT GENERATION ====================
def guest_register(password):
    payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
    body_json = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(KEY, body_json.encode(), hashlib.sha256).hexdigest()
    headers = {
        "User-Agent": "GarenaMSDK/4.0.39(SM-A325M ;Android 13;en;HK;)",
        "Authorization": f"Signature {signature}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Connection": "Keep-Alive"
    }
    resp = requests.post(REGISTER_URL, headers=headers, data=body_json, timeout=30, verify=False)
    if resp.status_code != 200:
        raise Exception(f"Register failed: HTTP {resp.status_code}")
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Register error: {data}")
    return data['data']['uid']

def guest_token(uid, password):
    payload = {
        "client_id": 100067,
        "client_secret": HEX_KEY,
        "client_type": 2,
        "password": password,
        "response_type": "token",
        "uid": uid
    }
    body_json = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(KEY, body_json.encode(), hashlib.sha256).hexdigest()
    headers = {
        "User-Agent": "GarenaMSDK/4.0.39(SM-A325M ;Android 13;en;HK;)",
        "Authorization": f"Signature {signature}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Connection": "Keep-Alive"
    }
    resp = requests.post(TOKEN_URL, headers=headers, data=body_json, timeout=30, verify=False)
    if resp.status_code != 200:
        raise Exception(f"Token failed: HTTP {resp.status_code}")
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Token error: {data}")
    return data['data']['access_token'], data['data']['open_id']

def major_register(access_token, open_id, name, region):
    lang = REGION_LANG.get(region, "en")
    encoded = encode_string(open_id)
    field = to_unicode_escaped(encoded['field_14'])
    field = codecs.decode(field, 'unicode_escape').encode('latin1')
    
    payload = {1: name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 
               13: 1, 14: field, 15: lang, 16: 1, 17: 1}
    proto_bytes = CrEaTe_ProTo(payload)
    encrypted_payload = E_AEs(bytes(proto_bytes).hex())
    
    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggpolarbear.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4."
    }
    resp = requests.post(MAJOR_REGISTER_URL, headers=headers, data=encrypted_payload, verify=False, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"MajorRegister failed: HTTP {resp.status_code}")
    return True

def major_login(access_token, open_id):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload_hex = "1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134"
    payload = bytes.fromhex(payload_hex)
    payload = payload.replace(b"2025-07-30 11:02:51", now.encode())
    payload = payload.replace(b"996a629dbcdb3964be6b6978f5d814db", open_id.encode())
    payload = payload.replace(b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a", access_token.encode())
    
    encrypted = encrypt_api(payload.hex())
    final_payload = bytes.fromhex(encrypted)
    
    headers = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggpolarbear.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }
    resp = requests.post(MAJOR_LOGIN_URL, headers=headers, data=final_payload, verify=False, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"MajorLogin failed: HTTP {resp.status_code}")
    
    if "eyJ" in resp.text:
        jwt = resp.text[resp.text.find("eyJ"):]
        second = jwt.find(".", jwt.find(".")+1)
        if second != -1:
            jwt = jwt[:second+44]
            return jwt, decode_jwt_token(jwt)
    return None, None

# ==================== RARITY CHECK ====================
def check_rarity(account_id, threshold=7):
    if not account_id or account_id == "N/A":
        return False, 0
    score = 0
    if re.search(r'(\d)\1{3,}', account_id): score += 3
    if re.search(r'(12345|23456|34567|45678|56789|67890|76543|65432|54321|43210)', account_id): score += 4
    if len(account_id) >= 4 and account_id == account_id[::-1]: score += 5
    if len(set(account_id)) == 1 and len(account_id) >= 4: score += 5
    if len(account_id) <= 8 and account_id.isdigit() and int(account_id) < 1000000: score += 3
    if re.search(r'(000|111|222|333|444|555|666|777|888|999)', account_id): score += 2
    return score >= threshold, score

def generate_one_account(region, name_prefix, pass_prefix):
    try:
        password = generate_custom_password(pass_prefix)
        uid = guest_register(password)
        access_token, open_id = guest_token(uid, password)
        name = generate_random_name(name_prefix)
        major_register(access_token, open_id, name, region)
        jwt, account_id = major_login(access_token, open_id)
        return {
            "uid": uid,
            "password": password,
            "name": name,
            "account_id": account_id or "N/A",
            "region": region,
            "region_name": REGION_NAMES.get(region, region),
            "access_token": access_token,
            "open_id": open_id,
            "jwt_token": jwt,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "region": region}

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Professional Guest Generator API",
        "version": "18.0",
        "description": "Generate Free Fire guest accounts for all 13 servers",
        "author": "SULAV-CODEX",
        "password_format": "{prefix}_BY_SULAV_GAMING_{random}",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /regions": "List all available regions",
            "GET /generate?name=SULAV&password=Test&count=5&region=IND": "Generate accounts (GET method)",
            "POST /generate": "Generate accounts (POST method)",
            "GET /stats": "API statistics"
        },
        "usage_example": "https://your-api.vercel.app/generate?name=SULAV&password=Test&count=10&region=IND"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "regions_available": len(ALL_REGIONS)
    })

@app.route('/regions', methods=['GET'])
def get_regions():
    regions = []
    for code in ALL_REGIONS:
        regions.append({
            "code": code,
            "name": REGION_NAMES.get(code, code),
            "language": REGION_LANG.get(code, "en")
        })
    return jsonify({
        "total": len(regions),
        "regions": regions
    })

@app.route('/generate', methods=['GET', 'POST'])
def generate_accounts():
    """Main endpoint for account generation - Supports both GET and POST"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            name = request.args.get('name', 'SULAV')
            password = request.args.get('password', 'Test')
            count = int(request.args.get('count', 1))
            region = request.args.get('region', 'IND').upper()
        else:
            data = request.get_json() or {}
            name = data.get('name', 'SULAV')
            password = data.get('password', 'Test')
            count = int(data.get('count', 1))
            region = data.get('region', 'IND').upper()
        
        # Limit maximum count to 1,000,000 as requested
        if count > 10000000:
            return jsonify({
                "success": False,
                "error": "Maximum count is 10,000,000. Please reduce the number."
            }), 400
        
        if count < 1:
            return jsonify({
                "success": False,
                "error": "Count must be at least 1"
            }), 400
        
        if region not in ALL_REGIONS:
            return jsonify({
                "success": False,
                "error": f"Invalid region. Available: {', '.join(ALL_REGIONS)}"
            }), 400
        
        # For large counts, generate in batches
        accounts = []
        success_count = 0
        fail_count = 0
        rare_count = 0
        
        # Use threading for faster generation
        def generate_batch(batch_size):
            batch_accounts = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for i in range(batch_size):
                    futures.append(executor.submit(generate_one_account, region, name, password))
                
                for future in as_completed(futures):
                    result = future.result()
                    batch_accounts.append(result)
            return batch_accounts
        
        # Generate in batches of 50 to avoid overwhelming
        batch_size = min(50, count)
        total_batches = (count + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            current_batch_size = min(batch_size, count - success_count - fail_count)
            if current_batch_size <= 0:
                break
            
            batch_results = generate_batch(current_batch_size)
            
            for acc in batch_results:
                if "error" in acc:
                    fail_count += 1
                    accounts.append({"success": False, "error": acc["error"]})
                else:
                    success_count += 1
                    is_rare, rarity_score = check_rarity(acc.get('account_id', ''))
                    if is_rare:
                        rare_count += 1
                    accounts.append({
                        "success": True,
                        "account": acc,
                        "is_rare": is_rare,
                        "rarity_score": rarity_score
                    })
        
        return jsonify({
            "success": True,
            "region": region,
            "region_name": REGION_NAMES.get(region, region),
            "name_prefix": name,
            "password_prefix": password,
            "password_format": f"{password}_BY_SULAV_GAMING_{{random}}",
            "requested": count,
            "successful": success_count,
            "failed": fail_count,
            "rare_accounts": rare_count,
            "accounts": accounts,
            "generated_at": datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": "Invalid count parameter. Please provide a valid number."
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get API statistics"""
    return jsonify({
        "total_regions": len(ALL_REGIONS),
        "regions": ALL_REGIONS,
        "max_count_per_request": 10000000,
        "supported_methods": ["GET", "POST"],
        "password_format": "{prefix}_BY_SULAV_GAMING_{random}",
        "features": [
            "13 servers support",
            "Rarity checking",
            "Bulk generation up to 10M accounts",
            "Multi-threaded generation",
            "Professional output format"
        ]
    })

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/health", 
            "/regions",
            "/generate?name=NAME&password=PASS&count=COUNT&region=REGION",
            "/stats"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": "Please try again later"
    }), 500

# Vercel handler
app.debug = False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)