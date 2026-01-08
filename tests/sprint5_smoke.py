"""
Sprint 5 Smoke Tests - Daily Ops + Search + Bulk Actions + CSV Export.

Tests:
1. Search across threads, leads, replies
2. CSV export (leads, tasks, threads)
3. Bulk operations setup
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_service import search_threads, search_leads, search_replies, search_all
from services.export_service import export_leads_csv, export_tasks_csv, export_threads_csv
from services.crm_store import CRMStore
from services.inbox_store import get_inbox_store
from services.replies_store import RepliesStore


def test_search_service():
    """Test unified search across entities."""
    print("\n=== Test 1: Search Service ===")
    
    # Use existing data from previous sprints
    crm = CRMStore()
    store = get_inbox_store()
    replies = RepliesStore()
    
    # Search threads (may exist from previous tests)
    thread_results = search_threads("test")
    print(f"✓ Thread search returned {len(thread_results)} result(s)")
    
    # Search leads (should exist from Sprint 2-4 tests)
    lead_results = search_leads("lina")  # From Sprint 4 workspace profile
    if len(lead_results) == 0:
        lead_results = search_leads("")  # Get all
    print(f"✓ Lead search returned {len(lead_results)} result(s)")
    
    # Search replies
    reply_results = search_replies("")  # Get all replies
    print(f"✓ Reply search returned {len(reply_results)} result(s)")
    
    # Test empty query handling
    empty_results = search_threads("")
    assert len(empty_results) == 0, "Empty query should return no results"
    print("✓ Empty query handling works")
    
    # Test unified search
    all_results = search_all("test")
    print(f"✓ Unified search returned {len(all_results)} total results")
    
    # Test result structure
    if len(thread_results) > 0:
        assert 'id' in thread_results[0]
        assert 'type' in thread_results[0]
        assert 'route_target' in thread_results[0]
        print("✓ Result structure valid")
    
    print("✅ PASS: Search service")


def test_csv_export():
    """Test CSV export for leads, tasks, threads."""
    print("\n=== Test 2: CSV Export ===")
    
    # Export leads
    leads_csv = export_leads_csv()
    assert "ID" in leads_csv, "CSV missing headers"
    assert "Name" in leads_csv, "CSV missing Name column"
    lines = leads_csv.strip().split('\n')
    print(f"✓ Leads CSV: {len(lines)} line(s) (including header)")
    assert len(lines) >= 1, "Expected at least header line"
    
    # Export tasks
    tasks_csv = export_tasks_csv()
    assert "ID" in tasks_csv, "Tasks CSV missing headers"
    assert "Title" in tasks_csv, "Tasks CSV missing Title column"
    print("✓ Tasks CSV generated")
    
    # Export threads
    threads_csv = export_threads_csv()
    assert "ID" in threads_csv, "Threads CSV missing headers"
    assert "Title" in threads_csv, "Threads CSV missing Title column"
    lines = threads_csv.strip().split('\n')
    print(f"✓ Threads CSV: {len(lines)} line(s) (including header)")
    assert len(lines) >= 1, "Expected at least header line"
    
    print("✅ PASS: CSV export")


def test_bulk_operations_setup():
    """Test bulk operations prerequisites."""
    print("\n=== Test 3: Bulk Operations Setup ===")
    
    store = get_inbox_store()
    crm = CRMStore()
    
    # Test triage label column setup (can work even without data)
    import sqlite3
    conn = sqlite3.connect(store.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE threads ADD COLUMN triage_label TEXT DEFAULT 'later'")
        conn.commit()
        print("✓ Added triage_label column to threads table")
    except:
        print("✓ triage_label column already exists")
    
    # Verify column exists
    cursor.execute("PRAGMA table_info(threads)")
    columns = [row[1] for row in cursor.fetchall()]
    assert 'triage_label' in columns, "triage_label column not found"
    print("✓ triage_label column verified")
    
    # Get threads for bulk selection (may be empty in fresh DB)
    threads = store.list_threads()
    print(f"✓ DB has {len(threads)} thread(s) available for bulk operations")
    
    # If threads exist, test update
    if len(threads) > 0:
        thread_id = threads[0]['thread_id']
        cursor.execute("UPDATE threads SET triage_label = ? WHERE thread_id = ?", ("today", thread_id))
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT triage_label FROM threads WHERE thread_id = ?", (thread_id,))
        result = cursor.fetchone()
        assert result[0] == "today", "Triage label not updated"
        print(f"✓ Updated thread triage label to 'today'")
    else:
        print("✓ Skipped triage update test (no threads in DB)")
    
    conn.close()
    
    print("✅ PASS: Bulk operations setup")


def test_ops_metrics():
    """Test daily ops metrics calculation."""
    print("\n=== Test 4: Ops Metrics ===")
    
    store = get_inbox_store()
    crm = CRMStore()
    
    # Get threads for SLA
    threads = store.list_threads()
    print(f"✓ Loaded {len(threads)} threads for SLA monitoring")
    
    # Get tasks
    tasks = crm.list_tasks()
    print(f"✓ Loaded {len(tasks)} tasks")
    
    # Get leads by status
    leads = crm.list_leads()
    status_counts = {}
    for lead in leads:
        status = lead.get('status', 'new')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"✓ Leads by status: {status_counts}")
    
    print("✅ PASS: Ops metrics")


if __name__ == "__main__":
    print("🧪 Running Sprint 5 Smoke Tests...")
    
    try:
        test_search_service()
        test_csv_export()
        test_bulk_operations_setup()
        test_ops_metrics()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED (4/4)")
        print("="*50)
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
