from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import requests
import uvicorn
import sqlite3
import os
import base64
import time
from datetime import datetime

app = FastAPI(title="Coin PT API")

# DB CONFIG
DB_PATH = "social_data.db"

# RATE LIMITING STORE (In-memory for simplicity)
# key: IP, value: last_post_timestamp
rate_limit_store = {}
COOLDOWN_SECONDS = 30 

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            nickname TEXT NOT NULL,
            content TEXT NOT NULL,
            image_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# MODELS
class SocialPost(BaseModel):
    nickname: str
    content: str
    image_data: Optional[str] = None # Base64 string
    honeypot: Optional[str] = None # Bot trap

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/crypto")
def get_crypto():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=true"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/social")
def get_social_posts(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    posts = [dict(row) for row in rows]
    conn.close()
    return posts

@app.post("/api/social")
def create_social_post(post: SocialPost, request: Request):
    # 1. HONEYPOT CHECK
    if post.honeypot:
        # If bot fills this field, reject silently or with error
        raise HTTPException(status_code=400, detail="Bot activity detected")
    
    # 2. RATE LIMITING
    client_ip = request.client.host
    now = time.time()
    if client_ip in rate_limit_store:
        last_post = rate_limit_store[client_ip]
        if now - last_post < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - (now - last_post))
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Please wait {remaining} seconds.")
    
    # 3. CONTENT VALIDATION
    if not post.content.strip():
        raise HTTPException(status_code=400, detail="Content required")
    
    # 4. SAVE POST
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO posts (timestamp, nickname, content, image_data)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, post.nickname, post.content, post.image_data))
    conn.commit()
    conn.close()
    
    # Update rate limit store
    rate_limit_store[client_ip] = now
    
    return {"status": "success"}

@app.delete("/api/social/{post_id}")
def delete_social_post(post_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
