#!/usr/bin/env python
"""
Complete Public API Setup
- Starts FastAPI server
- Creates ngrok tunnel
- Provides public URL and usage examples
"""

import subprocess
import time
import sys
import os
import signal
import requests
from pyngrok import ngrok

# Global process handle
server_process = None

def start_server():
    """Start FastAPI server"""
    global server_process
    
    print("[1] Starting FastAPI server on port 8000...")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    env = os.environ.copy()
    env['MODEL_PATH'] = 'src/models/model.pkl'
    env['CONFIG_PATH'] = 'data/processed/preprocess_config.json'
    
    # Start server without reload
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'src.app.main:app',
        '--host', '0.0.0.0',
        '--port', '8000'
    ]
    
    server_process = subprocess.Popen(cmd, env=env)
    
    # Wait for server to be ready
    for attempt in range(10):
        time.sleep(1)
        try:
            response = requests.get('http://localhost:8000/health', timeout=2)
            if response.status_code == 200:
                print("✓ FastAPI server is running!\n")
                return True
        except:
            pass
    
    print("✗ Server failed to start")
    return False

def create_tunnel():
    """Create ngrok tunnel"""
    print("[2] Creating public ngrok tunnel...")
    
    try:
        public_url = ngrok.connect(8000, "http")
        print(f"✓ Public tunnel created!\n")
        return str(public_url)
    except Exception as e:
        print(f"✗ Failed to create tunnel: {e}")
        print("\nSetup ngrok:")
        print("1. Sign up: https://ngrok.com")
        print("2. Get token: https://dashboard.ngrok.com/auth")
        print(f"3. Run: ngrok config add-authtoken <TOKEN>")
        return None

def test_endpoint(url):
    """Test public endpoint"""
    print(f"[3] Testing public endpoint...")
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Public endpoint is accessible!\n")
            return True
    except Exception as e:
        print(f"✗ Test failed: {e}\n")
    return False

def print_info(public_url):
    """Print usage information"""
    print("=" * 90)
    print("🚀 TWO-STAGE ML API IS NOW PUBLIC")
    print("=" * 90)
    
    print(f"\n🌐 PUBLIC URL: {public_url}")
    print(f"📍 Local URL: http://localhost:8000")
    
    print("\n" + "-" * 90)
    print("ENDPOINTS")
    print("-" * 90)
    
    endpoints = [
        ("Health", f"GET {public_url}/health"),
        ("Info", f"GET {public_url}/info"),
        ("Predict (Stage 1)", f"POST {public_url}/predict"),
        ("Batch Predict", f"POST {public_url}/batch_predict"),
        ("Two-Stage (RF+Hungarian)", f"POST {public_url}/predict_and_assign"),
    ]
    
    for name, cmd in endpoints:
        print(f"  {name:25} {cmd}")
    
    print("\n" + "-" * 90)
    print("QUICK TEST (PowerShell)")
    print("-" * 90)
    
    print(f"\n# Health check")
    print(f'Invoke-WebRequest "{public_url}/health"')
    
    print(f"\n# Test prediction:")
    print(f'''$body = @{{
  age = 45.0; sex = 1.0; cp = 3.0; trestbps = 130.0
  chol = 250.0; fbs = 0.0; restecg = 1.0; thalach = 150.0
  exang = 0.0; oldpeak = 2.6; slope = 0.0; ca = 0.0; thal = 0.0
}} | ConvertTo-Json

Invoke-WebRequest -Uri "{public_url}/predict" -Method Post `
  -ContentType "application/json" -Body $body
''')
    
    print(f"\n" + "-" * 90)
    print("PYTHON TEST")
    print("-" * 90)
    
    print(f'''
import requests

# Health
print(requests.get('{public_url}/health').json())

# Prediction
sample = {{
  "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
  "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
  "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
}}
print(requests.post('{public_url}/predict', json=sample).json())
    ''')
    
    print("\n" + "=" * 90)
    print("⚠️  NOTES")
    print("=" * 90)
    print("• Server is running: keep this window open")
    print("• Press Ctrl+C to stop")
    print("• Public URL expires after ~2 hours (ngrok free tier)")
    print("• New URL each restart")
    print("=" * 90 + "\n")

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\n\nShutting down...")
    if server_process:
        server_process.terminate()
        server_process.wait()
    ngrok.kill()
    print("✓ Stopped")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "=" * 90)
    print("PUBLIC API SETUP")
    print("=" * 90 + "\n")
    
    # Start server
    if not start_server():
        sys.exit(1)
    
    # Create tunnel
    public_url = create_tunnel()
    if not public_url:
        if server_process:
            server_process.terminate()
        sys.exit(1)
    
    # Test
    test_endpoint(public_url)
    
    # Print info
    print_info(public_url)
    
    # Keep running
    print("Running... Press Ctrl+C to stop\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
