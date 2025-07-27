from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# HELPERS

def remove_user_from_file(username):
    # Remove user info from users.txt
    with open("users.txt", "r") as file:
        lines = file.readlines() # array of strings
    
    with open("users.txt", "w") as file:
        for line in lines:
            if not line.startswith(f"{username} :"): # skips writing the line if it starts with target username
                file.write(line)


def log_user_to_file(username, raw_password):
    with open("users.txt", "a") as file:
            file.write(f"{username} : {raw_password}\n")


def create_user(username, raw_password):
    hashed_password = generate_password_hash(raw_password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    log_user_to_file(username, raw_password)


def delete_user_account(user):
    logout_user()  # Log out first for session cleanup
    db.session.delete(user)
    db.session.commit()
    remove_user_from_file(user.username)


# ROUTES


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']

        create_user(username, raw_password)

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Username or Password"
    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/delete', methods=['POST'])
@login_required
def delete():
    user = User.query.get_or_404(current_user.id)
    delete_user_account(user)
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



# NOTES
'''

Redirect: Sends the browser to a different URL  -  Clears the variables as well which is good for GET and POST requests 
Render_Template: Rends the webpage the user requested 


'''