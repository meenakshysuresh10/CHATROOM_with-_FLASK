from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import time

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Use a secure key in production
socketio = SocketIO(app)

# In-memory storage for messages and users
messages = []
users = {}

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Chat page route
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', messages=messages)

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username not in users:
            users[username] = True  # Mark user as logged in
            session['username'] = username  # Store username in session
            return redirect(url_for('chat'))
        else:
            return 'User already logged in', 400
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    username = session.get('username')
    if username in users:
        del users[username]  # Remove user from logged-in users
    session.pop('username', None)  # Clear session
    return redirect(url_for('login'))

# SocketIO event to handle incoming messages
@socketio.on('send_message')
def handle_message(data):
    username = data['username']
    message = data['message']
    timestamp = time.strftime('%H:%M:%S')
    messages.append({'user': username, 'message': message, 'time': timestamp})
    emit('receive_message', {'user': username, 'message': message, 'time': timestamp}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
