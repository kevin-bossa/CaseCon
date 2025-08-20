#!/usr/bin/env python3
"""
Version management script for CaseCon
Updates version numbers across all build files
"""
import re
import os
import sys
from pathlib import Path

def update_inno_setup_version(new_version):
    """Update version in Inno Setup script"""
    inno_file = "CaseCon_Setup.iss"
    if not os.path.exists(inno_file):
        print(f"Warning: {inno_file} not found")
        return False
    
    with open(inno_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version definition
    pattern = r'(#define MyAppVersion\s+")[^"]*(")'
    replacement = f'\\g<1>{new_version}\\g<2>'
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(inno_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Updated {inno_file}")
        return True
    else:
        print(f"✗ Could not update {inno_file}")
        return False

def update_app_info(new_version, app_name=None, publisher=None, url=None):
    """Update app information in Inno Setup script"""
    inno_file = "CaseCon_Setup.iss"
    if not os.path.exists(inno_file):
        print(f"Warning: {inno_file} not found")
        return False
    
    with open(inno_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Update version
    version_pattern = r'(#define MyAppVersion\s+")[^"]*(")'
    content = re.sub(version_pattern, f'\\g<1>{new_version}\\g<2>', content)
    
    # Update app name if provided
    if app_name:
        name_pattern = r'(#define MyAppName\s+")[^"]*(")'
        content = re.sub(name_pattern, f'\\g<1>{app_name}\\g<2>', content)
    
    # Update publisher if provided
    if publisher:
        publisher_pattern = r'(#define MyAppPublisher\s+")[^"]*(")'
        content = re.sub(publisher_pattern, f'\\g<1>{publisher}\\g<2>', content)
    
    # Update URL if provided
    if url:
        url_pattern = r'(#define MyAppURL\s+")[^"]*(")'
        content = re.sub(url_pattern, f'\\g<1>{url}\\g<2>', content)
    
    if content != original_content:
        with open(inno_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated app information in {inno_file}")
        return True
    else:
        print(f"No changes made to {inno_file}")
        return False

def create_version_file(version):
    """Create a version.txt file for reference"""
    with open("version.txt", "w") as f:
        f.write(f"CaseCon Version: {version}\n")
        f.write(f"Build Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("✓ Created version.txt")

def get_current_version():
    """Get current version from Inno Setup script"""
    inno_file = "CaseCon_Setup.iss"
    if not os.path.exists(inno_file):
        return "Unknown"
    
    try:
        with open(inno_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'#define MyAppVersion\s+"([^"]*)"', content)
        if match:
            return match.group(1)
    except:
        pass
    
    return "Unknown"

def increment_version(version_str, increment_type="patch"):
    """Increment version number (semantic versioning)"""
    try:
        parts = version_str.split('.')
        if len(parts) != 3:
            return version_str
        
        major, minor, patch = map(int, parts)
        
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    except:
        return version_str

def main():
    """Main version management function"""
    if len(sys.argv) < 2:
        current_version = get_current_version()
        print("CaseCon Version Manager")
        print("=" * 40)
        print(f"Current version: {current_version}")
        print("\nUsage:")
        print("  python update_version.py <new_version>")
        print("  python update_version.py increment [major|minor|patch]")
        print("  python update_version.py info <name> <publisher> <url>")
        print("\nExamples:")
        print("  python update_version.py 1.2.3")
        print("  python update_version.py increment patch")
        print("  python update_version.py increment minor")
        print('  python update_version.py info "CaseCon Pro" "Your Company" "https://yoursite.com"')
        return
    
    if sys.argv[1] == "increment":
        current_version = get_current_version()
        increment_type = sys.argv[2] if len(sys.argv) > 2 else "patch"
        new_version = increment_version(current_version, increment_type)
        
        print(f"Incrementing version: {current_version} → {new_version} ({increment_type})")
        
        if update_inno_setup_version(new_version):
            create_version_file(new_version)
            print(f"✓ Version updated to {new_version}")
        else:
            print("✗ Failed to update version")
    
    elif sys.argv[1] == "info":
        if len(sys.argv) < 5:
            print("Usage: python update_version.py info <name> <publisher> <url>")
            return
        
        current_version = get_current_version()
        app_name = sys.argv[2]
        publisher = sys.argv[3]
        url = sys.argv[4]
        
        print(f"Updating app information...")
        print(f"Name: {app_name}")
        print(f"Publisher: {publisher}")
        print(f"URL: {url}")
        
        if update_app_info(current_version, app_name, publisher, url):
            print("✓ App information updated successfully")
        else:
            print("✗ Failed to update app information")
    
    else:
        new_version = sys.argv[1]
        
        # Validate version format (basic check)
        if not re.match(r'^\d+\.\d+\.\d+$', new_version):
            print("Error: Version must be in format X.Y.Z (e.g., 1.0.0)")
            return
        
        current_version = get_current_version()
        print(f"Updating version: {current_version} → {new_version}")
        
        if update_inno_setup_version(new_version):
            create_version_file(new_version)
            print(f"✓ Version updated to {new_version}")
            print("\nNext steps:")
            print("1. Run: python build_exe.py")
            print("2. Compile with Inno Setup")
            print(f"3. Your installer will be: CaseCon_Setup_v{new_version}.exe")
        else:
            print("✗ Failed to update version")

if __name__ == "__main__":
    main()