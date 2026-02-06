#!/usr/bin/env python3
"""
Simple test to verify GUI application can be imported and initialized
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gui_import():
    """Test that GUI module can be imported"""
    try:
        import gui
        print("✓ GUI module imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import GUI module: {e}")
        return False

def test_tkinter_available():
    """Test that tkinter is available"""
    try:
        import tkinter as tk
        print("✓ Tkinter is available")
        return True
    except ImportError:
        print("✗ Tkinter is not available")
        print("  Install tkinter:")
        print("  - Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  - macOS: tkinter is included with Python")
        print("  - Windows: tkinter is included with Python")
        return False

def test_gui_class():
    """Test that GUI class can be instantiated (without mainloop)"""
    try:
        import tkinter as tk
        from gui import LLCARGui

        # Create root but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window

        # Try to create GUI instance
        app = LLCARGui(root)
        print("✓ LLCARGui class instantiated successfully")

        # Destroy window
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ Failed to instantiate LLCARGui: {e}")
        return False

def test_launchers_exist():
    """Test that launcher scripts exist"""
    launchers = ['launch_gui.sh', 'launch_gui.bat', 'gui.py']
    all_exist = True

    for launcher in launchers:
        path = Path(launcher)
        if path.exists():
            print(f"✓ {launcher} exists")
        else:
            print(f"✗ {launcher} not found")
            all_exist = False

    return all_exist

def main():
    """Run all tests"""
    print("=" * 60)
    print("LLCAR GUI - Basic Tests")
    print("=" * 60)
    print()

    results = []

    print("1. Testing Tkinter availability...")
    results.append(test_tkinter_available())
    print()

    print("2. Testing GUI import...")
    results.append(test_gui_import())
    print()

    print("3. Testing launcher scripts...")
    results.append(test_launchers_exist())
    print()

    print("4. Testing GUI class instantiation...")
    results.append(test_gui_class())
    print()

    print("=" * 60)
    if all(results):
        print("✓ All tests passed!")
        print()
        print("GUI is ready to use. Launch with:")
        print("  - Windows: launch_gui.bat")
        print("  - Linux/macOS: ./launch_gui.sh")
        print("  - Or directly: python gui.py")
        return 0
    else:
        print("✗ Some tests failed")
        print("Please check the errors above and install missing dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())
