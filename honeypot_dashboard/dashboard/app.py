from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from functools import wraps
from datetime import datetime
import logging
import random

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret in production

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
def db_connection():
    try:
        return pymysql.connect(host="localhost", user="amir", password="88226464", database="honeypot")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for('register'))

        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cur.fetchone():
                flash("Username already exists.", "warning")
                return redirect(url_for('register'))

            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash("An error occurred during registration.", "danger")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for('login'))

        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
            user = cur.fetchone()
            if user:
                session['user_id'] = user[0]
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password.", "danger")
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash("An error occurred during login.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template('login.html')

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Dashboard statistics and real-time intelligence
def get_stats():
    conn = db_connection()
    if conn is None:
        return 0, [], [], [], []

    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM access_logs")
        total = cur.fetchone()[0]

        cur.execute("SELECT ip_address, COUNT(*) as count FROM access_logs GROUP BY ip_address ORDER BY count DESC LIMIT 5")
        top_ips = cur.fetchall()

        cur.execute("SELECT file_accessed, COUNT(*) as count FROM access_logs GROUP BY file_accessed ORDER BY count DESC LIMIT 5")
        top_files = cur.fetchall()

        # Mock data for real-time alerting and analysis
        alerts = [
            {"time": datetime.now(), "message": "Suspicious IP detected: 192.168.1.5", "level": "High"},
            {"time": datetime.now(), "message": "Unauthorized file access attempt", "level": "Medium"}
        ]

        return total, top_ips, top_files, alerts
    except Exception as e:
        logging.error(f"Stats query error: {e}")
        return 0, [], [], [], []
    finally:
        cur.close()
        conn.close()

# Dashboard route
@app.route('/')
@login_required
def index():
    total, top_ips, top_files, alerts = get_stats()
    return render_template('index.html', total=total, top_ips=top_ips, top_files=top_files, alerts=alerts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
