"""
CRM Smoke Test - Sprint 2

Tests leads and tasks functionality.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.inbox_store import InboxStore
from services.crm_store import CRMStore


def test_lead_creation():
    """Test creating lead from thread."""
    print("=" * 60)
    print("TEST 1: Lead Creation from Thread")
    print("=" * 60)
    
    # Initialize stores
    import tempfile
    import os
    temp_db = os.path.join(tempfile.gettempdir(), "test_crm.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    inbox_store = InboxStore(db_path=temp_db)
    crm_store = CRMStore(db_path=temp_db)
    print("✓ Stores initialized")
    
    # Import test messages
    import_file = Path(__file__).parent.parent / "import.json"
    if not import_file.exists():
        print(f"✗ FAIL: {import_file} not found")
        return False
    
    with open(import_file, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    result = inbox_store.import_from_json(messages)
    print(f"✓ Imported {result['imported']} messages")
    
    # Get first thread
    threads = inbox_store.list_threads()
    if not threads:
        print("✗ FAIL: No threads found")
        return False
    
    thread = threads[0]
    thread_id = thread['thread_id']
    platform = thread['platform']
    print(f"✓ Found thread: {thread_id} ({platform})")
    
    # Create lead from thread
    lead_id = crm_store.create_lead_from_thread(thread_id, platform, "Test Lead")
    print(f"✓ Created lead #{lead_id}")
    
    # Verify lead exists
    lead = crm_store.get_lead(lead_id)
    if not lead:
        print("✗ FAIL: Lead not found")
        return False
    
    print(f"✓ Lead verified: {lead['name']}, status={lead['status']}")
    
    # Verify thread linkage
    lead_by_thread = crm_store.get_lead_by_thread(thread_id)
    if not lead_by_thread or lead_by_thread['id'] != lead_id:
        print("✗ FAIL: Lead-thread linkage broken")
        return False
    
    print("✓ Lead-thread linkage verified")
    
    print("\n✅ TEST 1 PASSED: Lead creation successful\n")
    return True, inbox_store, crm_store, lead_id, thread_id


def test_lead_operations():
    """Test lead status updates, tags, and notes."""
    print("=" * 60)
    print("TEST 2: Lead Operations")
    print("=" * 60)
    
    # Get stores from previous test
    _, inbox_store, crm_store, lead_id, thread_id = test_lead_creation()
    
    # Update status
    crm_store.update_lead_status(lead_id, 'qualified')
    lead = crm_store.get_lead(lead_id)
    if lead['status'] != 'qualified':
        print(f"✗ FAIL: Status not updated (expected 'qualified', got '{lead['status']}')")
        return False
    print(f"✓ Status updated to: {lead['status']}")
    
    # Add tags
    tags = ['hot-lead', 'follow-up', 'vip']
    crm_store.set_lead_tags(lead_id, tags)
    lead = crm_store.get_lead(lead_id)
    if lead['tags'] != tags:
        print(f"✗ FAIL: Tags not set correctly")
        return False
    print(f"✓ Tags set: {lead['tags']}")
    
    # Add notes
    crm_store.add_lead_note(lead_id, "First note")
    crm_store.add_lead_note(lead_id, "Second note")
    lead = crm_store.get_lead(lead_id)
    if not lead['notes'] or 'First note' not in lead['notes']:
        print("✗ FAIL: Notes not added")
        return False
    print(f"✓ Notes added ({len(lead['notes'])} chars)")
    
    # List leads by status
    qualified_leads = crm_store.list_leads(status='qualified')
    if not qualified_leads or qualified_leads[0]['id'] != lead_id:
        print("✗ FAIL: Lead not found in status filter")
        return False
    print(f"✓ Found {len(qualified_leads)} qualified lead(s)")
    
    print("\n✅ TEST 2 PASSED: Lead operations successful\n")
    return True, inbox_store, crm_store, lead_id, thread_id


def test_task_creation():
    """Test creating and managing tasks."""
    print("=" * 60)
    print("TEST 3: Task Creation")
    print("=" * 60)
    
    # Get stores from previous test
    _, inbox_store, crm_store, lead_id, thread_id = test_lead_operations()
    
    # Create follow-up task
    due_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
    task_id = crm_store.create_task(
        title="Follow up with Test Lead",
        due_at_iso=due_at,
        lead_id=lead_id,
        thread_id=thread_id,
        task_type="followup"
    )
    print(f"✓ Created task #{task_id}")
    
    # List tasks
    tasks = crm_store.list_tasks(include_completed=False)
    if not tasks or tasks[0]['id'] != task_id:
        print("✗ FAIL: Task not found")
        return False
    
    task = tasks[0]
    print(f"✓ Task found: '{task['title']}'")
    print(f"  Due: {task['due_at']}")
    print(f"  Type: {task['type']}")
    print(f"  Lead: #{task['related_lead_id']}")
    print(f"  Thread: {task['related_thread_id']}")
    
    # Complete task
    crm_store.complete_task(task_id)
    tasks_pending = crm_store.list_tasks(include_completed=False)
    if any(t['id'] == task_id for t in tasks_pending):
        print("✗ FAIL: Task still showing as pending")
        return False
    print("✓ Task completed")
    
    # Verify completed task in full list
    tasks_all = crm_store.list_tasks(include_completed=True)
    completed_task = next((t for t in tasks_all if t['id'] == task_id), None)
    if not completed_task or completed_task['completed'] != 1:
        print("✗ FAIL: Task completion not recorded")
        return False
    print("✓ Task completion verified")
    
    print("\n✅ TEST 3 PASSED: Task creation and management successful\n")
    return True


if __name__ == "__main__":
    try:
        # Run tests
        result1 = test_lead_creation()
        if not result1 or not result1[0]:
            sys.exit(1)
        
        result2 = test_lead_operations()
        if not result2 or not result2[0]:
            sys.exit(1)
        
        result3 = test_task_creation()
        if not result3:
            sys.exit(1)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED - Sprint 2 CRM Functionality Works!")
        print("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
