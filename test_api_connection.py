"""
Rahalah Trip Planning Assistant - API Connection Test
This script tests the connection between the frontend and backend API.
"""
import json
import requests
import time
from typing import Dict, Any, List, Optional
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Configuration
API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

def print_header(message: str) -> None:
    """Print a formatted header message.
    
    Args:
        message: The message to print
    """
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{message.center(80)}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")

def print_success(message: str) -> None:
    """Print a success message.
    
    Args:
        message: The message to print
    """
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message: str) -> None:
    """Print an error message.
    
    Args:
        message: The message to print
    """
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message: str) -> None:
    """Print an info message.
    
    Args:
        message: The message to print
    """
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")

def print_json(data: Dict[str, Any]) -> None:
    """Print formatted JSON data.
    
    Args:
        data: The data to print
    """
    json_str = json.dumps(data, indent=2)
    print(f"{Fore.MAGENTA}{json_str}{Style.RESET_ALL}")

def test_health_check() -> bool:
    """Test the health check endpoint.
    
    Returns:
        True if the test passes, False otherwise
    """
    print_header("Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check successful: {data}")
            return True
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Error during health check: {str(e)}")
        return False

def test_chat_api(mode: str, message: str, expected_results_key: Optional[str] = None) -> bool:
    """Test the chat API endpoint with a specific mode.
    
    Args:
        mode: The mode to test (flight, hotel, trip)
        message: The message to send
        expected_results_key: The expected key in search_results (if any)
        
    Returns:
        True if the test passes, False otherwise
    """
    print_header(f"Testing {mode.upper()} Mode")
    print_info(f"Sending message: '{message}'")
    
    try:
        payload = {
            "message": message,
            "mode": mode,
            "session_id": ""  # Empty string instead of None
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print_info(f"Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for expected fields
            if "response" in data:
                print_success(f"Response: {data['response']}")
            else:
                print_error("Missing 'response' field in API response")
                return False
            
            if "session_id" in data:
                print_success(f"Session ID: {data['session_id']}")
            else:
                print_error("Missing 'session_id' field in API response")
                return False
            
            if "mode" in data:
                print_success(f"Mode: {data['mode']}")
            else:
                print_error("Missing 'mode' field in API response")
                return False
            
            if "search_results" in data:
                if expected_results_key and expected_results_key in data["search_results"]:
                    results = data["search_results"][expected_results_key]
                    print_success(f"Found {len(results)} {expected_results_key} results")
                    print_info(f"First result preview:")
                    
                    if results:
                        first_result = results[0]
                        print_json(first_result)
                else:
                    print_info("Search results:")
                    print_json(data["search_results"])
            else:
                print_error("Missing 'search_results' field in API response")
                return False
            
            return True
        else:
            print_error(f"API request failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Error during API request: {str(e)}")
        return False

def test_frontend_connection() -> bool:
    """Test the connection to the Streamlit frontend.
    
    Returns:
        True if the test passes, False otherwise
    """
    print_header("Testing Frontend Connection")
    
    try:
        response = requests.get(FRONTEND_URL)
        
        if response.status_code == 200:
            print_success(f"Frontend connection successful")
            return True
        else:
            print_error(f"Frontend connection failed with status code: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Error connecting to frontend: {str(e)}")
        return False

def run_all_tests() -> None:
    """Run all connection tests."""
    print_header("RAHALAH TRIP PLANNING ASSISTANT - API CONNECTION TEST")
    
    tests = [
        {"name": "Health Check", "function": test_health_check, "args": []},
        {"name": "Flight Mode", "function": test_chat_api, "args": ["flight", "Find flights from Riyadh to Jeddah", "flight"]},
        {"name": "Hotel Mode", "function": test_chat_api, "args": ["hotel", "Find hotels in Mecca", "hotel"]},
        {"name": "Trip Mode", "function": test_chat_api, "args": ["trip", "Plan a trip to Riyadh", None]},
        {"name": "Frontend Connection", "function": test_frontend_connection, "args": []}
    ]
    
    results = {}
    
    for test in tests:
        print("\n" + "-" * 80)
        print_info(f"Running test: {test['name']}")
        result = test["function"](*test["args"])
        results[test["name"]] = result
    
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}TEST SUMMARY".center(80))
    print("=" * 80)
    
    all_passed = True
    for name, result in results.items():
        if result:
            print(f"{Fore.GREEN}✓ {name}: PASSED{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {name}: FAILED{Style.RESET_ALL}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print(f"{Fore.GREEN}ALL TESTS PASSED! Frontend and Backend are properly connected.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}SOME TESTS FAILED. Please check the errors above.{Style.RESET_ALL}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_all_tests()
