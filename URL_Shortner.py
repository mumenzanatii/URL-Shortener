from flask import Flask, request, redirect, render_template, g
import sqlite3
import string
import random

app = Flask(__name__)
app.config['DATABASE'] = 'urls.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db


@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def generate_short_url():
    chars = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(chars) for _ in range(6))
    return short_url


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = generate_short_url()
        db = get_db()
        db.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)',
                   (original_url, short_url))
        db.commit()
        return render_template('index.html', short_url=short_url)
    else:
        return render_template('index.html')


@app.route('/<short_url>')
def redirect_to_url(short_url):
    db = get_db()
    result = db.execute(
        'SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
    original_url = result.fetchone()[0]
    return redirect(original_url)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
