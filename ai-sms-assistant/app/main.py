from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
SMS_DB_PATH = os.getenv('SMS_DB_PATH', '/tmp/sms.db')

def init_db():
    conn = sqlite3.connect(SMS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inbox (id INTEGER PRIMARY KEY, from_number TEXT, body TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, from_number TEXT, body TEXT)''')
    conn.commit()
    conn.close()

@app.route('/sms/inbound', methods=['POST'])
def inbound():
    data = request.get_json()
    from_number = data.get('from_number')
    body = data.get('body')
    # Store in inbox
    conn = sqlite3.connect(SMS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO inbox (from_number, body) VALUES (?, ?)', (from_number, body))
    conn.commit()
    conn.close()
    reply = 'Received your message.'  # Simple reply logic
    return jsonify({'reply': reply})

@app.route('/sms/outbox', methods=['GET'])
def outbox():
    conn = sqlite3.connect(SMS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM outbox')
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)

@app.route('/sms/inbox', methods=['GET'])
def inbox():
    conn = sqlite3.connect(SMS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inbox')
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)

@app.route('/sms/send', methods=['POST'])
def send():
    data = request.get_json()
    from_number = data.get('from_number')
    body = data.get('body')
    # Store in outbox
    conn = sqlite3.connect(SMS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO outbox (from_number, body) VALUES (?, ?)', (from_number, body))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Message sent'})

@app.route('/sms/reset', methods=['POST'])
def reset():
    conn = sqlite3.connect(SMS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inbox')
    cursor.execute('DELETE FROM outbox')
    conn.commit()
    conn.close()
    return jsonify({'status': 'Storage cleared'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)