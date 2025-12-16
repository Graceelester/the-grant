from flask import Blueprint, render_template, request, redirect, session, jsonify
import sqlite3
import random
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------- BLUEPRINT --------------------
account_bp = Blueprint(
    'account',  # blueprint endpoint name
    __name__,
    template_folder='templates',
    static_folder='static'
)

# -------------------- DATABASE --------------------
def get_db_connection():
    conn = sqlite3.connect(
        "ffg_credit_union.db",
        timeout=10,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            dob TEXT,
            address TEXT,
            ssn TEXT,
            grant_amount REAL,
            account_last4 TEXT,
            signup_date TEXT,
            application_number TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------- HELPERS --------------------
def generate_account_last4():
    return str(random.randint(1000, 9999))

def create_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    session['captcha_answer'] = a + b
    return f"{a} + {b}"

def validate_captcha(user_input):
    try:
        valid = int(user_input) == session.get('captcha_answer')
    except (TypeError, ValueError):
        valid = False
    session.pop('captcha_answer', None)
    return valid

# -------------------- ROUTES --------------------

# ----- Dashboard / Home -----
@account_bp.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/account/login')

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if not user:
        session.clear()
        return redirect('/account/login')

    return render_template(
        'index.html',
        user_name=user['full_name'],
        grant_amount=f"{user['grant_amount']:,.2f}",
        account_last4=user['account_last4'],
        signup_date=user['signup_date'],
        application_number=user['application_number'],
        show_bottom_nav=True
    )

# ----- Signup -----
@account_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        if not validate_captcha(request.form.get('captcha_response')):
            return render_template(
                'signup.html',
                error="Incorrect CAPTCHA",
                captcha_question=create_captcha(),
                show_bottom_nav=False
            )

        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        dob = request.form['dob']
        address = request.form['address']
        ssn = request.form['ssn']
        grant_amount = float(request.form['grant_amount'])
        application_number = request.form['application_number']

        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO users
                (full_name, email, password, dob, address, ssn,
                 grant_amount, account_last4, signup_date, application_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, email, password, dob, address, ssn,
                grant_amount, generate_account_last4(),
                datetime.datetime.now().strftime("%b %d, %Y"),
                application_number
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                'signup.html',
                error="Email already registered",
                captcha_question=create_captcha(),
                show_bottom_nav=False
            )

        user_id = c.lastrowid
        conn.close()

        session['user_id'] = user_id
        session['user_name'] = name
        return redirect('/account/')

    return render_template(
        'signup.html',
        captcha_question=create_captcha(),
        show_bottom_nav=False
    )

# ----- Login -----
@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not validate_captcha(request.form.get('captcha_response')):
            return render_template(
                'login.html',
                error="Incorrect CAPTCHA",
                captcha_question=create_captcha(),
                show_bottom_nav=False
            )

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            return redirect('/account/')

        return render_template(
            'login.html',
            error="Invalid email or password",
            captcha_question=create_captcha(),
            show_bottom_nav=False
        )

    return render_template(
        'login.html',
        captcha_question=create_captcha(),
        show_bottom_nav=False
    )

# ----- Profile -----
@account_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/account/login')

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if not user:
        session.clear()
        return redirect('/account/login')

    return render_template(
        'profile.html',
        user_name=user['full_name'],
        application_number=user['application_number'],
        address=user['address'],
        ssn=user['ssn'],
        email=user['email'],
        show_bottom_nav=True
    )

# ----- Other Pages -----
@account_bp.route('/transfer')
def transfer():
    return render_template('transfer.html', show_bottom_nav=True)

@account_bp.route('/cards')
def cards():
    return render_template('cards.html', show_bottom_nav=True)

@account_bp.route('/help')
def help_page():
    return render_template('help.html', show_bottom_nav=True)

# ----- Logout -----
@account_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/account/login')

# ----- Chat Bot API -----
@account_bp.route('/api/chat', methods=['POST'])
def chat_api():
    user_message = request.json.get('message', '').lower()

    bot_responses = {
        "hi": "Hello! How can I assist you today?",
        "hello": "Hi there! How can I help?",
        "reset password": "To reset your password, go to the login page and click 'Forgot Password'.",
        "account": "You can view your account details on the Dashboard.",
        "transfer": "To make a transfer, visit the Transfer page and select your preferred method.",
        "card": "For card issues, you can order a new card on the Cards page.",
    }

    response = bot_responses.get("default", "Sorry, I don't understand. Can you try rephrasing your question?")
    for key, reply in bot_responses.items():
        if key in user_message:
            response = reply
            break

    return jsonify({"reply": response})

# ----- Forgot Password -----
@account_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user:
            return render_template('forgot_password.html', error="Email not found", show_bottom_nav=False)

        session['reset_user_id'] = user['id']
        return redirect('/account/reset-password')

    return render_template('forgot_password.html', show_bottom_nav=False)

# ----- Reset Password -----
@account_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    user_id = session.get('reset_user_id')
    if not user_id:
        return redirect('/account/forgot-password')

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not password or password != confirm_password:
            return render_template('reset_password.html', error="Passwords do not match", show_bottom_nav=False)

        hashed = generate_password_hash(password)
        conn = get_db_connection()
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        conn.commit()
        conn.close()

        session.pop('reset_user_id', None)
        return redirect('/account/login')

    return render_template('reset_password.html', show_bottom_nav=False)
