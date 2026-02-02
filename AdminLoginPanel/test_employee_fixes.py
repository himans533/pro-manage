"""
Test script to verify employee dashboard fixes
Tests:
1. GET /api/employee/tasks endpoint
2. POST /api/employee/tasks endpoint  
3. Error handling and response formats
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_employee_tasks_get():
    """Test GET /api/employee/tasks endpoint"""
    print("\n=== Testing GET /api/employee/tasks ===")
    
    # This will fail without auth, but should return JSON error, not crash
    response = requests.get(f"{API_BASE}/employee/tasks")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Check that it returns JSON even on error
    try:
        data = response.json()
        print("✓ Returns valid JSON")
        if "error" in data:
            print(f"✓ Error message: {data['error']}")
    except json.JSONDecodeError:
        print("✗ FAILED: Did not return valid JSON")
        return False
    
    return True

def test_employee_tasks_post():
    """Test POST /api/employee/tasks endpoint"""
    print("\n=== Testing POST /api/employee/tasks ===")
    
    # This will fail without auth, but should return JSON error, not crash
    response = requests.post(
        f"{API_BASE}/employee/tasks",
        json={"title": "Test Task", "project_id": 1}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Check that it returns JSON even on error
    try:
        data = response.json()
        print("✓ Returns valid JSON")
        if "error" in data:
            print(f"✓ Error message: {data['error']}")
    except json.JSONDecodeError:
        print("✗ FAILED: Did not return valid JSON")
        return False
    
    return True

def test_health_check():
    """Test basic health endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Server is running")
            return True
    except requests.exceptions.ConnectionError:
        print("✗ FAILED: Cannot connect to server. Is it running?")
        return False
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("Employee Dashboard API Tests")
    print("=" * 60)
    
    # Test if server is running
    if not test_health_check():
        print("\n⚠ Server is not running. Start the Flask app first:")
        print("  python app.py")
        exit(1)
    
    # Run tests
    results = []
    results.append(("GET /api/employee/tasks", test_employee_tasks_get()))
    results.append(("POST /api/employee/tasks", test_employee_tasks_post()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠ Some tests failed. Check the output above.")
