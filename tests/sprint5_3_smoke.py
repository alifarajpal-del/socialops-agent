"""
Sprint 5.3 Smoke Tests: Demo Management (Clear, Seed, Regenerate)
- Test clear_demo_all()
- Test seed after clear
- Test idempotency
- Test seed_demo_regenerate()
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.demo_seed import seed_demo_all, clear_demo_all, seed_demo_regenerate


def test_clear_demo():
    """Test that clear_demo_all removes all demo data"""
    print("\n🧪 Test 1: Clear Demo Data")
    
    result = clear_demo_all()
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    assert result['cleared'] is True, "Clear operation should succeed"
    
    print(f"   ✅ Demo data cleared: {result['threads_deleted']} threads, {result['messages_deleted']} messages, {result['leads_deleted']} leads, {result['tasks_deleted']} tasks, {result['replies_deleted']} replies")
    return True


def test_seed_after_clear():
    """Test seeding after clearing"""
    print("\n🧪 Test 2: Seed After Clear")
    
    result = seed_demo_all()
    
    if result.get('skipped'):
        print(f"   ℹ️  Demo data already exists (reason: {result.get('reason')})")
        # If skipped, we need to clear and try again
        clear_demo_all()
        result = seed_demo_all()
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    # Verify counts (9 threads, 6 leads, 9 tasks, 15 replies, 33 messages)
    assert result['threads'] >= 9, f"Expected >= 9 threads, got {result['threads']}"
    assert result['messages'] >= 30, f"Expected >= 30 messages, got {result['messages']}"
    assert result['leads'] >= 6, f"Expected >= 6 leads, got {result['leads']}"
    assert result['tasks'] >= 9, f"Expected >= 9 tasks, got {result['tasks']}"
    assert result['replies'] >= 15, f"Expected >= 15 replies, got {result['replies']}"
    assert result['created'] is True, "Seed should mark created=True"
    
    print(f"   ✅ Demo data seeded: {result['threads']} threads, {result['messages']} messages, {result['leads']} leads, {result['tasks']} tasks, {result['replies']} replies")
    return True


def test_idempotency():
    """Test that seeding twice skips the second time"""
    print("\n🧪 Test 3: Idempotency Check")
    
    # First seed (should succeed or already exist)
    result1 = seed_demo_all()
    
    # Second seed (should skip)
    result2 = seed_demo_all()
    
    assert result2['skipped'] is True, "Second seed call should be skipped"
    assert result2.get('reason') is not None, "Skip reason should be provided"
    
    print(f"   ✅ Idempotency verified: second call skipped (reason: {result2['reason']})")
    return True


def test_regenerate():
    """Test seed_demo_regenerate clears and seeds"""
    print("\n🧪 Test 4: Regenerate Demo Data")
    
    result = seed_demo_regenerate()
    
    # Check structure
    assert 'cleared' in result, "Result should contain 'cleared' key"
    assert 'seeded' in result, "Result should contain 'seeded' key"
    
    cleared = result['cleared']
    seeded = result['seeded']
    
    if 'error' in cleared:
        print(f"   ❌ Clear error: {cleared['error']}")
        return False
    
    if 'error' in seeded:
        print(f"   ❌ Seed error: {seeded['error']}")
        return False
    
    # Verify clear happened
    assert cleared['cleared'] is True, "Clear should succeed"
    
    # Verify seed happened
    assert seeded['created'] is True, "Seed should create new data"
    assert seeded['threads'] >= 9, f"Expected >= 9 threads, got {seeded['threads']}"
    assert seeded['leads'] >= 6, f"Expected >= 6 leads, got {seeded['leads']}"
    assert seeded['tasks'] >= 9, f"Expected >= 9 tasks, got {seeded['tasks']}"
    
    print(f"   ✅ Regenerate succeeded:")
    print(f"      - Cleared: {cleared['threads_deleted']} threads, {cleared['leads_deleted']} leads, {cleared['tasks_deleted']} tasks")
    print(f"      - Seeded: {seeded['threads']} threads, {seeded['leads']} leads, {seeded['tasks']} tasks, {seeded['replies']} replies")
    return True


def test_verify_sector_coverage():
    """Verify all 3 sectors are represented after regenerate"""
    print("\n🧪 Test 5: Sector Coverage After Regenerate")
    
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
    
    print(f"   ✅ Sector coverage verified: {salon_count} salon, {store_count} store, {clinic_count} clinic")
    return True


def main():
    """Run all Sprint 5.3 smoke tests"""
    print("=" * 60)
    print("🚀 Sprint 5.3 Smoke Tests: Demo Management")
    print("=" * 60)
    
    tests = [
        test_clear_demo,
        test_seed_after_clear,
        test_idempotency,
        test_regenerate,
        test_verify_sector_coverage,
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
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All Sprint 5.3 tests passed!")
        print("=" * 60)
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
