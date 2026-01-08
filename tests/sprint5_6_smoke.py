"""
Sprint 5.6 Smoke Tests - Demo Analytics + Export + Supportability

Tests the new demo event logging and summary functions.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.demo_seed import (
    get_demo_event_summary,
    seed_demo_all,
    clear_demo_all,
    seed_demo_regenerate,
    demo_integrity_check
)


def test_event_logging():
    """Test 1: Verify events are logged during operations."""
    print("\n🧪 Test 1: Event logging during operations")
    
    # Perform operations that should log events
    clear_demo_all()
    seed_demo_all()
    
    # Get event summary
    summary = get_demo_event_summary(limit=50)
    
    # Should have events
    assert summary['exists'] == True, "Event log should exist after operations"
    assert len(summary['events']) > 0, "Should have logged events"
    
    # Check for seed event
    event_types = [e.get('event_type') for e in summary['events']]
    assert 'seed' in event_types, "Should have logged seed event"
    assert 'clear' in event_types, "Should have logged clear event"
    
    print(f"  ✅ Logged {len(summary['events'])} events")
    print(f"  ✅ Event types: {set(event_types)}")


def test_event_summary_structure():
    """Test 2: Validate event summary structure."""
    print("\n🧪 Test 2: Event summary structure")
    
    summary = get_demo_event_summary(limit=10)
    
    # Validate structure
    assert 'exists' in summary, "Missing 'exists' key"
    assert 'events' in summary, "Missing 'events' key"
    assert 'totals' in summary, "Missing 'totals' key"
    
    # Validate totals structure
    totals = summary['totals']
    assert 'seed_count' in totals, "Missing seed_count"
    assert 'clear_count' in totals, "Missing clear_count"
    assert 'regen_count' in totals, "Missing regen_count"
    assert 'integrity_count' in totals, "Missing integrity_count"
    
    print(f"  ✅ Structure valid: exists={summary['exists']}")
    print(f"  ✅ Totals: seed={totals['seed_count']}, clear={totals['clear_count']}, regen={totals['regen_count']}, integrity={totals['integrity_count']}")


def test_regenerate_event():
    """Test 3: Verify regenerate logs event."""
    print("\n🧪 Test 3: Regenerate event logging")
    
    # Get count before
    summary_before = get_demo_event_summary(limit=100)
    regen_count_before = summary_before['totals']['regen_count']
    
    # Regenerate
    seed_demo_regenerate()
    
    # Get count after
    summary_after = get_demo_event_summary(limit=100)
    regen_count_after = summary_after['totals']['regen_count']
    
    # Should have incremented
    assert regen_count_after >= regen_count_before + 1, "Regen count should increment"
    
    # Check for regenerate event in recent events
    recent_types = [e.get('event_type') for e in summary_after['events'][:5]]
    assert 'regenerate' in recent_types, "Should have regenerate event in recent events"
    
    print(f"  ✅ Regen count: {regen_count_before} → {regen_count_after}")


def test_integrity_check_event():
    """Test 4: Verify integrity check logs event."""
    print("\n🧪 Test 4: Integrity check event logging")
    
    # Get count before
    summary_before = get_demo_event_summary(limit=100)
    integrity_count_before = summary_before['totals']['integrity_count']
    
    # Run integrity check
    demo_integrity_check()
    
    # Get count after
    summary_after = get_demo_event_summary(limit=100)
    integrity_count_after = summary_after['totals']['integrity_count']
    
    # Should have incremented
    assert integrity_count_after >= integrity_count_before + 1, "Integrity count should increment"
    
    # Check for integrity_check event in recent events
    recent_types = [e.get('event_type') for e in summary_after['events'][:5]]
    assert 'integrity_check' in recent_types, "Should have integrity_check event in recent events"
    
    print(f"  ✅ Integrity count: {integrity_count_before} → {integrity_count_after}")


def test_event_timestamps():
    """Test 5: Validate event timestamps are present and valid."""
    print("\n🧪 Test 5: Event timestamp validation")
    
    # Seed to create fresh event
    clear_demo_all()
    seed_demo_all()
    
    summary = get_demo_event_summary(limit=1)
    
    assert summary['exists'] == True, "Should have events"
    assert len(summary['events']) > 0, "Should have at least 1 event"
    
    last_event = summary['events'][0]
    
    # Check timestamp
    assert 'ts' in last_event, "Event should have timestamp"
    ts = last_event['ts']
    assert len(ts) > 0, "Timestamp should not be empty"
    
    # Validate ISO format (basic check)
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        print(f"  ✅ Valid timestamp: {ts}")
    except:
        raise AssertionError(f"Invalid timestamp format: {ts}")
    
    # Check payload
    assert 'payload' in last_event, "Event should have payload"
    print(f"  ✅ Event type: {last_event.get('event_type')}")


def test_totals_accumulation():
    """Test 6: Verify totals accumulate correctly."""
    print("\n🧪 Test 6: Totals accumulation")
    
    # Get initial totals
    summary_initial = get_demo_event_summary(limit=100)
    totals_before = summary_initial['totals']
    
    # Perform multiple operations
    clear_demo_all()
    seed_demo_all()
    demo_integrity_check()
    
    # Get new totals
    summary_after = get_demo_event_summary(limit=100)
    totals_after = summary_after['totals']
    
    # Verify increments
    assert totals_after['clear_count'] >= totals_before['clear_count'] + 1, "Clear count should increase"
    assert totals_after['seed_count'] >= totals_before['seed_count'] + 1, "Seed count should increase"
    assert totals_after['integrity_count'] >= totals_before['integrity_count'] + 1, "Integrity count should increase"
    
    print(f"  ✅ Before: seed={totals_before['seed_count']}, clear={totals_before['clear_count']}, integrity={totals_before['integrity_count']}")
    print(f"  ✅ After:  seed={totals_after['seed_count']}, clear={totals_after['clear_count']}, integrity={totals_after['integrity_count']}")


def test_event_payload_content():
    """Test 7: Verify event payloads contain useful data."""
    print("\n🧪 Test 7: Event payload content")
    
    # Clear and seed to create fresh events
    clear_demo_all()
    seed_result = seed_demo_all()
    
    # Get recent events
    summary = get_demo_event_summary(limit=5)
    
    # Find seed event
    seed_event = None
    for event in summary['events']:
        if event.get('event_type') == 'seed':
            seed_event = event
            break
    
    assert seed_event is not None, "Should find seed event"
    
    payload = seed_event.get('payload', {})
    
    # Check payload has useful data
    assert 'threads' in payload or 'created' in payload, "Seed payload should have threads or created field"
    
    if 'threads' in payload:
        assert payload['threads'] > 0, "Thread count should be positive"
        print(f"  ✅ Seed payload: threads={payload.get('threads')}, leads={payload.get('leads')}, tasks={payload.get('tasks')}")
    
    print(f"  ✅ Payload keys: {list(payload.keys())}")


if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 5.6 Smoke Tests - Demo Analytics + Export")
    print("=" * 60)
    
    try:
        test_event_logging()
        test_event_summary_structure()
        test_regenerate_event()
        test_integrity_check_event()
        test_event_timestamps()
        test_totals_accumulation()
        test_event_payload_content()
        
        print("\n" + "=" * 60)
        print("📊 Results: 7/7 tests passed ✅")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
