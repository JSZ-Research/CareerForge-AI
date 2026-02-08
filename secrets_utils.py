import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SECRETS_FILE = "secrets_store.json"

# --- Encryption Utils ---

def _derive_key(password: str, salt: bytes) -> bytes:
    """Derives a safe key from the password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data_dict: dict, password: str) -> dict:
    """Returns the structure: {'version': 1, 'salt': <hex>, 'data': <encrypted_str>}"""
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    f = Fernet(key)
    
    json_bytes = json.dumps(data_dict).encode('utf-8')
    encrypted = f.encrypt(json_bytes)
    
    return {
        "version": 1,
        "salt": salt.hex(),
        "data": encrypted.decode('utf-8')
    }

def decrypt_data(store: dict, password: str) -> dict:
    """Decrypts the store using the provided password. Raises InvalidToken if wrong."""
    salt = bytes.fromhex(store['salt'])
    key = _derive_key(password, salt)
    f = Fernet(key)
    
    encrypted_bytes = store['data'].encode('utf-8')
    decrypted_bytes = f.decrypt(encrypted_bytes)
    return json.loads(decrypted_bytes.decode('utf-8'))

# --- Core Logic ---

def load_secrets(password: str = None):
    """
    Loads secrets. 
    1. Checks ENV variables first (OPENAI_API_KEY, GEMINI_API_KEY).
    2. Checks disk.
       - If disk has v1 encrypted format, needs password.
       - If disk has old (list-based) or v0 (plain dict), loads directly.
    
    Returns:
        dict: {
            "openai_keys": [],    # or list of dicts for v1
            "gemini_keys": [],
            "is_encrypted": bool, 
            "requires_unlock": bool
        }
    """
    # Base structure
    secrets = {
        "openai_keys": [],
        "gemini_keys": [],
        "is_encrypted": False,
        "requires_unlock": False
    }

    # 1. Env Variables Override (Virtual keys)
    # We add them as "Environment" keys if they exist
    env_openai = os.getenv("OPENAI_API_KEY")
    env_gemini = os.getenv("GEMINI_API_KEY")

    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, "r") as f:
                disk_data = json.load(f)
            
            # Check version
            if isinstance(disk_data, dict) and "version" in disk_data and disk_data["version"] >= 1:
                # Encrypted path
                secrets["is_encrypted"] = True
                if password:
                    try:
                        decrypted = decrypt_data(disk_data, password)
                        # Merge decrypted fields
                        for k in ["openai_keys", "gemini_keys"]:
                            secrets[k] = decrypted.get(k, [])
                    except Exception:
                        secrets["requires_unlock"] = True
                else:
                    secrets["requires_unlock"] = True
            else:
                # Legacy unencrypted path
                # Standardize format if it was simple list
                if isinstance(disk_data, dict):
                    secrets["openai_keys"] = disk_data.get("openai_keys", [])
                    secrets["gemini_keys"] = disk_data.get("gemini_keys", [])
        except Exception as e:
            print(f"Error loading secrets: {e}")

    # Inject Env vars at runtime (not saved to disk)
    if env_openai:
        # Check if already present to avoid duplicates visually? No, env is special.
        # We prepend it as a special entry
        entry = {"name": "ENV (OPENAI_API_KEY)", "key": env_openai, "source": "env"}
        # Avoid dupes if we can, but simple prepend is safer for now
        secrets["openai_keys"].insert(0, entry)

    if env_gemini:
        entry = {"name": "ENV (GEMINI_API_KEY)", "key": env_gemini, "source": "env"}
        secrets["gemini_keys"].insert(0, entry)

    return secrets

def init_encryption(password: str):
    """Migrates current plain secrets to encrypted vault."""
    current = load_secrets() # Load currently accessible secrets
    
    # Filter out env vars before saving
    clean_openai = [k for k in current["openai_keys"] if isinstance(k, dict) and k.get("source") != "env" or isinstance(k, str)]
    clean_gemini = [k for k in current["gemini_keys"] if isinstance(k, dict) and k.get("source") != "env" or isinstance(k, str)]
    
    # Normalize str keys to objects if migrating from old format
    # Old format: ["sk-...", "sk-..."]
    # New format: [{"name": "Key 1", "key": "sk-..."}, ...]
    
    def normalize(k_list):
        new_list = []
        for item in k_list:
            if isinstance(item, str):
                new_list.append({"name": f"Legacy Key (...{item[-4:]})", "key": item})
            else:
                new_list.append(item)
        return new_list

    to_encrypt = {
        "openai_keys": normalize(clean_openai),
        "gemini_keys": normalize(clean_gemini)
    }
    
    encrypted_store = encrypt_data(to_encrypt, password)
    
    with open(SECRETS_FILE, "w") as f:
        json.dump(encrypted_store, f, indent=2)

def save_secret_encrypted(provider, name, key, password):
    """Saves a new key to the encrypted store."""
    # Load current with password
    secrets = load_secrets(password)
    target_list = "openai_keys" if provider == "OpenAI" else "gemini_keys"
    
    # Remove env keys from the list we will save
    real_keys = [k for k in secrets[target_list] if isinstance(k, dict) and k.get("source") != "env"]
    
    # Add new key
    real_keys.append({"name": name, "key": key})
    
    # Prepare full object to re-encrypt
    # We need the other provider's real keys too
    other_list = "gemini_keys" if provider == "OpenAI" else "openai_keys"
    other_keys = [k for k in secrets[other_list] if isinstance(k, dict) and k.get("source") != "env"]
    
    to_encrypt = {
        target_list: real_keys,
        other_list: other_keys
    }
    
    encrypted_store = encrypt_data(to_encrypt, password)
    try:
        with open(SECRETS_FILE, "w") as f:
            json.dump(encrypted_store, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

def save_secret_plain(provider, key, name="Key"):
    """Legacy save for unencrypted mode."""
    # We now also upgrade the structure to dicts even in plain mode for consistency in UI
    try:
        if os.path.exists(SECRETS_FILE):
             with open(SECRETS_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"openai_keys": [], "gemini_keys": []}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Secrets load warning: {e}")
        data = {"openai_keys": [], "gemini_keys": []}

    target = "openai_keys" if provider == "OpenAI" else "gemini_keys"
    
    # Check duplicate (simple string check or dict check)
    # If legacy list of strings
    if all(isinstance(k, str) for k in data.get(target, [])):
        # Upgrade to list of dicts on first write to support names
        new_list = [{"name": f"Legacy (...{k[-4:]})", "key": k} for k in data[target]]
        new_list.append({"name": name, "key": key})
        data[target] = new_list
    else:
        # It's a list of dicts or mixed. We'll append a dict.
        existing = data.get(target, [])
        # Check if key value exists
        exists = False
        for ex in existing:
            if isinstance(ex, str) and ex == key: exists = True
            if isinstance(ex, dict) and ex.get("key") == key: exists = True
        
        if not exists:
            # Save as named object
            existing.append({"name": name, "key": key})
            data[target] = existing
    
    # Safety check for non-upgraded other list
    other = "gemini_keys" if provider == "OpenAI" else "openai_keys"
    if other not in data: data[other] = []

    with open(SECRETS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def mask_key_obj(key_obj):
    """Helper to display key object in UI."""
    if isinstance(key_obj, str):
         # Legacy string key
         k = key_obj
         return f"Legacy (...{k[-4:]})" if len(k) > 4 else k
    elif isinstance(key_obj, dict):
        # New dict key with name
        name = key_obj.get("name", "Unnamed")
        k = key_obj.get("key", "")
        tail = k[-4:] if len(k) > 4 else "***"
        return f"{name} (...{tail})"
    return "Invalid Key"
