import json
import os
import shutil
import re

PROFILES_DIR = "profiles"
OLD_PROFILE_FILE = "my_profile.json"

def _sanitize_profile_name(profile_name: str) -> str:
    """
    Sanitizes profile name to prevent path traversal attacks.
    Removes any path separators and dangerous patterns.
    """
    if not profile_name:
        return "Default"
    
    # Remove any path separators and parent directory references
    sanitized = os.path.basename(profile_name)
    
    # Remove any remaining dangerous patterns
    sanitized = re.sub(r'[<>:"/\\|?*]', '', sanitized)
    sanitized = re.sub(r'\.\.+', '', sanitized)  # Remove multiple dots
    
    # Ensure we have a valid name
    sanitized = sanitized.strip('. ')
    
    if not sanitized:
        return "Default"
    
    return sanitized

def ensure_profiles_dir():
    """Ensures profiles directory exists and migrates old profile if needed."""
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)
    
    # Migration
    if os.path.exists(OLD_PROFILE_FILE):
        target = os.path.join(PROFILES_DIR, "Default.json")
        if not os.path.exists(target):
            try:
                shutil.move(OLD_PROFILE_FILE, target)
            except Exception as e:
                print(f"Migration error: {e}")
        else:
             # Just backup/ignore if Default already exists? 
             # Let's just leave it there for now to not be destructive
             pass

def list_profiles():
    """Returns a list of profile names (filenames without .json)."""
    ensure_profiles_dir()
    profiles = []
    if os.path.exists(PROFILES_DIR):
        for f in os.listdir(PROFILES_DIR):
            if f.endswith(".json"):
                 profiles.append(f[:-5])
    
    if not profiles:
        return ["Default"]
    return sorted(profiles)

def load_profile(profile_name="Default"):
    """Loads a specific profile."""
    ensure_profiles_dir()
    # FIX: Sanitize profile name to prevent path traversal
    safe_name = _sanitize_profile_name(profile_name)
    path = os.path.join(PROFILES_DIR, f"{safe_name}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load profile: {e}")
        return {}

def save_profile(profile_name, data):
    """Saves a profile."""
    ensure_profiles_dir()
    # FIX: Sanitize profile name to prevent path traversal
    safe_name = _sanitize_profile_name(profile_name)
    
    path = os.path.join(PROFILES_DIR, f"{safe_name}.json")
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

