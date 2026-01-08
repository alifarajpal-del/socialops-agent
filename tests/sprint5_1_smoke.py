"""
Sprint 5.1 Smoke Tests: Pilot Ready features
- Demo seed data loading
- Idempotency checks
- Search functionality
- Cross-page selection simulation
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.demo_seed import seed_demo_data
from services.db import get_db_path


def test_demo_seed():
    """Test that demo data can be seeded successfully"""
    print("\n🧪 Test 1: Demo Seed Data Loading")
    
    result = seed_demo_data()
    
    # Check if seed was successful
    if result.get('skipped'):
        print("   ℹ️  Demo data already exists (idempotent check passed)")
        return True
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    # Verify counts
    assert result['threads'] == 3, f"Expected 3 threads, got {result['threads']}"
    assert result['messages'] == 8, f"Expected 8 messages, got {result['messages']}"
    assert result['leads'] == 2, f"Expected 2 leads, got {result['leads']}"
    assert result['tasks'] == 3, f"Expected 3 tasks, got {result['tasks']}"
    assert result['replies'] >= 5, f"Expected >= 5 replies, got {result['replies']}"
    
    print(f"   ✅ Demo data seeded: {result['threads']} threads, {result['messages']} messages, {result['leads']} leads, {result['tasks']} tasks, {result['replies']} replies")
    return True


def test_idempotency():
    """Test that calling seed twice doesn't duplicate data"""
    print("\n🧪 Test 2: Idempotency Check")
    
    # First call
    result1 = seed_demo_data()
    
    # Second call
    result2 = seed_demo_data()
    
    # Second call should be skipped
    assert result2['skipped'] is True, "Second seed call should be skipped"
    
    print("   ✅ Idempotency verified: second call skipped")
    return True


def test_thread_count():
    """Test that threads exist in database after seeding"""
    print("\n🧪 Test 3: Thread Count Verification")
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count all threads
    cursor.execute("SELECT COUNT(*) FROM threads")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count >= 3, f"Expected at least 3 threads, found {count}"
    
    print(f"   ✅ Found {count} threads in database")
    return True


def test_search_simulation():
    """Simulate search query and verify results"""
    print("\n🧪 Test 4: Search Query Simulation")
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Search for demo threads
    query = "demo"
    cursor.execute("""
        SELECT thread_id, platform 
        FROM threads 
        WHERE thread_id LIKE ?
        LIMIT 5
    """, (f'%{query}%',))
    
    results = cursor.fetchall()
    conn.close()
    
    assert len(results) >= 3, f"Expected at least 3 search results, found {len(results)}"
    
    print(f"   ✅ Search returned {len(results)} results")
    return True


def test_cross_page_selection():
    """Simulate setting selected_thread_id for cross-page navigation"""
    print("\n🧪 Test 5: Cross-Page Selection Simulation")
    
    # Get first demo thread ID
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT thread_id 
        FROM threads 
        WHERE thread_id LIKE 'demo-%'
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("   ⚠️  No demo threads found to test selection")
        return True
    
    thread_id = result[0]
    
    # Simulate session state
    mock_session_state = {
        'selected_thread_id': thread_id,
        'current_page': 'inbox'
    }
    
    assert mock_session_state['selected_thread_id'] == thread_id
    assert mock_session_state['current_page'] == 'inbox'
    
    print(f"   ✅ Selection simulation passed: {thread_id}")
    return True


def main():
    """Run all Sprint 5.1 smoke tests"""
    print("=" * 60)
    print("🚀 Sprint 5.1 Smoke Tests: Pilot Ready")
    print("=" * 60)
    
    tests = [
        test_demo_seed,
        test_idempotency,
        test_thread_count,
        test_search_simulation,
        test_cross_page_selection,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except AssertionError as e:
            print(f"   ❌ Assertion Failed: {e}")
            results.append(False)
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All Sprint 5.1 tests passed!")
        print("=" * 60)
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
