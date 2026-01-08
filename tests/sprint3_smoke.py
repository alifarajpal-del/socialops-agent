"""
Sprint 3 Smoke Test - Replies Library + SLA + Follow-up

Tests replies store, SLA computation, and follow-up suggestions.
"""
import sys
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.replies_store import RepliesStore
from services.inbox_engine import compute_sla_status, suggest_followup_time


def test_replies_crud():
    """Test replies CRUD operations."""
    print("=" * 60)
    print("TEST 1: Replies CRUD")
    print("=" * 60)
    
    # Initialize store with temp DB
    temp_db = os.path.join(tempfile.gettempdir(), "test_replies.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    replies_store = RepliesStore(db_path=temp_db)
    print("✓ RepliesStore initialized")
    
    # Create reply
    reply_id = replies_store.create_reply(
        title="Test Welcome",
        body="Hello! How can I help you?",
        lang="en",
        scope="core",
        tags=["greeting", "test"]
    )
    print(f"✓ Created reply #{reply_id}")
    
    # Get reply
    reply = replies_store.get_reply(reply_id)
    if not reply:
        print("✗ FAIL: Reply not found")
        return False
    
    print(f"✓ Reply retrieved: '{reply['title']}'")
    print(f"  Lang: {reply['lang']}, Tags: {reply['tags']}")
    
    # List replies
    replies = replies_store.list_replies()
    if len(replies) != 1:
        print(f"✗ FAIL: Expected 1 reply, got {len(replies)}")
        return False
    print(f"✓ Listed {len(replies)} reply(s)")
    
    # Update reply
    replies_store.update_reply(reply_id, title="Updated Welcome", tags=["greeting", "updated"])
    updated = replies_store.get_reply(reply_id)
    if updated['title'] != "Updated Welcome":
        print("✗ FAIL: Reply not updated")
        return False
    print(f"✓ Reply updated: '{updated['title']}', tags={updated['tags']}")
    
    # Filter by lang
    replies_store.create_reply(
        title="Arabic Welcome",
        body="مرحباً",
        lang="ar",
        scope="core"
    )
    en_replies = replies_store.list_replies(lang="en")
    ar_replies = replies_store.list_replies(lang="ar")
    
    if len(en_replies) != 1 or len(ar_replies) != 1:
        print(f"✗ FAIL: Filter failed (en={len(en_replies)}, ar={len(ar_replies)})")
        return False
    print(f"✓ Language filter works (en={len(en_replies)}, ar={len(ar_replies)})")
    
    # Delete reply
    replies_store.delete_reply(reply_id)
    deleted = replies_store.get_reply(reply_id)
    if deleted is not None:
        print("✗ FAIL: Reply not deleted")
        return False
    print(f"✓ Reply #{reply_id} deleted")
    
    print("\n✅ TEST 1 PASSED: Replies CRUD works\n")
    return True


def test_replies_seed():
    """Test seeding default replies."""
    print("=" * 60)
    print("TEST 2: Replies Seeding")
    print("=" * 60)
    
    # Initialize fresh store
    temp_db = os.path.join(tempfile.gettempdir(), "test_seed.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    replies_store = RepliesStore(db_path=temp_db)
    print("✓ Fresh RepliesStore initialized")
    
    # Seed defaults
    count = replies_store.seed_defaults()
    if count != 10:
        print(f"✗ FAIL: Expected 10 seeded replies, got {count}")
        return False
    print(f"✓ Seeded {count} default replies")
    
    # Verify counts by language
    en_count = len(replies_store.list_replies(lang="en"))
    ar_count = len(replies_store.list_replies(lang="ar"))
    
    if en_count != 5 or ar_count != 5:
        print(f"✗ FAIL: Expected 5 EN and 5 AR, got {en_count} EN and {ar_count} AR")
        return False
    print(f"✓ Language distribution: {en_count} EN, {ar_count} AR")
    
    # Try seeding again (should skip)
    count2 = replies_store.seed_defaults()
    if count2 != 0:
        print(f"✗ FAIL: Second seed should return 0, got {count2}")
        return False
    print("✓ Second seed correctly skipped (table not empty)")
    
    print("\n✅ TEST 2 PASSED: Seeding works correctly\n")
    return True


def test_sla_computation():
    """Test SLA status computation."""
    print("=" * 60)
    print("TEST 3: SLA Computation")
    print("=" * 60)
    
    # Test recent message (OK)
    recent = (datetime.now() - timedelta(hours=1)).isoformat()
    sla_ok = compute_sla_status(recent)
    
    if sla_ok['status'] != 'ok':
        print(f"✗ FAIL: Expected 'ok', got '{sla_ok['status']}'")
        return False
    print(f"✓ Recent message (1h ago): {sla_ok['emoji']} {sla_ok['status']}")
    
    # Test warning message (4-24h)
    warning = (datetime.now() - timedelta(hours=12)).isoformat()
    sla_warning = compute_sla_status(warning)
    
    if sla_warning['status'] != 'warning':
        print(f"✗ FAIL: Expected 'warning', got '{sla_warning['status']}'")
        return False
    print(f"✓ Warning message (12h ago): {sla_warning['emoji']} {sla_warning['status']}")
    
    # Test urgent message (>24h)
    urgent = (datetime.now() - timedelta(hours=48)).isoformat()
    sla_urgent = compute_sla_status(urgent)
    
    if sla_urgent['status'] != 'urgent':
        print(f"✗ FAIL: Expected 'urgent', got '{sla_urgent['status']}'")
        return False
    print(f"✓ Urgent message (48h ago): {sla_urgent['emoji']} {sla_urgent['status']}")
    
    print("\n✅ TEST 3 PASSED: SLA computation works\n")
    return True


def test_followup_suggestions():
    """Test follow-up time suggestions."""
    print("=" * 60)
    print("TEST 4: Follow-up Suggestions")
    print("=" * 60)
    
    base_time = datetime.now().isoformat()
    
    # Test urgent priority (1h)
    urgent_followup = suggest_followup_time(base_time, priority='urgent')
    urgent_dt = datetime.fromisoformat(urgent_followup)
    base_dt = datetime.fromisoformat(base_time)
    
    urgent_hours = (urgent_dt - base_dt).total_seconds() / 3600
    if not (0.9 < urgent_hours < 1.1):  # Allow small tolerance
        print(f"✗ FAIL: Urgent should be ~1h, got {urgent_hours:.1f}h")
        return False
    print(f"✓ Urgent priority: +{urgent_hours:.1f}h")
    
    # Test normal priority (24h)
    normal_followup = suggest_followup_time(base_time, priority='normal')
    normal_dt = datetime.fromisoformat(normal_followup)
    
    normal_hours = (normal_dt - base_dt).total_seconds() / 3600
    if not (23.5 < normal_hours < 24.5):
        print(f"✗ FAIL: Normal should be ~24h, got {normal_hours:.1f}h")
        return False
    print(f"✓ Normal priority: +{normal_hours:.1f}h")
    
    # Test low priority (72h / 3 days)
    low_followup = suggest_followup_time(base_time, priority='low')
    low_dt = datetime.fromisoformat(low_followup)
    
    low_hours = (low_dt - base_dt).total_seconds() / 3600
    if not (71 < low_hours < 73):
        print(f"✗ FAIL: Low should be ~72h, got {low_hours:.1f}h")
        return False
    print(f"✓ Low priority: +{low_hours:.1f}h")
    
    print("\n✅ TEST 4 PASSED: Follow-up suggestions work\n")
    return True


if __name__ == "__main__":
    try:
        # Run tests
        result1 = test_replies_crud()
        if not result1:
            sys.exit(1)
        
        result2 = test_replies_seed()
        if not result2:
            sys.exit(1)
        
        result3 = test_sla_computation()
        if not result3:
            sys.exit(1)
        
        result4 = test_followup_suggestions()
        if not result4:
            sys.exit(1)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED - Sprint 3 Functionality Works!")
        print("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
