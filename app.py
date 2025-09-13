from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime

db_config = {
    'host': 'localhost',
    'database': 'flask_db',
    'user': 'root',
    'password': 'root'
}

app = Flask(__name__)
app.secret_key = '1234'

# database se connect karne ke liye function
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("✅ Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    connection = get_db_connection()
    if connection:
        connection.close()
        return render_template('index.html')
    else:
        return "Database connection failed!"

# ye signup page hai jismei hum jo data dalenge vo database mei jayenge
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO user (username, password, created_at) VALUES (%s, %s, %s)",
                (username, password, current_time)
            )
            connection.commit()
            return redirect(url_for('signin'))
        except Error as e:
            return f"Database error: {e}"
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT password FROM user WHERE username=%s",
                (username,)
            )
            user = cursor.fetchone()

            if user and user[0] == password:
                session['username'] = username
                return redirect(url_for('dashboard_home'))
            else:
                return "Invalid username or password!"

        except Error as e:
            return f"Database error: {e}"
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()

    return render_template('signin.html')

@app.route('/dashboard_home')
def dashboard_home():
    if 'username' in session:
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)  # dict form me data milega

            cursor.execute("SELECT id, username, created_at FROM user")
            users = cursor.fetchall()

            return render_template('dashboard_home.html', users=users, username=session['username'])
        except Error as e:
            return f"Database error: {e}"
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection:
                connection.close()
    else:
        return redirect(url_for('signin'))


@app.route('/dashboard_about')
def dashboard_about():
    if 'username' in session:
        return render_template('dashboard_about.html', username=session['username'])
    else:
        return redirect(url_for('signin'))

@app.route('/dashboard_contact')
def dashboard_contact():
    if 'username' in session:
        return render_template('dashboard_contact.html', username=session['username'])
    else:
        return redirect(url_for('signin'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)