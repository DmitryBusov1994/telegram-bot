from flask import Flask, request, jsonify
import asyncpg
from config import DATABASE_URL, CENT_APP_API_KEY
import hmac
import hashlib

app = Flask(__name__)

async def verify_signature(data: dict, signature: str) -> bool:
    secret = CENT_APP_API_KEY.encode()
    payload = f"{data['id']}{data['amount']}{data['status']}".encode()
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route('/callback', methods=['POST'])
async def callback():
    data = request.json
    signature = request.headers.get('X-Signature')

    if not await verify_signature(data, signature):
        return jsonify({"error": "Invalid signature"}), 400

    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        UPDATE payments SET status = $1 WHERE payment_id = $2
    ''', data['status'], data['id'])

    if data['status'] == 'success':
        if data['amount'] == 20:  # Разовый доступ
            await conn.execute('''
                UPDATE users SET paid_attempts = paid_attempts + 10
                WHERE user_id = $1
            ''', data['user_id'])
        elif data['amount'] == 100:  # Месячный доступ
            await conn.execute('''
                UPDATE users SET subscription_end = NOW() + INTERVAL '30 days'
                WHERE user_id = $1
            ''', data['user_id'])

    await conn.close()
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)