from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from authlib.integrations.flask_client import OAuth
from functools import wraps
import json
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY')

# Fix for ngrok/proxy - makes Flask aware it's behind a reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure CORS
CORS(app, supports_credentials=True, origins=[
    f"https://{os.getenv('NGROK_DOMAIN')}",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
])

# Initialize OAuth
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    api_base_url=f"https://{os.getenv('AUTH0_DOMAIN')}",
    access_token_url=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

DATABASE = 'arabicwriter.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def requires_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def get_user_id():
    """Get current user's ID from session"""
    if 'user' in session:
        return session['user'].get('sub', 'anonymous')
    return 'anonymous'

def init_db():
    """Initialize the database"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='arabic_words'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Check and add missing columns
        cursor.execute("PRAGMA table_info(arabic_words)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'translation' not in columns:
            print('Adding translation column...')
            cursor.execute('ALTER TABLE arabic_words ADD COLUMN translation TEXT')
        if 'phonetic' not in columns:
            print('Adding phonetic column...')
            cursor.execute('ALTER TABLE arabic_words ADD COLUMN phonetic TEXT')
        if 'sentence' not in columns:
            print('Adding sentence column...')
            cursor.execute('ALTER TABLE arabic_words ADD COLUMN sentence TEXT')
        if 'arabic_sentence' not in columns:
            print('Adding arabic_sentence column...')
            cursor.execute('ALTER TABLE arabic_words ADD COLUMN arabic_sentence TEXT')
        if 'user_id' not in columns:
            print('Adding user_id column...')
            cursor.execute('ALTER TABLE arabic_words ADD COLUMN user_id TEXT')
        conn.commit()
    else:
        # Create table with all columns
        cursor.execute('''
            CREATE TABLE arabic_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                translation TEXT,
                phonetic TEXT,
                sentence TEXT,
                arabic_sentence TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                user_id TEXT
            )
        ''')
        conn.commit()
    
    conn.close()
    print('Database initialized')

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Serve the main page"""
    return app.send_static_file('index.html')

# Auth0 routes
@app.route('/login')
def login():
    """Redirect to Auth0 login"""
    try:
        # Use ngrok domain if available
        ngrok_domain = os.getenv('NGROK_DOMAIN')
        if ngrok_domain:
            redirect_uri = f"https://{ngrok_domain}/callback"
        else:
            redirect_uri = url_for('callback', _external=True, _scheme='https')
        
        print(f"Login redirect URI: {redirect_uri}")
        print(f"Auth0 Domain: {os.getenv('AUTH0_DOMAIN')}")
        print(f"Client ID: {os.getenv('AUTH0_CLIENT_ID')}")
        
        return auth0.authorize_redirect(redirect_uri=redirect_uri)
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/callback')
def callback():
    """Handle Auth0 callback"""
    try:
        print("Callback received")
        token = auth0.authorize_access_token()
        print(f"Token received: {token.get('userinfo', {})}")
        session['user'] = token['userinfo']
        return redirect('/')
    except Exception as e:
        print(f"Callback error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        + f"returnTo={url_for('index', _external=True, _scheme='https')}&"
        + f"client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )

@app.route('/api/user')
def get_user():
    """Get current user info"""
    if 'user' in session:
        return jsonify({
            'authenticated': True,
            'user': session['user']
        })
    return jsonify({'authenticated': False})

@app.route('/api/translate', methods=['POST'])
@requires_auth
def translate_word():
    """Translate Arabic word to English using OpenAI"""
    data = request.json
    arabic_word = data.get('word', '')
    
    if not arabic_word:
        return jsonify({'error': 'No word provided'}), 400
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a translator. Respond ONLY with valid JSON in this exact format: {\"english\": \"word\", \"phonetic\": \"pronunciation\", \"sentence\": \"example sentence\", \"arabic_sentence\": \"arabic example sentence\"}. No other text."},
                {"role": "user", "content": f"For the Arabic word '{arabic_word}', provide: 1) English translation (one word), 2) phonetic transliteration, 3) one simple example sentence using the word in English, 4) the same example sentence in Arabic."}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        import json
        result = json.loads(response.choices[0].message.content.strip())
        
        return jsonify({
            'success': True,
            'word': arabic_word,
            'translation': result['english'],
            'phonetic': result['phonetic'],
            'sentence': result['sentence'],
            'arabic_sentence': result['arabic_sentence']
        })
    except Exception as e:
        print(f"Translation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/words', methods=['POST'])
@requires_auth
def save_words():
    """Save words to database"""
    data = request.json
    words_data = data.get('words', [])
    session_id = data.get('sessionId', 'default')
    user_id = get_user_id()
    
    if not words_data:
        return jsonify({'error': 'No words provided'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    for item in words_data:
        word = item.get('word', '').strip()
        translation = item.get('translation', '')
        phonetic = item.get('phonetic', '')
        sentence = item.get('sentence', '')
        arabic_sentence = item.get('arabic_sentence', '')
        if word:
            cursor.execute(
                'INSERT INTO arabic_words (word, translation, phonetic, sentence, arabic_sentence, session_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (word, translation, phonetic, sentence, arabic_sentence, session_id, user_id)
            )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Saved {len(words_data)} words',
        'count': len(words_data)
    })

@app.route('/api/words', methods=['GET'])
@requires_auth
def get_words():
    """Get words from database with pagination and search"""
    session_id = request.args.get('sessionId')
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    search = request.args.get('search', '').strip()
    user_id = get_user_id()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Build query with filters - only get current user's words
    query = 'SELECT * FROM arabic_words WHERE user_id = ?'
    count_query = 'SELECT COUNT(*) as total FROM arabic_words WHERE user_id = ?'
    params = [user_id]
    
    if session_id:
        query += ' AND session_id = ?'
        count_query += ' AND session_id = ?'
        params.append(session_id)
    
    if search:
        query += ' AND (word LIKE ? OR translation LIKE ?)'
        count_query += ' AND (word LIKE ? OR translation LIKE ?)'
        search_param = f'%{search}%'
        params.append(search_param)
        params.append(search_param)
    
    # Get total count
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Get paginated results
    query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    words = [dict(row) for row in rows]
    return jsonify({
        'success': True,
        'words': words,
        'total': total,
        'page': (offset // limit) + 1,
        'per_page': limit
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get word statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_words,
            COUNT(DISTINCT word) as unique_words,
            COUNT(DISTINCT session_id) as total_sessions
        FROM arabic_words
    ''')
    
    stats = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({'stats': stats})

@app.route('/api/frequency', methods=['GET'])
def get_frequency():
    """Get word frequency"""
    limit = request.args.get('limit', 20, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            word,
            COUNT(*) as count
        FROM arabic_words
        GROUP BY word
        ORDER BY count DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    frequency = [dict(row) for row in rows]
    return jsonify({'frequency': frequency})

@app.route('/api/words', methods=['DELETE'])
def delete_words():
    """Delete words from database"""
    session_id = request.args.get('sessionId')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if session_id:
        cursor.execute('DELETE FROM arabic_words WHERE session_id = ?', (session_id,))
    else:
        cursor.execute('DELETE FROM arabic_words')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Words deleted'})

@app.route('/api/words/<int:word_id>', methods=['DELETE'])
@requires_auth
def delete_word(word_id):
    """Delete a single word by ID"""
    user_id = get_user_id()
    conn = get_db()
    cursor = conn.cursor()
    
    # Only delete if word belongs to current user
    cursor.execute('DELETE FROM arabic_words WHERE id = ? AND user_id = ?', (word_id, user_id))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Word not found'}), 404
    
    conn.close()
    return jsonify({'success': True, 'message': 'Word deleted'})

if __name__ == '__main__':
    print('Arabic Writer app running at http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
