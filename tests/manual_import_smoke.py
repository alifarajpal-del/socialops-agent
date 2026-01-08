"""
Smoke test for manual import and reply generation.
Tests Sprint A functionality without Streamlit UI.
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.inbox_store import InboxStore
from services.plugins_registry import register_plugin, route_to_plugin
from plugins.salons.plugin import SalonsPlugin


def test_manual_import():
    """Test manual JSON import functionality."""
    print("=" * 60)
    print("TEST 1: Manual Import")
    print("=" * 60)
    
    # Initialize inbox store with memory DB
    import tempfile
    import os
    temp_db = os.path.join(tempfile.gettempdir(), "test_inbox.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    store = InboxStore(db_path=temp_db)
    print("✓ InboxStore initialized with tables")
    
    # Load test data
    import_file = Path(__file__).parent.parent / "import.json"
    if not import_file.exists():
        print(f"✗ FAIL: {import_file} not found")
        return False
    
    with open(import_file, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    print(f"✓ Loaded {len(messages)} messages from import.json")
    
    # Import messages
    result = store.import_from_json(messages)
    print(f"✓ Import result: {result['imported']} messages, {result['threads_created']} threads")
    
    if result['errors']:
        print(f"✗ FAIL: Import errors: {result['errors']}")
        return False
    
    # Verify threads created
    threads = store.list_threads()
    if len(threads) < 1:
        print(f"✗ FAIL: Expected >= 1 thread, got {len(threads)}")
        return False
    print(f"✓ Found {len(threads)} thread(s)")
    
    # Verify messages in thread
    thread_id = threads[0]['thread_id']
    messages = store.get_thread_messages(thread_id)
    if len(messages) != 2:
        print(f"✗ FAIL: Expected 2 messages in thread, got {len(messages)}")
        return False
    print(f"✓ Thread contains {len(messages)} messages")
    
    print("\n✅ TEST 1 PASSED: Manual import successful\n")
    return True, store, threads[0], messages


def test_reply_generation():
    """Test AI reply suggestion generation."""
    print("=" * 60)
    print("TEST 2: Reply Generation")
    print("=" * 60)
    
    # Register plugin
    plugin = SalonsPlugin()
    register_plugin(plugin)
    print(f"✓ Registered plugin: {plugin.name}")
    
    # Get store and thread from previous test
    _, store, thread, messages = test_manual_import()
    
    # Get last message
    last_msg = messages[-1]
    platform = thread['platform']
    text = last_msg['text']
    
    print(f"✓ Last message: '{text[:50]}...'")
    print(f"✓ Platform: {platform}")
    
    # Route to plugin
    routed_plugin = route_to_plugin(platform, text, 'ar')
    if not routed_plugin:
        print("✗ FAIL: No plugin routed")
        return False
    print(f"✓ Routed to plugin: {routed_plugin.name}")
    
    # Classify intent
    intent = routed_plugin.classify(text, 'ar')
    print(f"✓ Classified intent: {intent}")
    
    # Extract entities
    entities = routed_plugin.extract(text, 'ar')
    print(f"✓ Extracted entities: {entities}")
    
    # Generate reply
    context = {
        'extracted': entities,
        'sender_name': last_msg['sender_name'],
        'platform': platform
    }
    suggested_reply = routed_plugin.suggest_reply(intent, 'ar', context)
    
    if not suggested_reply or len(suggested_reply) < 10:
        print(f"✗ FAIL: Invalid suggested reply: '{suggested_reply}'")
        return False
    
    print(f"✓ Suggested reply ({len(suggested_reply)} chars):")
    print(f"  {suggested_reply[:120]}...")
    
    # Verify language (should contain Arabic characters)
    arabic_chars = sum(1 for c in suggested_reply if '\u0600' <= c <= '\u06FF')
    if arabic_chars < 5:
        print(f"✗ FAIL: Reply doesn't seem to be in Arabic (only {arabic_chars} Arabic chars)")
        return False
    print(f"✓ Reply contains {arabic_chars} Arabic characters")
    
    print("\n✅ TEST 2 PASSED: Reply generation successful\n")
    return True


if __name__ == "__main__":
    try:
        # Run tests
        import_result = test_manual_import()
        if not import_result or not import_result[0]:
            sys.exit(1)
        
        reply_result = test_reply_generation()
        if not reply_result:
            sys.exit(1)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
