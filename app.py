from flask import Flask, render_template_string, request, jsonify, session
from flask_cors import CORS
import tweepy
import threading
import time
from datetime import datetime
import secrets

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)

CONSUMER_KEY = "0FOTjTsGIITp6tTBMJWMqlqzM"
CONSUMER_SECRET = "0uPLAuHKo8NFM4N7c4OJucivuh4gblqQkVOruCPpXKVqhqhao3"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIJ48QEAAAAACSfj66yu9D221b2p54yccq3PyRk=ZHasMmofSntLxA2lc3W94lCaslrh7FsS3yS9XgzVxZ74NPm0A7"
ACCESS_TOKEN = "1215682194804486144-wzjhMVyd6w40ZtMSvCwBLQ4KSh64yC"
ACCESS_TOKEN_SECRET = "8PDByzZFbxyN9EMAj1YxOnl9q0RTEakp5EFzvHI0iEmmM"

client = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET, bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

bot_state = {"running": False, "blocked_count": 0, "logs": []}

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    log = f"[{ts}] {msg}"
    bot_state["logs"].append(log)
    if len(bot_state["logs"]) > 100:
        bot_state["logs"] = bot_state["logs"][-50:]

@app.route('/')
def login():
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>X Bot</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}.container{background:white;border-radius:20px;max-width:400px;width:100%;padding:50px 40px;text-align:center}.icon{font-size:70px;margin-bottom:20px}.title{font-size:32px;font-weight:700;color:#333;margin-bottom:12px}.form-group{margin-bottom:20px;text-align:left}.form-group label{display:block;font-size:13px;font-weight:600;color:#555;margin-bottom:8px}.form-group input{width:100%;padding:14px;border:2px solid #e0e0e0;border-radius:10px;font-size:15px;font-family:inherit}.btn{width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;margin-top:20px}.error{background:#ffe8e8;color:#ff4757;padding:12px;border-radius:8px;margin-bottom:20px;display:none}</style></head><body><div class="container"><span class="icon">robotemoji</span><div class="title">X Bot</div><div class="error" id="error"></div><form onsubmit="login(event)"><div class="form-group"><label>Twitter Kullanici Adi</label><input type="text" id="username" placeholder="@username" required></div><div class="form-group"><label>Twitter Sifre</label><input type="password" id="password" placeholder="..." required></div><button type="submit" class="btn">Giris Yap</button></form></div><script>async function login(e){e.preventDefault();const u=document.getElementById("username").value;const p=document.getElementById("password").value;const r=await fetch("/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:u,password:p})});const d=await r.json();if(r.ok){window.location.href="/dashboard"}else{document.getElementById("error").textContent=d.error;document.getElementById("error").style.display="block"}}</script></body></html>'''
    return render_template_string(html)

@app.route('/login', methods=['POST'])
def login_check():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    if username and password:
        session['logged_in'] = True
        session['user'] = username
        return jsonify({"ok": True}), 200
    return jsonify({"error": "Hatali"}), 401

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return "Hata", 403
    user = session.get('user', 'User')
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>X Bot</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}.container{{background:white;border-radius:20px;max-width:450px;width:100%;padding:40px}}.header{{text-align:center;margin-bottom:40px;position:relative}}.icon{{font-size:60px;margin-bottom:15px}}.title{{font-size:28px;font-weight:700;color:#333;margin-bottom:8px}}.logout{{position:absolute;top:-30px;right:0;background:#ff4757;color:white;border:none;padding:8px 12px;border-radius:6px;font-size:12px;cursor:pointer}}.form-group{{margin-bottom:20px}}.form-group label{{display:block;font-size:13px;font-weight:600;color:#555;margin-bottom:8px}}.form-group input,.form-group select{{width:100%;padding:12px 14px;border:2px solid #e0e0e0;border-radius:10px;font-size:15px;font-family:inherit}}.button-group{{display:flex;gap:12px;margin-bottom:25px}}button{{flex:1;padding:14px;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer}}.btn-primary{{background:linear-gradient(135deg,#667eea,#764ba2);color:white}}.btn-secondary{{background:#f5f5f5;color:#333}}.status-box{{background:#f8f9fa;border-radius:10px;padding:16px;margin-bottom:20px;border-left:4px solid #667eea}}.status-value{{font-size:24px;font-weight:700;color:#333}}.log{{background:#1a1a1a;color:#00d26a;padding:12px;border-radius:8px;font-size:12px;font-family:monospace;max-height:200px;overflow-y:auto;margin-bottom:20px;line-height:1.5}}.log-entry{{margin-bottom:4px}}</style></head><body><div class="container"><div class="header"><a class="logout" href="/logout">Cikis</a><span class="icon">robotemoji</span><div class="title">X Bot</div></div><div style="font-size:12px;color:#666;margin-bottom:20px">Hos geldin, {user}</div><div class="form-group"><label>Aranacak Konu</label><input type="text" id="query" placeholder="#Python" value=""></div><div class="form-group"><label>Kac Tweet</label><input type="number" id="limit" placeholder="50" value="50" min="10" max="500"></div><div class="form-group"><label>Islem</label><select id="action"><option value="block">Engelle</option><option value="mute">Sesini Kapat</option></select></div><div class="button-group"><button class="btn-primary" onclick="startBot()">Baslat</button><button class="btn-secondary" onclick="stopBot()">Durdur</button></div><div class="status-box"><div style="font-size:12px;color:#999">Engellenen</div><div class="status-value" id="stats">0</div></div><div class="log" id="logBox"></div><button class="btn-secondary" onclick="clearLogs()" style="width:100%;">Temizle</button></div><script>let botRunning=false;function addLog(m){{const l=document.getElementById("logBox");const e=document.createElement("div");e.className="log-entry";e.textContent=m;l.appendChild(e);l.scrollTop=l.scrollHeight}}function clearLogs(){{document.getElementById("logBox").innerHTML="";addLog("Temizlendi")}}async function startBot(){{const q=document.getElementById("query").value.trim();const l=document.getElementById("limit").value;const a=document.getElementById("action").value;if(!q){{addLog("Konu yazin");return}}botRunning=true;addLog("Baslatiliyor...");const r=await fetch("/start",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{query:q,limit:parseInt(l),action:a}})}});const d=await r.json();addLog("Bitti: "+d.blocked+" hesap");document.getElementById("stats").textContent=d.blocked;botRunning=false}}function stopBot(){{botRunning=false;addLog("Durduruldu")}}addLog("Hazir")</script></body></html>'''
    return render_template_string(html)

@app.route('/logout')
def logout():
    session.clear()
    return '<script>window.location.href="/"</script>'

@app.route('/start', methods=['POST'])
def start_bot():
    if not session.get('logged_in'):
        return jsonify({"error": "Login"}), 403
    
    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 50)
    action = data.get('action', 'block')
    
    bot_state["running"] = True
    bot_state["blocked_count"] = 0
    
    thread = threading.Thread(target=run_bot, args=(query, limit, action))
    thread.daemon = True
    thread.start()
    
    return jsonify({"blocked": 0}), 202

def run_bot(query, limit, action):
    try:
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(limit, 100),
            tweet_fields=['author_id'],
            expansions=['author_id'],
            user_fields=['verified', 'username']
        )
        
        if not tweets.data:
            bot_state["running"] = False
            return
        
        users = {}
        if tweets.includes and 'users' in tweets.includes:
            for user in tweets.includes['users']:
                if user.verified:
                    users[user.id] = user.username
        
        if not users:
            bot_state["running"] = False
            return
        
        success = 0
        for uid, uname in users.items():
            try:
                if action == 'block':
                    client.block(target_user_id=uid)
                elif action == 'mute':
                    client.mute(target_user_id=uid)
                success += 1
                bot_state["blocked_count"] = success
                time.sleep(1)
            except:
                pass
        
    except:
        pass
    finally:
        bot_state["running"] = False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
