from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import psycopg2
import random
import joblib

app = Flask(__name__)
CORS(app)

# Load the model on deploy
# No need to load this every request
legacy_model = joblib.load("models/legacy.joblib")

# Run queries in postgres
# Takes a query string as input and returns the result rows
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
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    return rows


# Hello World
@app.route('/')
def home():
    return "Hello from Flask on Render!"

'''
This is the database query endpoint it will search the database based on the keyword
the user is wanting to search for. It then selects a random response from a doctor
that was addressing a patient with a keyword related problem. It is a random
response to add variety to the POC.
'''
@app.route('/legacy')
def legacy():
    user_input = request.args.get('input', '')
    query_string = f"select response from records where '{user_input}' = ANY(keywords)"
    rows = query(query_string)
    if len(rows) > 0:
        return rows[int(random.randint(0, len(rows)))][0]
    else:
        return "No related response found"

# Get list of possible clinics for drop down
@app.route('/getClinics')
def get_clinics():
    query_string = "select distinct clinic from records order by clinic"
    rows = query(query_string)
    if len(rows) > 0:
        clinics = [row[0] for row in rows]
        return jsonify(clinics)
    else:
        return jsonify(["No clinics found"])
    
# Get list of possible doctors for drop down
@app.route('/getDoctors')
def get_doctors():
    query_string = "select distinct doctor from records order by doctor"
    rows = query(query_string)
    if len(rows) > 0:
        doctors = [row[0] for row in rows]
        return jsonify(doctors)
    else:
        return jsonify(["No doctors found"])
    
'''
This is where the model prediciton happens, it takes the age of the patient, the clinic, and the doctor
to return either True of False in regards to whether or not the doctors responses are extensive (> 100 words).
This is a simple binary classification model for the POC. I chose a random forrest because of the mix of categorical
and numerical data, as well as having seen random forests at previous companies I though it was a good option as I
wanted to do something a bit more in depth than a linear regression model.
'''
@app.route('/predict', methods=["POST"])
def predict():
    data = request.json
    model_input = pd.DataFrame([
            [data['age'], data['clinic'], data['doctor']],
        ], columns=["age", "clinic", "doctor"])
    
    result = legacy_model.predict(model_input)[0]
    if result == 0:
        return "True"
    else:
        return "False"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
