import unittest
import json
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import secrets_utils
import utils
import export_utils
import profile_utils

class TestBasics(unittest.TestCase):

    def test_json_cleanup(self):
        """Test the JSON regex extractor."""
        raw = "Here is the json:\n```json\n{\"foo\": \"bar\"}\n```"
        clean = utils.clean_json_text(raw)
        self.assertEqual(json.loads(clean), {"foo": "bar"})

        raw2 = "Some text {\"a\": 1} more text"
        clean2 = utils.clean_json_text(raw2)
        self.assertEqual(json.loads(clean2), {"a": 1})

    def test_encryption_roundtrip(self):
        """Test encrypting and decrypting data."""
        data = {"key": "secret_value"}
        password = "strongpassword"
        
        # Encrypt
        encrypted = secrets_utils.encrypt_data(data, password)
        self.assertNotEqual(encrypted["data"], "secret_value")
        self.assertTrue("salt" in encrypted)
        
        # Decrypt
        decrypted = secrets_utils.decrypt_data(encrypted, password)
        self.assertEqual(decrypted, data)
        
        # Wrong password
        with self.assertRaises(Exception):
            secrets_utils.decrypt_data(encrypted, "wrong")

    def test_latex_escape(self):
        """Test latex escaping logic via export_utils internal helper or indirect output."""
        # Using a dummy dict to call create_latex
        data = {"body": "Test & % $ # _ { } ~ ^ \\", "user_info": {}}
        _, code = export_utils.create_latex(data)
        
        # Check for escaped characters
        self.assertIn(r"\&", code)
        self.assertIn(r"\%", code)
        self.assertIn(r"\textasciitilde{}", code)

    def test_profile_io(self):
        """Test profile saving and loading."""
        test_name = "TestProfile_Unique"
        data = {"full_name": "Tester"}
        
        # Save
        saved = profile_utils.save_profile(test_name, data)
        self.assertTrue(saved)
        
        # Load
        loaded = profile_utils.load_profile(test_name)
        self.assertEqual(loaded["full_name"], "Tester")
        
        # Cleanup
        path = os.path.join("profiles", f"{test_name}.json")
        if os.path.exists(path):
            os.remove(path)

if __name__ == '__main__':
    unittest.main()
