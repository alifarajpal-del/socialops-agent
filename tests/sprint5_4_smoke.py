"""
Sprint 5.4 Smoke Tests - Demo Status & Confirmations

Tests the new get_demo_stats() and demo_exists() functions.
Also validates the complete demo data lifecycle with stats tracking.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.demo_seed import (
    demo_exists,
    get_demo_stats,
    seed_demo_all,
    clear_demo_all,
    seed_demo_regenerate
)


def test_demo_exists():
    """Test 1: demo_exists() returns correct boolean."""
    print("\n🧪 Test 1: demo_exists() function")
    
    # Clear first
    clear_demo_all()
    
    # Should return False when no demo data
    exists = demo_exists()
    assert exists == False, f"Expected False, got {exists}"
    print(f"  ✅ No demo: exists={exists}")
    
    # Seed demo
    seed_demo_all()
    
    # Should return True after seeding
    exists = demo_exists()
    assert exists == True, f"Expected True, got {exists}"
    print(f"  ✅ After seed: exists={exists}")


def test_get_demo_stats_empty():
    """Test 2: get_demo_stats() on empty database."""
    print("\n🧪 Test 2: get_demo_stats() on empty DB")
    
    # Clear all demo data
    clear_demo_all()
    
    # Get stats
    stats = get_demo_stats()
    
    # Validate structure
    assert 'exists' in stats, "Missing 'exists' key"
    assert 'threads' in stats, "Missing 'threads' key"
    assert 'leads' in stats, "Missing 'leads' key"
    assert 'tasks' in stats, "Missing 'tasks' key"
    assert 'replies' in stats, "Missing 'replies' key"
    
    # Validate values
    assert stats['exists'] == False, f"Expected exists=False, got {stats['exists']}"
    assert stats['threads'] == 0, f"Expected 0 threads, got {stats['threads']}"
    assert stats['leads'] == 0, f"Expected 0 leads, got {stats['leads']}"
    assert stats['tasks'] == 0, f"Expected 0 tasks, got {stats['tasks']}"
    assert stats['replies'] == 0, f"Expected 0 replies, got {stats['replies']}"
    
    print(f"  ✅ Empty stats: {stats}")


def test_get_demo_stats_after_seed():
    """Test 3: get_demo_stats() after seeding."""
    print("\n🧪 Test 3: get_demo_stats() after seed")
    
    # Clear first
    clear_demo_all()
    
    # Seed demo data
    seed_result = seed_demo_all()
    
    # Get stats
    stats = get_demo_stats()
    
    # Validate exists is True
    assert stats['exists'] == True, f"Expected exists=True, got {stats['exists']}"
    
    # Validate counts match seed result
    assert stats['threads'] == seed_result['threads'], f"Thread count mismatch: stats={stats['threads']}, seed={seed_result['threads']}"
    assert stats['leads'] == seed_result['leads'], f"Lead count mismatch: stats={stats['leads']}, seed={seed_result['leads']}"
    assert stats['tasks'] == seed_result['tasks'], f"Task count mismatch: stats={stats['tasks']}, seed={seed_result['tasks']}"
    assert stats['replies'] == seed_result['replies'], f"Reply count mismatch: stats={stats['replies']}, seed={seed_result['replies']}"
    
    print(f"  ✅ After seed stats: threads={stats['threads']}, leads={stats['leads']}, tasks={stats['tasks']}, replies={stats['replies']}")
    print(f"  ✅ Matches seed result: {seed_result['created']=}, {seed_result['threads']=}, {seed_result['leads']=}, {seed_result['tasks']=}, {seed_result['replies']=}")


def test_stats_after_regenerate():
    """Test 4: get_demo_stats() after regenerating."""
    print("\n🧪 Test 4: get_demo_stats() after regenerate")
    
    # Seed first
    seed_demo_all()
    
    # Regenerate
    regen_result = seed_demo_regenerate()
    
    # Get stats
    stats = get_demo_stats()
    
    # Validate exists is True
    assert stats['exists'] == True, f"Expected exists=True after regenerate, got {stats['exists']}"
    
    # Validate counts match regenerated seed
    seeded = regen_result['seeded']
    assert stats['threads'] == seeded['threads'], f"Thread count mismatch after regen"
    assert stats['leads'] == seeded['leads'], f"Lead count mismatch after regen"
    assert stats['tasks'] == seeded['tasks'], f"Task count mismatch after regen"
    assert stats['replies'] == seeded['replies'], f"Reply count mismatch after regen"
    
    print(f"  ✅ After regenerate stats: threads={stats['threads']}, leads={stats['leads']}, tasks={stats['tasks']}, replies={stats['replies']}")
    print(f"  ✅ Cleared: {regen_result['cleared']['cleared']=}, {regen_result['cleared']['threads_deleted']=}")
    print(f"  ✅ Reseeded: {regen_result['seeded']['created']=}, {regen_result['seeded']['threads']=}")


def test_expected_counts():
    """Test 5: Validate expected demo data counts (9 threads, 6 leads, 9 tasks)."""
    print("\n🧪 Test 5: Validate expected counts")
    
    # Clear and seed
    clear_demo_all()
    seed_demo_all()
    
    # Get stats
    stats = get_demo_stats()
    
    # Expected: 9 threads (3 salon + 3 store + 3 clinic)
    expected_threads = 9
    assert stats['threads'] == expected_threads, f"Expected {expected_threads} threads, got {stats['threads']}"
    
    # Expected: 6 leads (2 per sector)
    expected_leads = 6
    assert stats['leads'] == expected_leads, f"Expected {expected_leads} leads, got {stats['leads']}"
    
    # Expected: 9 tasks (1 per thread)
    expected_tasks = 9
    assert stats['tasks'] == expected_tasks, f"Expected {expected_tasks} tasks, got {stats['tasks']}"
    
    # Expected: 15 replies (5 per sector)
    expected_replies = 15
    assert stats['replies'] == expected_replies, f"Expected {expected_replies} replies, got {stats['replies']}"
    
    print(f"  ✅ Validated expected counts:")
    print(f"    - Threads: {stats['threads']} (expected {expected_threads})")
    print(f"    - Leads: {stats['leads']} (expected {expected_leads})")
    print(f"    - Tasks: {stats['tasks']} (expected {expected_tasks})")
    print(f"    - Replies: {stats['replies']} (expected {expected_replies})")


def test_lifecycle():
    """Test 6: Full lifecycle - clear → stats → seed → stats → clear → stats."""
    print("\n🧪 Test 6: Full lifecycle")
    
    # 1. Clear
    clear_demo_all()
    stats1 = get_demo_stats()
    assert stats1['exists'] == False and stats1['threads'] == 0, "Step 1 failed"
    print(f"  ✅ Step 1: Clear → exists={stats1['exists']}, threads={stats1['threads']}")
    
    # 2. Seed
    seed_demo_all()
    stats2 = get_demo_stats()
    assert stats2['exists'] == True and stats2['threads'] == 9, "Step 2 failed"
    print(f"  ✅ Step 2: Seed → exists={stats2['exists']}, threads={stats2['threads']}")
    
    # 3. Clear again
    clear_demo_all()
    stats3 = get_demo_stats()
    assert stats3['exists'] == False and stats3['threads'] == 0, "Step 3 failed"
    print(f"  ✅ Step 3: Clear → exists={stats3['exists']}, threads={stats3['threads']}")
    
    print(f"  ✅ Full lifecycle completed successfully")


if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 5.4 Smoke Tests - Demo Status & Confirmations")
    print("=" * 60)
    
    try:
        test_demo_exists()
        test_get_demo_stats_empty()
        test_get_demo_stats_after_seed()
        test_stats_after_regenerate()
        test_expected_counts()
        test_lifecycle()
        
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
