#!/usr/bin/env python
"""
Launch FastAPI server with public ngrok tunnel
Accessible from anywhere!
"""

import subprocess
import time
import os
import sys
from pyngrok import ngrok
import requests

def start_api_server():
    """Start FastAPI server in background"""
    print("[1] Starting FastAPI server on http://localhost:8000...")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Set environment variables
    env = os.environ.copy()
    env['MODEL_PATH'] = 'src/models/model.pkl'
    env['CONFIG_PATH'] = 'data/processed/preprocess_config.json'
    
    # Start uvicorn
    process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'src.app.main:app', '--host', '0.0.0.0', '--port', '8000'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✓ FastAPI server started successfully!")
            return process
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        process.terminate()
        sys.exit(1)

def create_public_tunnel():
    """Create public ngrok tunnel"""
    print("\n[2] Creating public ngrok tunnel...")
    
    try:
        # Create tunnel to localhost:8000
        public_url = ngrok.connect(8000, "http")
        print(f"✓ Public tunnel created!")
        print(f"\n" + "=" * 80)
        print(f"PUBLIC API URL: {public_url}")
        print(f"=" * 80)
        
        return public_url
    except Exception as e:
        print(f"✗ Failed to create tunnel: {e}")
        print("Note: ngrok requires an account. Sign up at https://ngrok.com")
        sys.exit(1)

def test_public_endpoint(public_url):
    """Test public endpoint"""
    print(f"\n[3] Testing public endpoint...")
    
    try:
        response = requests.get(f"{public_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✓ Public endpoint is working!")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Endpoint returned status code: {response.status_code}")
    except Exception as e:
        print(f"✗ Failed to test endpoint: {e}")

def print_usage(public_url):
    """Print usage instructions"""
    print(f"\n" + "=" * 80)
    print("API ENDPOINTS (Publicly Accessible)")
    print("=" * 80)
    
    endpoints = [
        ("Health Check", f"GET {public_url}/health"),
        ("Model Info", f"GET {public_url}/info"),
        ("Single Prediction", f"POST {public_url}/predict"),
        ("Batch Prediction", f"POST {public_url}/batch_predict"),
        ("Two-Stage (RF+Hungarian)", f"POST {public_url}/predict_and_assign"),
    ]
    
    for name, endpoint in endpoints:
        print(f"\n{name}:")
        print(f"  {endpoint}")
    
    print(f"\n" + "=" * 80)
    print("EXAMPLE CURL COMMANDS")
    print("=" * 80)
    
    print(f"\n1. Health Check:")
    print(f"   curl {public_url}/health")
    
    print(f"\n2. Single Prediction:")
    print(f'''   curl -X POST {public_url}/predict \\
     -H "Content-Type: application/json" \\
     -d '{{
       "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
       "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
       "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
     }}'
    ''')
    
    print(f"\n3. Full Two-Stage Pipeline:")
    print(f'''   curl -X POST {public_url}/predict_and_assign \\
     -H "Content-Type: application/json" \\
     -d '{{
       "samples": [
         {{"age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0, "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0, "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0}},
         {{"age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0, "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0, "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0}}
       ],
       "n_tasks": 2,
       "maximize_assignment": true
     }}'
    ''')
    
    print(f"\n" + "=" * 80)
    print("PYTHON TEST CODE")
    print("=" * 80)
    print(f'''
import requests

# Test health endpoint
response = requests.get('{public_url}/health')
print(response.json())

# Single prediction
sample = {{
    "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
    "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
    "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
}}
response = requests.post('{public_url}/predict', json=sample)
print(response.json())
    ''')
    
    print(f"\n" + "=" * 80)
    print("⚠️  IMPORTANT:")
    print("=" * 80)
    print("- Keep this terminal open to maintain the public tunnel")
    print("- Press Ctrl+C to stop the server and close the tunnel")
    print("- Each ngrok session has a limited duration (free tier: 2 hours)")
    print("- The public URL changes each time you restart")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    print("=" * 80)
    print("TWO-STAGE ML API - PUBLIC DEPLOYMENT")
    print("=" * 80)
    
    # Start API server
    api_process = start_api_server()
    
    # Create public tunnel
    public_url = create_public_tunnel()
    
    # Test public endpoint
    test_public_endpoint(public_url)
    
    # Print usage
    print_usage(public_url)
    
    # Keep running
    try:
        print("Server and tunnel running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        api_process.terminate()
        ngrok.kill()
        print("✓ Server stopped")
