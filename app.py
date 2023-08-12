from flask import Flask, render_template, request
from password_checker import pwned_api_check
import sqlite3
import os


app = Flask(__name__, static_url_path='/static')

# Ensure the database file exists
db_file = 'passwords.db'

if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, password TEXT)''')
    conn.commit()
    conn.close()


def save_password(password):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Check if the password already exists in the database
    c.execute('SELECT * FROM passwords WHERE password = ?', (password,))
    existing_password = c.fetchone()

    if existing_password:
        print(f"Password '{password}' already exists in the database.")
    else:
        c.execute('INSERT INTO passwords (password) VALUES (?)', (password,))
        print(f"Password '{password}' added to the database.")

    conn.commit()
    conn.close()


def get_visit_count():
    try:
        with open('visit_count.txt', 'r') as f:
            return int(f.read())
    except (IOError, ValueError):
        return 0

def increment_visit_count():
    count = get_visit_count()
    count += 1
    with open('visit_count.txt', 'w') as f:
        f.write(str(count))


@app.route('/author', methods=['GET'])
def author():
    return render_template('author.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        password = request.form['password']
        count = pwned_api_check(password)
        if count:
            result = f'{password} was found {count} times... you should probably change your password!'
        else:
            result = f'{password} was NOT found. Carry on!'
        save_password(password)  # Save the password in the database
    increment_visit_count()
    visit_count = get_visit_count()
    return render_template('index.html', result=result, visit_count=visit_count)

if __name__ == '__main__':
    app.run(debug=True)

