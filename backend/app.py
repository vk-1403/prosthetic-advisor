from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load ML artifacts (dummy models for initial setup)
try:
    model = joblib.load('prosthetic_model.joblib')
    le = joblib.load('label_encoder.joblib')
except:
    print("Using fallback models")
    model = None
    le = None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        input_data = {
            'ambulation': data.get('ambulation', 'single-speed'),
            'stability': data.get('stability', 'stable'),
            'risk': data.get('risk', 'low')
        }
        
        # Fallback recommendations
        fallback_response = {
            'recommendation': 'ESAR Foot',
            'confidence': 0.85
        }
        
        return jsonify(fallback_response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/collect-data', methods=['POST'])
def collect_data():
    try:
        data = request.json
        timestamp = datetime.now().isoformat()
        
        # Save to CSV (dummy implementation)
        with open('training_data.csv', 'a') as f:
            f.write(f"{timestamp},{data.get('age')},{data.get('gender')}\n")
            
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)