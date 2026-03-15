import sqlite3
import uuid
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'for-my-princess-secret-key'

DB_PATH = os.path.join(os.path.dirname(__file__), 'gifts.db')
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp_portraits')
os.makedirs(TEMP_DIR, exist_ok=True)

# ── Database Setup ──
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gifts (
            id TEXT PRIMARY KEY,
            sender_name TEXT,
            letter_text TEXT,
            portrait_data TEXT,
            has_letter INTEGER DEFAULT 0,
            has_portrait INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

init_db()

# ── Sender Pages ──
@app.route('/')
def home():
    session.clear()
    # Clean up any leftover temp portrait
    temp_id = session.get('temp_id')
    if temp_id:
        temp_path = os.path.join(TEMP_DIR, f'{temp_id}.txt')
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return render_template('home.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/portrait')
def portrait():
    return render_template('portrait.html')

@app.route('/letter')
def letter():
    return render_template('letter.html')

@app.route('/flowers')
def flowers():
    return render_template('flowers.html')

# ── Save portrait to temp file (bypasses session size limit) ──
@app.route('/save-portrait', methods=['POST'])
def save_portrait():
    data = request.get_json()
    image_data = data.get('imageData', '')

    # Give this session a temp ID if it doesn't have one
    if 'temp_id' not in session:
        session['temp_id'] = str(uuid.uuid4())

    temp_path = os.path.join(TEMP_DIR, f"{session['temp_id']}.txt")
    with open(temp_path, 'w') as f:
        f.write(image_data)

    session['has_portrait'] = True
    return jsonify({'status': 'ok'})

# ── Save letter to session ──
@app.route('/save-letter', methods=['POST'])
def save_letter():
    data = request.get_json()
    session['letter_text'] = data.get('letterText', '')
    session['has_letter'] = True
    return jsonify({'status': 'ok'})

# ── Confirmation page ──
@app.route('/confirm')
def confirm():
    has_portrait = session.get('has_portrait', False)
    has_letter = session.get('has_letter', False)
    return render_template('confirm.html',
        has_portrait=has_portrait,
        has_letter=has_letter
    )

# ── Submit gift and generate link ──
@app.route('/submit-gift', methods=['POST'])
def submit_gift():
    data = request.get_json()
    sender_name = data.get('senderName', 'Thy Chosen Knight').strip() or 'Thy Chosen Knight'

    # Read portrait from temp file
    portrait_data = ''
    temp_id = session.get('temp_id')
    if temp_id:
        temp_path = os.path.join(TEMP_DIR, f'{temp_id}.txt')
        if os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                portrait_data = f.read()
            os.remove(temp_path)

    gift_id = str(uuid.uuid4())[:8]

    conn = get_db()
    conn.execute('''
        INSERT INTO gifts (id, sender_name, letter_text, portrait_data, has_letter, has_portrait)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        gift_id,
        sender_name,
        session.get('letter_text', ''),
        portrait_data,
        1 if session.get('has_letter') else 0,
        1 if session.get('has_portrait') else 0,
    ))
    conn.commit()
    conn.close()

    session.clear()
    return jsonify({'giftId': gift_id})

# ── Recipient Pages ──
@app.route('/gift/<gift_id>')
def chest(gift_id):
    conn = get_db()
    gift = conn.execute('SELECT * FROM gifts WHERE id = ?', (gift_id,)).fetchone()
    conn.close()
    if not gift:
        return render_template('404.html'), 404
    return render_template('chest.html', gift=gift)

@app.route('/gift/<gift_id>/letter')
def recipient_letter(gift_id):
    conn = get_db()
    gift = conn.execute('SELECT * FROM gifts WHERE id = ?', (gift_id,)).fetchone()
    conn.close()
    if not gift:
        return render_template('404.html'), 404
    return render_template('recipient_letter.html', gift=gift)

@app.route('/gift/<gift_id>/portrait')
def recipient_portrait(gift_id):
    conn = get_db()
    gift = conn.execute('SELECT * FROM gifts WHERE id = ?', (gift_id,)).fetchone()
    conn.close()
    if not gift:
        return render_template('404.html'), 404
    return render_template('recipient_portrait.html', gift=gift)

@app.route('/gift/<gift_id>/end')
def recipient_end(gift_id):
    return render_template('recipient_end.html')

if __name__ == '__main__':
    app.run(debug=True)
