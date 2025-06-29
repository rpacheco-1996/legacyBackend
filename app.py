from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import psycopg2
import random

app = Flask(__name__)
CORS(app)

def query(query):
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

    cursor.execute(query, (True,))
    # Fetch all rows from the executed query
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    return rows


@app.route('/')
def home():
    return "Hello from Flask on Render!"

@app.route('/legacy')
def legacy():
    user_input = request.args.get('input', '')
    query_string = f"select response from records where '{user_input}' = ANY(keywords)"
    rows = query(query_string)
    if len(rows) > 0:
        return rows[int(random.randint(0, len(rows)))][0]
    else:
        return "No related response found"

@app.route('/getClinics')
def get_clinics():
    query_string = "select distinct clinic from records order by clinic"
    rows = query(query_string)
    if len(rows) > 0:
        clinics = [row[0] for row in rows]
        return jsonify(clinics)
    else:
        return jsonify(["No clinics found"])
    
@app.route('/getDoctors')
def get_doctors():
    query_string = "select distinct doctor from records order by doctor"
    rows = query(query_string)
    if len(rows) > 0:
        doctors = [row[0] for row in rows]
        return jsonify(doctors)
    else:
        return jsonify(["No doctors found"])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
