# RESTful URL Shortening Microservice

A lightweight, persistent URL shortening service and redirect engine built with Python, Flask, and SQLite.

## Overview
Unlike basic in-memory implementations that lose data across process restarts, this microservice features durable ACID-compliant SQLite persistence, cryptographic non-sequential tokenization to mitigate ID enumeration attacks, atomic redirect analytics, and standard REST HTTP status compliance.

---

## Architectural Features

* **Persistent SQLite Storage:** Replaces volatile in-memory mappings with a dedicated SQLite database schema indexed on `short_code` for $O(1)$ indexed lookup latency.
* **Anti-Enumeration Security:** Generates cryptographically secure, high-entropy 6-character tokens (`secrets.token_urlsafe`) instead of predictable auto-increment IDs (`1, 2, 3...`), preventing automated catalog scraping.
* **Strict HTTP Status Semantics:**
  * `201 Created` for successfully provisioned short URLs.
  * `400 Bad Request` for missing payloads or invalid URL schemes.
  * `302 Found` for standard temporary resource redirects.
  * `404 Not Found` for unmapped or expired shortcodes.
* **Atomic Telemetry & Analytics:** Records and increments request click counts directly in the database during redirect execution.
* **Input Validation & Sanitization:** Enforces protocol checks (`http://`, `https://`) and URI parsing via `urllib.parse` to reject malformed payloads.

---

## API Specification

### 1. Shorten a URL
* **Endpoint:** `POST /shorten`
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "url": "[https://www.example.com/very/long/target/path](https://www.example.com/very/long/target/path)"
  }
Success Response (201 Created):

JSON
{
  "short_code": "k9xL2a",
  "short_url": "[http://127.0.0.1:5000/k9xL2a](http://127.0.0.1:5000/k9xL2a)"
}
Error Response (400 Bad Request):

JSON
{
  "error": "Bad Request: Invalid or unsupported URL scheme"
}
2. Resolve & Redirect
Endpoint: GET /<short_code>

Behavior: Atomically increments the clicks counter and returns a 302 Found redirect header targeting the destination URL.

Error Response (404 Not Found):

JSON
{
  "error": "Resource Not Found: Short code does not exist"
}
Local Setup & Installation
Prerequisites
Python 3.8+

pip

1. Clone the repository
Bash
git clone [https://github.com/stephelin/url-shortener.git](https://github.com/stephelin/url-shortener.git)
cd url-shortener
2. Set up virtual environment & install dependencies
Bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask
3. Run the service
Bash
python3 app.py
The service will initialize urls.db automatically and listen on http://127.0.0.1:5000.

Quick Testing with cURL
Bash
# 1. Generate a short URL
curl -X POST [http://127.0.0.1:5000/shorten](http://127.0.0.1:5000/shorten) \
  -H "Content-Type: application/json" \
  -d '{"url": "[https://news.ycombinator.com](https://news.ycombinator.com)"}'

# 2. Test redirect via terminal (inspect 302 Location header)
curl -i [http://127.0.0.1:5000/](http://127.0.0.1:5000/)<short_code>

---
