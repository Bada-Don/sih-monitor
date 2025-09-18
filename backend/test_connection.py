#!/usr/bin/env python3
"""
Test script to check SIH website connectivity and troubleshoot 403 errors
"""

import requests
import time
import random
from sih_monitor import SIHSubmissionMonitor

def test_basic_connection():
    """Test basic connection to SIH website"""
    url = "https://sih.gov.in/sih2025PS"
    
    print("Testing basic connection...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Basic connection failed: {e}")
        return False

def test_with_headers():
    """Test connection with browser-like headers"""
    url = "https://sih.gov.in/sih2025PS"
    
    print("\nTesting with browser headers...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        # Add a small delay
        time.sleep(random.uniform(2, 5))
        
        response = session.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            print("✓ Connection successful with headers")
            return True
        else:
            print(f"✗ Failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Connection with headers failed: {e}")
        return False

def test_monitor_class():
    """Test the SIHSubmissionMonitor class"""
    print("\nTesting SIHSubmissionMonitor class...")
    
    try:
        monitor = SIHSubmissionMonitor()
        print(f"Target ID: {monitor.target_id}")
        print(f"URL: {monitor.url}")
        
        # Test fetching page content
        html_content = monitor.fetch_page_content()
        print(f"✓ Successfully fetched page content ({len(html_content)} characters)")
        
        # Test parsing
        count = monitor.parse_submission_count(html_content)
        print(f"✓ Successfully parsed submission count: {count}")
        
        return True
        
    except Exception as e:
        print(f"✗ Monitor class test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("SIH Website Connectivity Test")
    print("=" * 40)
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Connection with Headers", test_with_headers),
        ("Monitor Class", test_monitor_class)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    if all(result for _, result in results):
        print("\n🎉 All tests passed! The connection should work.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nPossible solutions:")
        print("1. The website may be temporarily blocking requests")
        print("2. Try running from a different IP address")
        print("3. Consider using a proxy service")
        print("4. Check if the website structure has changed")

if __name__ == "__main__":
    main()