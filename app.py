from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import psycopg2

app = Flask(__name__)
CORS(app)

def query(keyword):
    DB_NAME = "legacy_pacheco"
    DB_USER = "rpacheco"
    DB_PASSWORD = "D1qoGvjXqPTd2vB4i4KS71xDEWmCOpSq"
    DB_HOST = "dpg-d1ff63mmcj7s739p963g-a.oregon-postgres.render.com"
    DB_PORT = "5432"

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
    )
    cursor = conn.cursor()

    query = f"select response from records where '{keyword}' = ANY(keywords)"

    cursor.execute(query, (True,))
    # Fetch all rows from the executed query
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    if len(rows) > 0:
        return rows[0][0]
    else:
        return "No related response found"


@app.route('/')
def home():
    return "Hello from Flask on Render!"

@app.route('/legacy')
def legacy():
    user_input = request.args.get('input', '')
    response = query(user_input)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
