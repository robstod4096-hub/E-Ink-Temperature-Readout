from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def get_24hr_data():
    conn = sqlite3.connect('climate_data.db')
    cursor = conn.cursor()
    # Query logs from the last 24 hours only
    cursor.execute('''
        SELECT timestamp, temperature, humidity, outdoor_temp 
        FROM readings 
        WHERE timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "labels": [row[0] for row in rows],
        "temperatures": [row[1] for row in rows],
        "humidities": [row[2] for row in rows],
        "outdoor_temps": [row[3] for row in rows]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    return jsonify(get_24hr_data())

if __name__ == '__main__':
    # host='0.0.0.0' exposes the web server to your entire local network
    app.run(host='0.0.0.0', port=5000)