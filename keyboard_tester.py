#!/usr/bin/env python3
"""
Keyboard Key Name Detector for CaseCon
Save this as: keyboard_tester.py
Run with: python keyboard_tester.py
"""

import keyboard
import pyperclip
import time

print("=== KEYBOARD KEY NAME DETECTOR FOR CASECON ===")
print("This will help you find the correct key names for your keyboard")
print()
print("INSTRUCTIONS:")
print("1. Press key combinations to see their actual names")
print("2. Try pressing: Ctrl+Windows+Alt+U")
print("3. Press ESC when you're done testing")
print("=" * 60)

def on_key_event(event):
    if event.event_type == keyboard.KEY_DOWN:
        key_name = event.name
        print(f"Key pressed: '{key_name}'")
        
        # Try to detect common combinations
        pressed_keys = []
        
        # Check for Ctrl
        try:
            if keyboard.is_pressed('ctrl') or keyboard.is_pressed('left ctrl'):
                pressed_keys.append('ctrl')
        except:
            pass
            
        # Check for Alt
        try:
            if keyboard.is_pressed('alt') or keyboard.is_pressed('left alt'):
                pressed_keys.append('alt')
        except:
            pass
            
        # Check various possible Windows key names
        windows_key_names = [
            'left windows', 'right windows', 'windows',
            'cmd', 'left cmd', 'right cmd', 
            'windows izquierda', 'windows derecha',
            'super', 'left super', 'right super'
        ]
        
        windows_detected = None
        for win_key in windows_key_names:
            try:
                if keyboard.is_pressed(win_key):
                    windows_detected = win_key
                    pressed_keys.append('WIN')
                    break
            except:
                continue
        
        if pressed_keys:
            combination = '+'.join(pressed_keys + [key_name.upper()])
            print(f"  → Combination detected: {combination}")
            
            # Show what would be saved for the app
            if windows_detected:
                internal_combo = f"ctrl+{windows_detected}+alt+{key_name.lower()}"
                print(f"  → Internal format: {internal_combo}")
                print(f"  → This would work for CaseCon!")
            
        print("-" * 40)
        
        if key_name.lower() == 'esc':
            print("Exiting tester...")
            return False

print("\n🎯 Starting key detection... Press some keys!")
print("💡 Try: Ctrl+Windows+Alt+U, then press ESC to quit\n")

try:
    keyboard.hook(on_key_event)
    keyboard.wait('esc')
except KeyboardInterrupt:
    print("\nTester interrupted by user")
except Exception as e:
    print(f"\nError during key detection: {e}")

print("\n" + "=" * 60)
print("CLIPBOARD & HOTKEY TESTS")
print("=" * 60)

# Test clipboard functionality
print("\n📋 Testing clipboard operations...")
try:
    original = pyperclip.paste()
    test_text = "Hello World Test"
    
    pyperclip.copy(test_text)
    time.sleep(0.1)
    result = pyperclip.paste()
    
    if result == test_text:
        print("✅ Clipboard operations work correctly")
    else:
        print("❌ Clipboard operations may have issues")
        print(f"   Expected: '{test_text}'")
        print(f"   Got: '{result}'")
    
    # Restore original clipboard
    pyperclip.copy(original)
    
except Exception as e:
    print(f"❌ Clipboard error: {e}")

# Test hotkey registration with common variations
print("\n🔥 Testing hotkey registration...")
print("Trying different Windows key variations...")

variations_to_test = [
    'ctrl+left windows+alt+u',
    'ctrl+right windows+alt+u',
    'ctrl+windows+alt+u',
    'left ctrl+left windows+left alt+u',
    'ctrl+cmd+alt+u',
    'ctrl+super+alt+u'
]

successful_variations = []
for variation in variations_to_test:
    try:
        def test_handler():
            print(f"🎉 SUCCESS: {variation} would work!")
        
        handle = keyboard.add_hotkey(variation, test_handler)
        print(f"✅ Can register: {variation}")
        successful_variations.append(variation)
        keyboard.remove_hotkey(handle)
        
    except Exception as e:
        print(f"❌ Cannot register: {variation}")
        print(f"   Error: {e}")

print("\n" + "=" * 60)
print("RESULTS & RECOMMENDATIONS")
print("=" * 60)

if successful_variations:
    print("🎉 GOOD NEWS! These key combinations should work in CaseCon:")
    for var in successful_variations:
        print(f"   ✅ {var}")
    
    recommended = successful_variations[0]
    print(f"\n💡 RECOMMENDED for your settings.json:")
    print(f'   "uppercase": "{recommended.replace("+u", "+u")}",')
    print(f'   "lowercase": "{recommended.replace("+u", "+l")}",')
    
else:
    print("⚠️  WARNING: No standard key combinations worked!")
    print("   You may need to try different key combinations manually.")

print(f"\n🔍 Key Detection Complete!")
print("You can now update your CaseCon settings based on these results.")
print("Press any key to exit...")

try:
    input()
except:
    pass