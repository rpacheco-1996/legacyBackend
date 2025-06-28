from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import psycopg2

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Hello from Flask on Render!"

@app.route('/legacy')
def legacy():
    user_input = request.args.get('input', '')
    return f"Received input: {user_input}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
