import secrets_utils

try:
    print(f"init_encryption exists: {hasattr(secrets_utils, 'init_encryption')}")
    print(f"set_master_password exists: {hasattr(secrets_utils, 'set_master_password')}")
    assert secrets_utils.set_master_password == secrets_utils.init_encryption
    print("SUCCESS: Alias works.")
except Exception as e:
    print(f"FAILURE: {e}")
