from flask import Flask, session, render_template, request, redirect, url_for
import sqlite3
from markupsafe import escape
import os

PROTECT_XSS = True
PROTECT_SQL = True
PROTECT_CSRF = False
# 连接数据库
def connect_db():
    db = sqlite3.connect('test.db')
    db.cursor().execute('CREATE TABLE IF NOT EXISTS comments '
                        '(id INTEGER PRIMARY KEY, '
                        'comment TEXT)')
    db.commit()

    db.cursor().execute('CREATE TABLE IF NOT EXISTS users '
                        '(id INTEGER PRIMARY KEY, '
                        'username TEXT, '
                        'password TEXT)')
    db.commit()

    db.cursor().execute('CREATE TABLE IF NOT EXISTS sessions '
                        '(id INTEGER PRIMARY KEY, '
                        'username TEXT, '
                        'session_id TEXT,'
                        'csrf_token TEXT)')
    db.commit()

    db.cursor().execute('INSERT INTO users (username, password) '
                        'VALUES (?, ?)', ('Ashuo', '123456'))
    db.commit()

    return db

# 添加评论
def add_comment(comment):
    session_id = request.cookies.get('session')
    csrf_token = request.form.get('csrf_token')
    db = connect_db()
    token = db.cursor().execute('SELECT csrf_token FROM sessions WHERE session_id=?', (session_id,)).fetchone()
    
    # TODO：为了防止 CSRF 攻击，我们需要检查是否有正确的 CSRF token。将此处变为 Flase 即可重新进行 CSRF 攻击
    if PROTECT_CSRF:
        if token[0] == csrf_token:
            db.cursor().execute('INSERT INTO comments (comment) '
                                'VALUES (?)', (comment,))
            db.commit()

    else:
        db.cursor().execute('INSERT INTO comments (comment) '
                            'VALUES (?)', (comment,))
        db.commit()

# 得到评论
def get_comments(search_query=None):
    db = connect_db()
    results = []
    get_all_query = 'SELECT comment FROM comments'
    for (comment,) in db.cursor().execute(get_all_query).fetchall():
        if search_query is None or search_query in comment:
            results.append(comment)
    return results


# 启动flask
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        add_comment(request.form['comment'])

    search_query = request.args.get('q')

    comments = get_comments(search_query)
    
    # TODO：为了防止 XSS 攻击，我们需要对评论内容进行转义。将此处变为 Flase 即可重新进行 XSS 攻击
    if PROTECT_XSS:
        if search_query is not None:
            search_query = escape(search_query)
        comments = [escape(comment) for comment in comments]

    session_id = request.cookies.get('session')
    db = connect_db()
    user_token = db.cursor().execute('SELECT csrf_token FROM sessions WHERE session_id=?', (session_id,)).fetchone()
    
    if user_token:
        return render_template('index.html',
                           comments=comments,
                           search_query=search_query,
                           csrf_token=user_token[0])
    else:
        return redirect(url_for('login'))

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = connect_db()
        # TODO：为了防止 SQL 攻击，我们不能简单地拼接字符串。将此处变为 Flase 即可重新进行 SQL 注入攻击
        if PROTECT_SQL:
            user = db.cursor().execute('SELECT username FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        else:    
            user = db.cursor().execute('SELECT username FROM users WHERE username=\'{}\' AND password=\'{}\''.format(username, password)).fetchone()
            
        if user:
            session_id = os.urandom(16).hex()
            csrf_token = os.urandom(16).hex()
            db.cursor().execute('INSERT INTO sessions (username, session_id, csrf_token) VALUES (?, ?, ?)', (username, session_id, csrf_token))
            db.commit()
            res = redirect(url_for('index'))
            res.set_cookie('session', session_id)
            return res
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
    
# 注销
@app.route('/logout', methods=['POST'])
def logout():
    res = redirect(url_for('login'))

    # delete session
    session_id = request.cookies.get('session')
    db = connect_db()
    db.cursor().execute('DELETE FROM sessions WHERE session_id=?', (session_id,))
    db.commit()

    res.set_cookie('session', '', expires=0)
    return res

# CSRF 攻击
@app.route('/index', methods=['GET', 'POST'])
def csrf():
    if request.method == 'POST':
        add_comment(request.form['comment'])
        return render_template('index.html')
    else:
        return render_template('csrf.html')