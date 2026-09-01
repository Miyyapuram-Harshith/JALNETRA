import httpx
import sys
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, expected_status=200, json_data=None):
    try:
        if method == "GET":
            response = httpx.get(f"{BASE_URL}{url}")
        elif method == "POST":
            response = httpx.post(f"{BASE_URL}{url}", json=json_data)
        
        if response.status_code == expected_status:
            print(f"[✓] {name}")
            return True, response.json()
        else:
            print(f"[✗] {name} (Status: {response.status_code})")
            print(f"    Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"[✗] {name} (Error: {e})")
        return False, None

def main():
    print("JALNETRA SMOKE TEST\n")
    all_passed = True
    
    # 1. API / Health / Database
    passed, data = test_endpoint("API", "GET", "/api/system/health")
    if not passed:
        all_passed = False
    elif data.get("api") != "healthy" or data.get("database") != "healthy":
        print("[✗] Database / API internal health check failed")
        all_passed = False
    else:
        print("[✓] Database")
        
    # 2. Demo data
    passed, data = test_endpoint("Demo data", "GET", "/api/regions")
    all_passed = all_passed and passed

    # 3. Risk engine
    passed, data = test_endpoint("Risk engine", "GET", "/api/risk")
    all_passed = all_passed and passed

    # 4. Propagation
    passed, data = test_endpoint("Propagation", "GET", "/api/propagation")
    all_passed = all_passed and passed

    # 5. Impact
    passed, data = test_endpoint("Impact", "GET", "/api/impact")
    all_passed = all_passed and passed

    # 6. Routes
    passed, data = test_endpoint("Routes", "GET", "/api/routes")
    all_passed = all_passed and passed

    # 7. Safe departure
    passed, data = test_endpoint("Safe departure", "GET", "/api/departure-window")
    all_passed = all_passed and passed

    # 8. Alerts
    # We can check events or trigger a demo alert
    passed, data = test_endpoint("Alerts", "GET", "/api/events")
    all_passed = all_passed and passed

    # 9. WhatsApp
    passed, data = test_endpoint("WhatsApp", "POST", "/api/demo/whatsapp")
    all_passed = all_passed and passed

    # 10. SOS
    passed, data = test_endpoint("SOS", "POST", "/api/demo/sos")
    all_passed = all_passed and passed

    # 11. Responder
    # Responder gets data from incidents
    passed, data = test_endpoint("Responder", "GET", "/api/incidents")
    all_passed = all_passed and passed

    # 12. Reset
    passed, data = test_endpoint("Reset", "POST", "/api/demo/reset")
    all_passed = all_passed and passed
    
    print()
    if all_passed:
        print("JALNETRA READY")
        sys.exit(0)
    else:
        print("TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    # check if server is up
    try:
        httpx.get(f"{BASE_URL}/api/system/health")
        main()
    except httpx.ConnectError:
        print("Backend server is not running at http://localhost:8000. Please start it with 'uvicorn app.main:app --reload'")
        sys.exit(1)
