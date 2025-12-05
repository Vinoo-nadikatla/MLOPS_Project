#!/usr/bin/env python
"""Test the two-stage model API with sample predictions"""

import requests
import json
import time

API_BASE = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing /health endpoint ===")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_single_prediction():
    """Test single prediction (Stage 1 only)"""
    print("\n=== Testing /predict endpoint (Stage 1: RF only) ===")
    sample = {
        "age": 45.0,
        "sex": 1.0,
        "cp": 3.0,
        "trestbps": 130.0,
        "chol": 250.0,
        "fbs": 0.0,
        "restecg": 1.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 2.6,
        "slope": 0.0,
        "ca": 0.0,
        "thal": 0.0
    }
    response = requests.post(f"{API_BASE}/predict", json=sample)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_batch_prediction():
    """Test batch predictions"""
    print("\n=== Testing /batch_predict endpoint ===")
    batch = {
        "samples": [
            {
                "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
                "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
                "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
            },
            {
                "age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0,
                "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0,
                "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0
            }
        ]
    }
    response = requests.post(f"{API_BASE}/batch_predict", json=batch)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_predict_and_assign():
    """Test full two-stage pipeline with Hungarian assignment"""
    print("\n=== Testing /predict_and_assign endpoint (Two-Stage Pipeline) ===")
    batch = {
        "samples": [
            {
                "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
                "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
                "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
            },
            {
                "age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0,
                "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0,
                "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0
            },
            {
                "age": 50.0, "sex": 1.0, "cp": 2.0, "trestbps": 140.0,
                "chol": 280.0, "fbs": 1.0, "restecg": 2.0, "thalach": 140.0,
                "exang": 1.0, "oldpeak": 4.2, "slope": 2.0, "ca": 3.0, "thal": 3.0
            }
        ],
        "n_tasks": 3,
        "maximize_assignment": True
    }
    response = requests.post(f"{API_BASE}/predict_and_assign", json=batch)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response:\n")
    print(f"  Predictions (Stage 1): {result.get('stage_1_rf_predictions')}")
    print(f"  Probabilities: {[f'{p:.4f}' for p in result.get('stage_1_probabilities', [])]}")
    print(f"  Optimal Assignments (Stage 2 - Hungarian):\n    {result.get('stage_2_optimal_assignments')}")
    print(f"  Total Assignment Score: {result.get('stage_2_total_score'):.4f}")


def test_model_info():
    """Test model info endpoint"""
    print("\n=== Testing /info endpoint ===")
    response = requests.get(f"{API_BASE}/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


# New Tests Added Below

def test_invalid_prediction():
    """Test for invalid input (e.g., missing or incorrect field types)"""
    print("\n=== Testing /predict endpoint with invalid input ===")
    invalid_sample = {
        "age": "invalid",  # This should be a float
        "sex": 1.0,
        "cp": 3.0,
        "trestbps": 130.0,
        "chol": 250.0,
        "fbs": 0.0,
        "restecg": 1.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 2.6,
        "slope": 0.0,
        "ca": 0.0,
        "thal": 0.0
    }
    response = requests.post(f"{API_BASE}/predict", json=invalid_sample)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_edge_case_prediction():
    """Test for edge case input (e.g., extreme values or missing fields)"""
    print("\n=== Testing /predict endpoint with edge case input ===")
    edge_case_sample = {
        "age": 0.0,  # Lower boundary for age
        "sex": 1.0,
        "cp": 3.0,
        "trestbps": 300.0,  # Extreme value for blood pressure
        "chol": 600.0,  # Extremely high cholesterol
        "fbs": 0.0,
        "restecg": 1.0,
        "thalach": 220.0,  # Very high heart rate
        "exang": 0.0,
        "oldpeak": 5.0,
        "slope": 0.0,
        "ca": 3.0,  # Maximum value for ca
        "thal": 3.0
    }
    response = requests.post(f"{API_BASE}/predict", json=edge_case_sample)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_prediction_performance():
    """Test performance by measuring response time"""
    print("\n=== Testing /predict endpoint performance ===")
    sample = {
        "age": 45.0,
        "sex": 1.0,
        "cp": 3.0,
        "trestbps": 130.0,
        "chol": 250.0,
        "fbs": 0.0,
        "restecg": 1.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 2.6,
        "slope": 0.0,
        "ca": 0.0,
        "thal": 0.0
    }
    start_time = time.time()
    response = requests.post(f"{API_BASE}/predict", json=sample)
    end_time = time.time()
    response_time = end_time - start_time
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Response Time: {response_time:.4f} seconds")


def test_invalid_endpoint():
    """Test for invalid API endpoint"""
    print("\n=== Testing invalid endpoint ===")
    response = requests.get(f"{API_BASE}/invalid_endpoint")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("=" * 80)
    print("TWO-STAGE MODEL API TEST")
    print("=" * 80)

    try:
        test_health()
        test_model_info()
        test_single_prediction()
        test_batch_prediction()
        test_predict_and_assign()
        test_invalid_prediction()  # Newly added test
        test_edge_case_prediction()  # Newly added test
        test_prediction_performance()  # Newly added test
        test_invalid_endpoint()  # Newly added test

        print("\n" + "=" * 80)
        print("✓ All tests completed successfully!")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print(f"✗ ERROR: Cannot connect to API at {API_BASE}")
        print("Make sure the API is running: uvicorn src.app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"✗ ERROR: {e}")

