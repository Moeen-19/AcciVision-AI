from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_bcrypt import Bcrypt
import os, json
import secrets

from models import db, User  # Import from models.py

app = Flask(__name__, static_folder='snapshots')
app.secret_key = secrets.token_urlsafe(32)  # CHANGE THIS TO SOMETHING RANDOM

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)
bcrypt = Bcrypt(app)

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------- Routes --------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(username=username, password=hashed_pw, is_approved=False)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Awaiting admin approval.')
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            if not user.is_admin and not user.is_approved:
                flash('Your account is pending admin approval.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/admin/approve_users')
@login_required
def approve_users():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('dashboard'))

    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template('approve_users.html', users=pending_users)

@app.route('/admin/analytics')
@login_required
def analytics():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('dashboard'))
    return render_template('analytics.html')

@app.route('/admin/approve/<int:user_id>')
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f"{user.username} approved.")
    return redirect(url_for('approve_users'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    events = []
    log_path = "logs/events.json"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            events = json.load(f)
    events = sorted(events, key=lambda x: x["timestamp"], reverse=True)
    return render_template(
        "dashboard.html",
        events=events,
        username=current_user.username,
        is_admin=current_user.is_admin
    )
@app.route('/feedback', methods=['POST'])
@login_required
def handle_feedback():
    data = request.get_json()
    snapshot = data.get("snapshot")
    feedback = data.get("feedback")  # "correct" or "false_positive"

    # Convert snapshot filename to clip filename
    clip_name = snapshot.replace(".jpg", ".npy")

    # Paths
    accident_path = f"dataset/preprocessed/accident/{clip_name}"
    normal_path = f"dataset/preprocessed/normal/{clip_name}"

    # Move the clip if feedback is false_positive
    if feedback == "false_positive":
        if os.path.exists(accident_path):
            os.rename(accident_path, normal_path)
            print(f"🔁 Moved clip: {clip_name} (accident ➝ normal)")
        else:
            print(f"⚠️ Clip not found: {clip_name}")

    return {"status": "success"}

# -------------------- Run App --------------------#

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # ✅ Hardcoded admin creation
        admin_username = "admin"
        admin_password = "admin123"  # Change to something strong

        from models import User

        existing_admin = User.query.filter_by(username=admin_username).first()
        if not existing_admin:
            hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            admin = User(username=admin_username, password=hashed_pw, is_admin=True, is_approved=True)
            db.session.add(admin)
            db.session.commit()
           
    app.run(host="0.0.0.0", port=5000, debug=True)

