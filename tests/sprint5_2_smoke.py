"""
Sprint 5.2 Smoke Tests: Unified Demo Seed (9 threads across 3 sectors)
- Demo seed all sectors (salon, store, clinic)
- Idempotency checks
- Count verification
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.demo_seed import seed_demo_all


def test_demo_seed_all():
    """Test that unified demo seed creates all sector data"""
    print("\n🧪 Test 1: Unified Demo Seed (All Sectors)")
    
    result = seed_demo_all()
    
    # Check if seed was successful
    if result.get('skipped'):
        print("   ℹ️  Demo data already exists (idempotent check passed)")
        return True
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    # Verify counts (9 threads, 6 leads, 9 tasks, 15 replies)
    assert result['threads'] >= 9, f"Expected >= 9 threads, got {result['threads']}"
    assert result['messages'] >= 30, f"Expected >= 30 messages, got {result['messages']}"
    assert result['leads'] >= 6, f"Expected >= 6 leads, got {result['leads']}"
    assert result['tasks'] >= 9, f"Expected >= 9 tasks, got {result['tasks']}"
    assert result['replies'] >= 15, f"Expected >= 15 replies, got {result['replies']}"
    
    print(f"   ✅ Demo data seeded: {result['threads']} threads, {result['messages']} messages, {result['leads']} leads, {result['tasks']} tasks, {result['replies']} replies")
    return True


def test_idempotency():
    """Test that calling seed twice doesn't duplicate data"""
    print("\n🧪 Test 2: Idempotency Check")
    
    # First call
    result1 = seed_demo_all()
    
    # Second call
    result2 = seed_demo_all()
    
    # Second call should be skipped
    assert result2['skipped'] is True, "Second seed call should be skipped"
    
    print("   ✅ Idempotency verified: second call skipped")
    return True


def test_sector_coverage():
    """Test that all 3 sectors are represented"""
    print("\n🧪 Test 3: Sector Coverage Verification")
    
    import sqlite3
    from services.db import get_db_path
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check salon threads
    cursor.execute("SELECT COUNT(*) FROM threads WHERE thread_id LIKE 'demo_salon_%'")
    salon_count = cursor.fetchone()[0]
    
    # Check store threads
    cursor.execute("SELECT COUNT(*) FROM threads WHERE thread_id LIKE 'demo_store_%'")
    store_count = cursor.fetchone()[0]
    
    # Check clinic threads
    cursor.execute("SELECT COUNT(*) FROM threads WHERE thread_id LIKE 'demo_clinic_%'")
    clinic_count = cursor.fetchone()[0]
    
    conn.close()
    
    assert salon_count >= 3, f"Expected >= 3 salon threads, found {salon_count}"
    assert store_count >= 3, f"Expected >= 3 store threads, found {store_count}"
    assert clinic_count >= 3, f"Expected >= 3 clinic threads, found {clinic_count}"
    
    print(f"   ✅ Sector coverage: {salon_count} salon, {store_count} store, {clinic_count} clinic")
    return True


def main():
    """Run all Sprint 5.2 smoke tests"""
    print("=" * 60)
    print("🚀 Sprint 5.2 Smoke Tests: Unified Demo Seed")
    print("=" * 60)
    
    tests = [
        test_demo_seed_all,
        test_idempotency,
        test_sector_coverage,
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
        print("✅ All Sprint 5.2 tests passed!")
        print("=" * 60)
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
