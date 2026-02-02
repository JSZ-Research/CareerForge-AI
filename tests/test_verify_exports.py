import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import export_utils
from io import BytesIO

class TestExports(unittest.TestCase):
    def setUp(self):
        self.mock_data = {
            "body": "Test User\nAddress | Email\n\nDear Manager,\n\nThis is a **test** cover letter body.\n\n* Point 1\n* Point 2",
            "date_str": "January 1, 2024",
            "user_info": {
                "full_name": "Test User",
                "email": "test@example.com",
                "phone": "123-456-7890",
                "linkedin": "linkedin.com/in/test",
                "address": "123 Test St"
            },
            "hr_info": {
                "job_title": "Software Engineer",
                "company_name": "Test Corp"
            }
        }

    def test_create_docx(self):
        result = export_utils.create_docx(self.mock_data)
        self.assertIsInstance(result, BytesIO)
        self.assertTrue(result.getvalue().startswith(b"PK")) # DOCX signature

    def test_create_pdf(self):
        result = export_utils.create_pdf(self.mock_data)
        self.assertIsInstance(result, BytesIO)
        self.assertTrue(result.getvalue().startswith(b"%PDF")) # PDF signature

    def test_create_latex(self):
        data, code = export_utils.create_latex(self.mock_data)
        self.assertIsInstance(data, BytesIO)
        self.assertIsInstance(code, str)
        self.assertIn("\\documentclass", code)
        self.assertIn("Test User", code)

if __name__ == '__main__':
    unittest.main()
