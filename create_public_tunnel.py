#!/usr/bin/env python
"""Create public ngrok tunnel to local FastAPI server"""

import time
import requests
from pyngrok import ngrok

print("=" * 80)
print("CREATING PUBLIC TUNNEL TO TWO-STAGE ML API")
print("=" * 80)

# Check if server is running
print("\n[1] Checking if FastAPI server is running...")
for i in range(5):
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            print("✓ FastAPI server is running and responding!")
            break
    except:
        if i < 4:
            print(f"   Waiting... ({i+1}/5)")
            time.sleep(2)
        else:
            print("✗ Server not responding. Make sure uvicorn is running:")
            print("   cd D:\\Brajesh\\GitHubDsktop\\MLOPS_Project")
            print("   $env:MODEL_PATH = 'src/models/model.pkl'")
            print("   $env:CONFIG_PATH = 'data/processed/preprocess_config.json'")
            print("   .venv\\Scripts\\uvicorn.exe src.app.main:app --host 0.0.0.0 --port 8000")
            exit(1)

# Create tunnel
print("\n[2] Creating public ngrok tunnel...")
try:
    public_url = ngrok.connect(8000, "http")
    print(f"✓ Public tunnel created!")
except Exception as e:
    print(f"✗ Failed to create tunnel: {e}")
    print("\nTo use ngrok, you need to:")
    print("1. Sign up at https://ngrok.com (free)")
    print("2. Get your auth token from https://dashboard.ngrok.com/auth")
    print("3. Run: ngrok config add-authtoken <your-token>")
    exit(1)

# Test public endpoint
print(f"\n[3] Testing public endpoint...")
try:
    response = requests.get(f"{public_url}/health", timeout=10)
    if response.status_code == 200:
        print(f"✓ Public endpoint is working!")
        health_data = response.json()
        print(f"   Status: {health_data.get('status')}")
        print(f"   Model Loaded: {health_data.get('model_loaded')}")
except Exception as e:
    print(f"✗ Failed to test endpoint: {e}")

# Print info
print("\n" + "=" * 80)
print("✅ PUBLIC API IS NOW ACCESSIBLE")
print("=" * 80)
print(f"\n🌐 PUBLIC URL: {public_url}")
print("\n" + "=" * 80)
print("API ENDPOINTS")
print("=" * 80)

endpoints = {
    "Health Check": f"GET {public_url}/health",
    "Model Info": f"GET {public_url}/info",
    "Single Prediction": f"POST {public_url}/predict",
    "Batch Prediction": f"POST {public_url}/batch_predict",
    "Two-Stage Pipeline (RF+Hungarian)": f"POST {public_url}/predict_and_assign",
}

for name, endpoint in endpoints.items():
    print(f"\n{name}:")
    print(f"  {endpoint}")

print("\n" + "=" * 80)
print("QUICK TEST COMMANDS")
print("=" * 80)

print(f"\n1️⃣  Health Check (PowerShell):")
print(f'   Invoke-WebRequest -Uri "{public_url}/health" | Select-Object -ExpandProperty Content')

print(f"\n2️⃣  Model Info:")
print(f'   Invoke-WebRequest -Uri "{public_url}/info" | Select-Object -ExpandProperty Content')

print(f"\n3️⃣  Single Prediction (PowerShell):")
print(f'''   $sample = @{{
     age = 45.0; sex = 1.0; cp = 3.0; trestbps = 130.0
     chol = 250.0; fbs = 0.0; restecg = 1.0; thalach = 150.0
     exang = 0.0; oldpeak = 2.6; slope = 0.0; ca = 0.0; thal = 0.0
   }} | ConvertTo-Json
   
   Invoke-WebRequest -Uri "{public_url}/predict" `
     -Method Post -ContentType "application/json" `
     -Body $sample | Select-Object -ExpandProperty Content
''')

print(f"\n4️⃣  Python Test:")
print(f'''   import requests
   r = requests.get('{public_url}/health')
   print(r.json())
''')

print("\n" + "=" * 80)
print("⚠️  IMPORTANT")
print("=" * 80)
print("• Keep this script running to maintain the public tunnel")
print("• Press Ctrl+C to close")
print("• Each ngrok session lasts ~2 hours (free tier)")
print("• Public URL changes each time you restart")
print("• Do NOT share ngrok URLs with sensitive data")
print("=" * 80 + "\n")

try:
    print("Tunnel active. Press Ctrl+C to stop...\n")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nClosing tunnel...")
    ngrok.kill()
    print("✓ Tunnel closed")
