"""
Sprint 4 Smoke Tests - Monetizable Productization.

Tests:
1. Workspace profile CRUD
2. Template placeholder filling
3. Saved reply insertion with placeholders
4. Plan limits retrieval
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.workspace_store import WorkspaceStore
from services.template_fill import fill_placeholders
from services.settings_flags import get_plan, get_plan_limits


def test_workspace_profile():
    """Test workspace profile save and retrieval."""
    print("\n=== Test 1: Workspace Profile CRUD ===")
    
    store = WorkspaceStore()
    
    # Save profile
    profile = {
        'business_name': "Lina's Salon",
        'business_type': 'salon',
        'city': 'Dubai',
        'phone': '+971 50 123 4567',
        'hours': '9AM-9PM daily',
        'booking_link': 'https://book.me/lina',
        'location_link': 'https://maps.google.com/lina',
        'brand_tone': 'friendly',
        'lang_default': 'en'
    }
    
    store.save_profile(profile)
    print("✓ Profile saved")
    
    # Retrieve profile
    retrieved = store.get_profile()
    assert retrieved is not None, "Profile not found"
    assert retrieved['business_name'] == "Lina's Salon"
    assert retrieved['city'] == 'Dubai'
    assert retrieved['phone'] == '+971 50 123 4567'
    print("✓ Profile retrieved correctly")
    
    print("✅ PASS: Workspace profile CRUD")


def test_template_filling():
    """Test template placeholder replacement."""
    print("\n=== Test 2: Template Placeholder Filling ===")
    
    profile = {
        'business_name': "Lina's Salon",
        'city': 'Dubai',
        'phone': '+971 50 123 4567',
        'hours': '9AM-9PM daily',
        'booking_link': 'https://book.me/lina',
        'location_link': 'https://maps.google.com/lina'
    }
    
    template = "Hi! Welcome to {business_name} in {city}. Call us at {phone}. Hours: {hours}"
    
    filled = fill_placeholders(template, profile)
    
    assert "Lina's Salon" in filled
    assert "Dubai" in filled
    assert "+971 50 123 4567" in filled
    assert "9AM-9PM daily" in filled
    print(f"✓ Filled: {filled}")
    
    # Test with missing profile
    filled_no_profile = fill_placeholders(template, None)
    assert "{business_name}" in filled_no_profile  # placeholders remain
    print("✓ Placeholders preserved when profile missing")
    
    print("✅ PASS: Template filling")


def test_saved_reply_with_placeholders():
    """Test saved reply insertion with placeholder filling."""
    print("\n=== Test 3: Saved Reply with Placeholders ===")
    
    profile = {
        'business_name': "Lina's Salon",
        'city': 'Dubai',
        'phone': '+971 50 123 4567'
    }
    
    saved_reply = "Thank you for contacting {business_name} in {city}! Call {phone} to book."
    
    # Simulate insertion (Append mode)
    ai_reply = "I'd be happy to help!"
    filled_reply = fill_placeholders(saved_reply, profile)
    final_text = f"{ai_reply}\n\n{filled_reply}"
    
    assert "Lina's Salon" in final_text
    assert "Dubai" in final_text
    assert "+971 50 123 4567" in final_text
    assert "I'd be happy to help!" in final_text
    print(f"✓ Final text: {final_text}")
    
    # Simulate Replace mode
    final_text_replace = fill_placeholders(saved_reply, profile)
    assert "Lina's Salon" in final_text_replace
    assert "I'd be happy to help!" not in final_text_replace
    print("✓ Replace mode works")
    
    print("✅ PASS: Saved reply with placeholders")


def test_plan_limits():
    """Test plan and limits retrieval."""
    print("\n=== Test 4: Plan & Limits ===")
    
    plan = get_plan()
    limits = get_plan_limits()
    
    assert plan in ['free', 'starter', 'pro', 'enterprise']
    print(f"✓ Current plan: {plan}")
    
    assert 'max_threads' in limits
    assert 'max_replies' in limits
    assert 'max_leads' in limits
    print(f"✓ Limits: {limits}")
    
    print("✅ PASS: Plan limits")


if __name__ == "__main__":
    print("🧪 Running Sprint 4 Smoke Tests...")
    
    try:
        test_workspace_profile()
        test_template_filling()
        test_saved_reply_with_placeholders()
        test_plan_limits()
        
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
