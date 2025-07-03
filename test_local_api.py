#!/usr/bin/env python3
"""
Test script for the local document extraction API.

This script tests the local FastAPI server to ensure it's working correctly.
Run this after starting the server with `python run_locally.py`.

Usage:
    python test_local_api.py
"""

import json
import time
import requests
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure the server is running on http://localhost:8000")
        return False


def test_config_endpoint():
    """Test the configuration endpoint."""
    print("🔍 Testing configuration endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuration retrieved:")
            for key, value in data.items():
                if "error" not in key:
                    print(f"   {key}: {value}")
                else:
                    print(f"   ❌ {key}: {value}")
            return True
        else:
            print(f"❌ Configuration check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Configuration check failed: {e}")
        return False


def test_extract_endpoint_validation():
    """Test the extract endpoint with invalid input."""
    print("🔍 Testing extract endpoint validation...")
    
    try:
        # Test with missing path
        response = requests.post(
            f"{BASE_URL}/extract",
            json={},
            timeout=5
        )
        
        if response.status_code == 422:  # Validation error
            print("✅ Input validation working correctly")
            return True
        else:
            print(f"❌ Expected validation error (422), got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Extract endpoint validation test failed: {e}")
        return False


def test_extract_endpoint_with_fake_path():
    """Test the extract endpoint with a fake path (should fail gracefully)."""
    print("🔍 Testing extract endpoint with fake path...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/extract",
            json={"path": "fake/document.pdf"},
            timeout=10
        )
        
        # Should return an error response but with proper structure
        if response.status_code in [404, 500]:
            data = response.json()
            if "success" in data and data["success"] is False:
                print("✅ Extract endpoint handles errors correctly")
                print(f"   Error: {data.get('message', 'No message')}")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ Expected error status, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Extract endpoint test failed: {e}")
        return False


def test_lambda_format_endpoint():
    """Test the Lambda format endpoint."""
    print("🔍 Testing Lambda format endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/extract-lambda",
            json={"path": "fake/document.pdf"},
            timeout=10
        )
        
        # Should return a response (error in this case)
        if response.status_code == 200:
            data = response.json()
            if "success" in data:
                print("✅ Lambda format endpoint working")
                if not data["success"]:
                    print(f"   Expected error for fake path: {data.get('message', 'No message')}")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ Lambda format endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Lambda format endpoint test failed: {e}")
        return False


def run_all_tests():
    """Run all test functions."""
    print("🚀 Starting API tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Configuration", test_config_endpoint),
        ("Input Validation", test_extract_endpoint_validation),
        ("Extract Endpoint", test_extract_endpoint_with_fake_path),
        ("Lambda Format", test_lambda_format_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        start_time = time.time()
        success = test_func()
        duration = time.time() - start_time
        
        results.append((test_name, success, duration))
        
        if success:
            print(f"✅ {test_name} completed in {duration:.2f}s")
        else:
            print(f"❌ {test_name} failed after {duration:.2f}s")
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("-" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success, duration in results:
        status = "PASS" if success else "FAIL"
        print(f"{status:>6} | {test_name:<20} | {duration:>6.2f}s")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False


if __name__ == "__main__":
    print("🧪 Document Extraction API Test Suite")
    print("Make sure the server is running with: python run_locally.py")
    print()
    
    # Give user a chance to start the server
    try:
        input("Press Enter when the server is running (or Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\n👋 Test cancelled.")
        exit(0)
    
    success = run_all_tests()
    
    if success:
        print("\n🔧 Next steps:")
        print("1. Try the interactive docs at http://localhost:8000/docs")
        print("2. Test with real S3 document paths")
        print("3. Check the server logs for detailed information")
    else:
        print("\n🛠️  Troubleshooting:")
        print("1. Make sure all environment variables are set correctly")
        print("2. Check AWS credentials and S3 bucket permissions")
        print("3. Verify the server is running and accessible")
        print("4. Check the server logs for detailed error information")
