import sqlite3
import re
import secrets
from urllib.parse import urlparse
from flask import Flask, request, redirect, jsonify, abort

app = Flask(__name__)
DB_NAME = "urls.db"

def init_db():
    """Initialize persistent SQLite table with indexing."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)")

def is_valid_url(url: str) -> bool:
    """Validate URL structure and protocol."""
    if not url or len(url) > 2048:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Bad Request: Missing 'url' payload"}), 400

    original_url = data["url"].strip()
    if not is_valid_url(original_url):
        return jsonify({"error": "Bad Request: Invalid or unsupported URL scheme"}), 400

    # Generate a cryptographically secure 6-character token (bypasses sequential scraping)
    short_code = secrets.token_urlsafe(4)[:6]

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                (short_code, original_url)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        # Collision fallback retry
        short_code = secrets.token_urlsafe(5)[:7]
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                (short_code, original_url)
            )

    return jsonify({
        "short_code": short_code,
        "short_url": f"{request.host_url}{short_code}"
    }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_url(short_code):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Resource Not Found: Short code does not exist"}), 404

        # Increment click analytics atomically
        conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,))
        conn.commit()

    return redirect(row[0], code=302)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
