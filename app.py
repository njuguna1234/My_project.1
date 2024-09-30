from flask import Flask, render_template_string, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration for upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {
    "admin": generate_password_hash("password123")
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Specify custom path for your HTML files
@app.route('/')
def home():
    with open('index.html') as f:
        return render_template_string(f.read())

@app.route('/portfolio')
def portfolio():
    # List all files in the upload folder
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    with open('portfolio.html') as f:
        return render_template_string(f.read(), uploaded_files=uploaded_files)

@app.route('/booking')
def booking():
    with open('booking.html') as f:
        return render_template_string(f.read())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('upload_content'))
        else:
            flash('Invalid username or password')
    
    with open('login.html') as f:
        return render_template_string(f.read())

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_content():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect(url_for('portfolio'))  # Redirect to the portfolio page to view the uploaded work
    with open('upload.html') as f:
        return render_template_string(f.read())

@app.route('/delete_file', methods=['POST'])
@login_required
def delete_file():
    filename = request.form.get('filename')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'{filename} was successfully deleted.')
    else:
        flash(f'{filename} not found.')

    return redirect(url_for('portfolio'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
