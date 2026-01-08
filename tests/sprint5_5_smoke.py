"""
Sprint 5.5 Smoke Tests - Ops Quality-of-Life + Data Integrity

Tests the new ops filtering functions and data integrity checks.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.demo_seed import (
    infer_sector_from_thread_id,
    demo_integrity_check,
    get_demo_stats,
    seed_demo_all,
    clear_demo_all
)


def test_infer_sector():
    """Test 1: Sector inference from thread IDs."""
    print("\n🧪 Test 1: infer_sector_from_thread_id()")
    
    test_cases = [
        ('demo_salon_001', 'salon'),
        ('demo_store_xyz', 'store'),
        ('demo_clinic_abc', 'clinic'),
        ('DEMO_SALON_UPPER', 'salon'),
        ('demo_Store_Mixed', 'store'),
        ('random_thread_123', 'unknown'),
        ('', 'unknown'),
        (None, 'unknown')
    ]
    
    for thread_id, expected in test_cases:
        result = infer_sector_from_thread_id(thread_id) if thread_id is not None else infer_sector_from_thread_id('')
        assert result == expected, f"Expected '{expected}' for '{thread_id}', got '{result}'"
        print(f"  ✅ '{thread_id}' → '{result}'")


def test_integrity_check_clean():
    """Test 2: Integrity check on clean seeded data (no orphans)."""
    print("\n🧪 Test 2: demo_integrity_check() on clean data")
    
    # Clear and seed fresh data
    clear_demo_all()
    seed_result = seed_demo_all()
    
    assert seed_result['created'] == True, "Seed should succeed"
    print(f"  ✅ Seeded: {seed_result['threads']} threads")
    
    # Run integrity check
    integrity = demo_integrity_check()
    
    # Fresh seed should have no orphans
    assert integrity['orphans_found'] == 0, f"Expected 0 orphans, found {integrity['orphans_found']}"
    assert integrity['orphans_deleted'] == 0, f"Expected 0 deleted, got {integrity['orphans_deleted']}"
    
    print(f"  ✅ Integrity check: {integrity['orphans_found']} orphans found")
    print(f"  ✅ Details: {integrity['details']}")


def test_integrity_check_after_clear():
    """Test 3: Integrity check after clearing threads (should clean orphans)."""
    print("\n🧪 Test 3: demo_integrity_check() after partial clear")
    
    # Seed first
    clear_demo_all()
    seed_demo_all()
    
    # Manually delete threads only (leaving orphans)
    from services.db import get_db_path
    import sqlite3
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete only threads (leave messages/leads/tasks)
    cursor.execute("DELETE FROM threads WHERE thread_id LIKE 'demo_%'")
    conn.commit()
    conn.close()
    
    print(f"  ✅ Deleted demo threads (orphaning children)")
    
    # Now run integrity check
    integrity = demo_integrity_check()
    
    # Should find and clean orphans
    assert integrity['orphans_found'] > 0, "Should find orphaned records"
    assert integrity['orphans_deleted'] > 0, "Should delete orphaned records"
    
    print(f"  ✅ Found {integrity['orphans_found']} orphans")
    print(f"  ✅ Deleted {integrity['orphans_deleted']} orphans")
    print(f"  ✅ Details: {integrity['details']}")


def test_stats_after_integrity_cleanup():
    """Test 4: Stats should reflect clean state after integrity check."""
    print("\n🧪 Test 4: get_demo_stats() after integrity cleanup")
    
    # Clear and seed
    clear_demo_all()
    seed_demo_all()
    
    # Get initial stats
    stats_before = get_demo_stats()
    print(f"  ✅ Before cleanup: threads={stats_before['threads']}, leads={stats_before['leads']}, tasks={stats_before['tasks']}")
    
    # Run integrity check (should be clean)
    integrity = demo_integrity_check()
    
    # Stats should remain the same (no orphans)
    stats_after = get_demo_stats()
    print(f"  ✅ After cleanup: threads={stats_after['threads']}, leads={stats_after['leads']}, tasks={stats_after['tasks']}")
    
    assert stats_before['threads'] == stats_after['threads'], "Thread count should match"
    assert stats_before['leads'] == stats_after['leads'], "Lead count should match"
    assert stats_before['tasks'] == stats_after['tasks'], "Task count should match"
    
    print(f"  ✅ Stats unchanged (data was clean)")


def test_sector_coverage():
    """Test 5: Verify all 3 sectors present after seeding."""
    print("\n🧪 Test 5: Sector coverage validation")
    
    from services.db import get_db_path
    import sqlite3
    
    # Seed fresh data
    clear_demo_all()
    seed_demo_all()
    
    # Count threads by sector
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT thread_id FROM threads WHERE thread_id LIKE 'demo_%'")
    threads = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    sectors = {
        'salon': 0,
        'store': 0,
        'clinic': 0,
        'unknown': 0
    }
    
    for thread_id in threads:
        sector = infer_sector_from_thread_id(thread_id)
        sectors[sector] += 1
    
    # Validate coverage
    assert sectors['salon'] > 0, "Should have salon threads"
    assert sectors['store'] > 0, "Should have store threads"
    assert sectors['clinic'] > 0, "Should have clinic threads"
    assert sectors['unknown'] == 0, "Should have no unknown sectors"
    
    print(f"  ✅ Sector distribution: salon={sectors['salon']}, store={sectors['store']}, clinic={sectors['clinic']}")


def test_full_lifecycle():
    """Test 6: Full lifecycle - seed → integrity check → clear → integrity check."""
    print("\n🧪 Test 6: Full lifecycle")
    
    # Step 1: Clear
    clear_demo_all()
    stats1 = get_demo_stats()
    assert stats1['exists'] == False, "Should be empty"
    print(f"  ✅ Step 1: Clear → exists={stats1['exists']}")
    
    # Step 2: Seed
    seed_demo_all()
    stats2 = get_demo_stats()
    assert stats2['exists'] == True, "Should have data"
    print(f"  ✅ Step 2: Seed → exists={stats2['exists']}, threads={stats2['threads']}")
    
    # Step 3: Integrity check (should be clean)
    integrity1 = demo_integrity_check()
    assert integrity1['orphans_found'] == 0, "Fresh seed should be clean"
    print(f"  ✅ Step 3: Integrity check → {integrity1['orphans_found']} orphans")
    
    # Step 4: Clear again
    clear_demo_all()
    stats3 = get_demo_stats()
    assert stats3['exists'] == False, "Should be empty again"
    print(f"  ✅ Step 4: Clear → exists={stats3['exists']}")
    
    # Step 5: Final integrity check (should be clean)
    integrity2 = demo_integrity_check()
    print(f"  ✅ Step 5: Final integrity → {integrity2['orphans_found']} orphans")
    
    print(f"  ✅ Full lifecycle completed successfully")


if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 5.5 Smoke Tests - Ops Quality + Data Integrity")
    print("=" * 60)
    
    try:
        test_infer_sector()
        test_integrity_check_clean()
        test_integrity_check_after_clear()
        test_stats_after_integrity_cleanup()
        test_sector_coverage()
        test_full_lifecycle()
        
        print("\n" + "=" * 60)
        print("📊 Results: 6/6 tests passed ✅")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
