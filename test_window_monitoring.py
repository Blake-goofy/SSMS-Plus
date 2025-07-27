"""Test script to validate the new window title monitoring logic"""

from ssms_window import SsmsWindow
import time

def test_window_monitoring():
    """Test the new window title monitoring functionality"""
    
    print("=== Testing Window Title Monitoring Logic ===")
    print()
    
    print("This test simulates different SSMS scenarios:")
    print("1. New Query from loading state (should detect as 'new query')")
    print("2. Script View As from existing content (should detect as 'Script View As')")
    print()
    
    # Test 1: Simulate new query scenario
    print("--- Test 1: New Query Detection ---")
    print("Expected behavior:")
    print("- Initial title: 'Microsoft SQL Server Management Studio' (loading)")
    print("- Should detect as: new query workflow")
    print("- Should wait for: SQLQuery title to appear")
    print()
    
    # Test 2: Simulate Script View As scenario  
    print("--- Test 2: Script View As Detection ---")
    print("Expected behavior:")
    print("- Initial title: Something with content (existing tab)")
    print("- Should detect as: Script View As workflow")
    print("- Should wait for: SQLQuery title to appear")
    print()
    
    print("--- Actual Window Monitoring ---")
    print("Testing with current active window...")
    print("(This will timeout if not in SSMS with proper workflow)")
    
    # Test the actual function
    try:
        start_time = time.time()
        ready, is_new_query = SsmsWindow.wait_for_query(timeout=5)
        end_time = time.time()
        
        print(f"Results after {end_time - start_time:.2f} seconds:")
        print(f"- Window ready: {ready}")
        print(f"- Is new query: {is_new_query}")
        print(f"- Workflow type: {'New Query' if is_new_query else 'Script View As'}")
        
    except Exception as e:
        print(f"Error during test: {e}")
    
    print()
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_window_monitoring()
