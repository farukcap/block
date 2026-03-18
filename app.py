from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import tweepy
import os
import threading
import time
from datetime import datetime

app = Flask(**name**)
CORS(app)

# X API Bilgileri

CONSUMER_KEY = “0FOTjTsGIITp6tTBMJWMqlqzM”
CONSUMER_SECRET = “0uPLAuHKo8NFM4N7c4OJucivuh4gblqQkVOruCPpXKVqhqhao3”
BEARER_TOKEN = “AAAAAAAAAAAAAAAAAAAAAIJ48QEAAAAACSfj66yu9D221b2p54yccq3PyRk=ZHasMmofSntLxA2lc3W94lCaslrh7FsS3yS9XgzVxZ74NPm0A7”
ACCESS_TOKEN = “1215682194804486144-wzjhMVyd6w40ZtMSvCwBLQ4KSh64yC”
ACCESS_TOKEN_SECRET = “8PDByzZFbxyN9EMAj1YxOnl9q0RTEakp5EFzvHI0iEmmM”

# Tweepy istemcisi

try:
client = tweepy.Client(
consumer_key=CONSUMER_KEY,
consumer_secret=CONSUMER_SECRET,
access_token=ACCESS_TOKEN,
access_token_secret=ACCESS_TOKEN_SECRET,
bearer_token=BEARER_TOKEN,
wait_on_rate_limit=True
)
except Exception as e:
print(f”❌ Tweepy hatası: {e}”)
client = None

# Bot durumu

bot_state = {
“running”: False,
“blocked_count”: 0,
“current_query”: “”,
“status”: “Hazır”,
“logs”: []
}

def add_log(message):
“”“Log ekle”””
timestamp = datetime.now().strftime(”%H:%M:%S”)
log_msg = f”[{timestamp}] {message}”
bot_state[“logs”].append(log_msg)
if len(bot_state[“logs”]) > 100:
bot_state[“logs”] = bot_state[“logs”][-50:]
print(log_msg)

@app.route(’/’)
def index():
“”“Ana sayfa - Web arayüzü”””
html = “””
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X Mavi Tik Bot</title>
<style>
* {
margin: 0;
padding: 0;
box-sizing: border-box;
}

```
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            width: 100%;
            padding: 40px;
            animation: slideUp 0.6s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .icon {
            font-size: 60px;
            margin-bottom: 15px;
            display: block;
        }

        .title {
            font-size: 28px;
            font-weight: 700;
            color: #333;
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 14px;
            color: #999;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #555;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px 14px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 15px;
            font-family: inherit;
            transition: all 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .button-group {
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
        }

        button {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:active {
            transform: scale(0.97);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn-secondary {
            background: #f5f5f5;
            color: #333;
        }

        .btn-secondary:active {
            background: #e8e8e8;
        }

        .status-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .status-label {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 6px;
            font-weight: 600;
        }

        .status-value {
            font-size: 24px;
            font-weight: 700;
            color: #333;
        }

        .status-box.success {
            border-left-color: #2ed573;
            background: #f0ffe8;
        }

        .status-box.success .status-value {
            color: #2ed573;
        }

        .status-box.error {
            border-left-color: #ff4757;
            background: #ffe8e8;
        }

        .status-box.error .status-value {
            color: #ff4757;
        }

        .log {
            background: #1a1a1a;
            color: #00d26a;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            font-family: 'Courier New', monospace;
            max-height: 200px;
            overflow-y: auto;
            margin-bottom: 20px;
            line-height: 1.5;
            border: 1px solid #333;
        }

        .log-entry {
            margin-bottom: 4px;
        }

        .info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            color: #1565c0;
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .divider {
            height: 1px;
            background: #e0e0e0;
            margin: 25px 0;
        }

        @media (max-width: 360px) {
            .container {
                padding: 25px;
            }
            .title {
                font-size: 24px;
            }
            button {
                font-size: 13px;
                padding: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="icon">🤖</span>
            <div class="title">X Bot</div>
            <div class="subtitle">Mavi Tik Engelleme</div>
        </div>

        <div class="info">
            ✨ Mavi tik'li hesapları otomatik olarak engelle
        </div>

        <div class="form-group">
            <label>Aranacak Konu / Hashtag</label>
            <input type="text" id="query" placeholder="#Python" value="">
        </div>

        <div class="form-group">
            <label>Kaç Tweet Taranacak?</label>
            <input type="number" id="limit" placeholder="50" value="50" min="10" max="500">
        </div>

        <div class="form-group">
            <label>İşlem Tipi</label>
            <select id="action">
                <option value="block">🚫 Engelle</option>
                <option value="mute">🔇 Sesini Kapat</option>
            </select>
        </div>

        <div class="button-group">
            <button class="btn-primary" id="startBtn" onclick="startBot()">▶️ Başlat</button>
            <button class="btn-secondary" id="stopBtn" onclick="stopBot()" disabled>⏹️ Durdur</button>
        </div>

        <div class="status-box" id="statsBox">
            <div class="status-label">Engellenen Hesaplar</div>
            <div class="status-value">0</div>
        </div>

        <div class="log" id="logBox"></div>

        <div class="status-box" id="statusBox">
            <div class="status-label">Durum</div>
            <div class="status-value">Hazır</div>
        </div>

        <button class="btn-secondary" onclick="clearLogs()" style="width: 100%;">Günlüğü Temizle</button>
    </div>

    <script>
        let botRunning = false;

        function addLog(message) {
            const log = document.getElementById('logBox');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = message;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }

        function clearLogs() {
            document.getElementById('logBox').innerHTML = '';
            addLog('Günlük temizlendi.');
        }

        function updateStats(count) {
            document.querySelector('#statsBox .status-value').textContent = count;
        }

        function updateStatus(status, isError = false) {
            const box = document.getElementById('statusBox');
            document.querySelector('#statusBox .status-value').textContent = status;
            box.classList.toggle('error', isError);
            box.classList.toggle('success', !isError);
        }

        async function startBot() {
            if (botRunning) {
                addLog('❌ Bot zaten çalışıyor!');
                return;
            }

            const query = document.getElementById('query').value.trim();
            const limit = document.getElementById('limit').value;
            const action = document.getElementById('action').value;

            if (!query) {
                addLog('❌ Lütfen bir konu yazın!');
                return;
            }

            botRunning = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            updateStatus('Çalışıyor...', false);
            addLog('🚀 Bot başlatılıyor...');

            try {
                const response = await fetch('/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        limit: parseInt(limit),
                        action: action
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    addLog(`✅ Başarıyla tamamlandı!`);
                    addLog(`📊 ${data.blocked} hesap ${action === 'block' ? 'engellendi' : 'sesinin kapanması sağlandı'}`);
                    updateStats(data.blocked);
                    updateStatus('Tamamlandı ✓', false);
                } else {
                    addLog(`❌ Hata: ${data.error}`);
                    updateStatus('Hata oluştu', true);
                }
            } catch (error) {
                addLog(`❌ Hata: ${error.message}`);
                updateStatus('Bağlantı hatası', true);
            } finally {
                botRunning = false;
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
        }

        function stopBot() {
            botRunning = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            addLog('⏹️ Bot durduruldu.');
            updateStatus('Durduruldu', false);
        }

        // İlk log mesajı
        addLog('✅ Sistem hazır! Başlamak için konu yazın ve "Başlat" butonuna tıklayın.');
    </script>
</body>
</html>
"""
return render_template_string(html)
```

@app.route(’/start’, methods=[‘POST’])
def start_bot():
“”“Bot’u başlat”””
if not client:
return jsonify({“error”: “X API bağlantısı başarısız”}), 500

```
if bot_state["running"]:
    return jsonify({"error": "Bot zaten çalışıyor"}), 400

data = request.json
query = data.get('query', '').strip()
limit = data.get('limit', 50)
action = data.get('action', 'block')

if not query:
    return jsonify({"error": "Sorgu boş"}), 400

bot_state["running"] = True
bot_state["blocked_count"] = 0
bot_state["current_query"] = query

# Bot'u ayrı thread'de çalıştır
thread = threading.Thread(target=run_bot, args=(query, limit, action))
thread.daemon = True
thread.start()

return jsonify({"message": "Bot başlatıldı", "blocked": 0}), 202
```

def run_bot(query, limit, action):
“”“Bot işlemi”””
try:
add_log(f’🔍 “{query}” aranıyor…’)
bot_state[“status”] = f”Taranıyor: {query}”

```
    # Tweet'leri ara
    tweets = client.search_recent_tweets(
        query=query,
        max_results=min(limit, 100),
        tweet_fields=['author_id'],
        expansions=['author_id'],
        user_fields=['verified', 'username']
    )

    if not tweets.data:
        add_log("⚠️ Tweet bulunamadı")
        bot_state["status"] = "Tweet bulunamadı"
        bot_state["running"] = False
        return

    # Mavi tik'li kullanıcıları bul
    users_to_action = {}

    if tweets.includes and 'users' in tweets.includes:
        for user in tweets.includes['users']:
            if user.verified:
                users_to_action[user.id] = user.username

    if not users_to_action:
        add_log("⚠️ Mavi tik'li kullanıcı bulunamadı")
        bot_state["status"] = "Mavi tik bulunamadı"
        bot_state["running"] = False
        return

    add_log(f"📌 {len(users_to_action)} mavi tik'li hesap bulundu")
    add_log(f"🔄 İşlem başlanıyor ({action})...")

    # İşlem yap
    success_count = 0
    for user_id, username in users_to_action.items():
        try:
            if action == 'block':
                client.block(target_user_id=user_id)
                add_log(f"✅ @{username} engellendi")
            elif action == 'mute':
                client.mute(target_user_id=user_id)
                add_log(f"✅ @{username} sesinin kapanması sağlandı")

            success_count += 1
            bot_state["blocked_count"] = success_count
            bot_state["status"] = f"{success_count} işlem tamamlandı"

            time.sleep(1)  # Rate limit

        except Exception as e:
            add_log(f"⚠️ @{username} başarısız: {str(e)[:50]}")

    add_log(f"✅ Tamamlandı! {success_count} hesap işlendi")
    bot_state["status"] = "Tamamlandı ✓"

except Exception as e:
    add_log(f"❌ Hata: {str(e)}")
    bot_state["status"] = f"Hata: {str(e)[:30]}"
    print(f"Bot hatası: {e}")

finally:
    bot_state["running"] = False
```

@app.route(’/status’, methods=[‘GET’])
def get_status():
“”“Durum bilgisi al”””
return jsonify({
“running”: bot_state[“running”],
“blocked_count”: bot_state[“blocked_count”],
“status”: bot_state[“status”],
“logs”: bot_state[“logs”]
})

if **name** == ‘**main**’:
add_log(“🚀 Sunucu başlatılıyor…”)
port = int(os.environ.get(‘PORT’, 5000))
app.run(debug=False, host=‘0.0.0.0’, port=port)
