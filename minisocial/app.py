from flask import Flask, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

DB_PATH = os.path.join(os.path.dirname(__file__), "site.db")

# Veritabanını başlat
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        content TEXT
    )""")
    # admin kullanıcısı
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ("admin", generate_password_hash("1234")))
    conn.commit()
    conn.close()

init_db()

def style():
    return """
    <style>
        body { background:#0f0f0f; color:white; font-family:Arial; text-align:center; }
        input, textarea, button { padding:10px; margin:5px; border-radius:5px; border:none; }
        button { background:#00ffcc; cursor:pointer; }
        a { color:#00ffcc; text-decoration:none; }
        .post { background:#1c1c1c; margin:10px auto; padding:10px; width:300px; border-radius:10px; }
    </style>
    """

@app.route("/")
def home():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, content FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    post_html = "".join([f"<div class='post'><b>{p[0]}</b><br>{p[1]}</div>" for p in posts])
    if "user" in session:
        return style() + f"""
        <h1>Hoş geldin {session['user']} 😎</h1>
        <a href='/logout'>Çıkış</a><br><br>
        <form method='POST' action='/post'>
            <textarea name='content' placeholder='Ne düşünüyorsun?' required></textarea><br>
            <button type='submit'>Paylaş</button>
        </form>
        <h2>Postlar</h2>
        {post_html}
        """
    return style() + """
    <h1>Mini Sosyal Medya</h1>
    <a href='/login'>Giriş Yap</a><br><br>
    <a href='/register'>Kayıt Ol</a>
    """

@app.route("/post", methods=["POST"])
def post():
    if "user" not in session:
        return redirect(url_for("login"))
    content = request.form["content"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO posts (username, content) VALUES (?, ?)", (session["user"], content))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            return style() + "Bu kullanıcı zaten var ❌"
    return style() + """
    <h2>Kayıt Ol</h2>
    <form method="POST">
        <input name="username" placeholder="Kullanıcı adı"><br>
        <input name="password" type="password" placeholder="Şifre"><br>
        <button type="submit">Kayıt Ol</button>
    </form>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return style() + "Hatalı giriş ❌"
    return style() + """
    <h2>Giriş Yap</h2>
    <form method="POST">
        <input name="username" placeholder="Kullanıcı adı"><br>
        <input name="password" type="password" placeholder="Şifre"><br>
        <button type="submit">Giriş Yap</button>
    </form>
    """

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()