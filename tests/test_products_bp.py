import unittest
from app import app


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        """Налаштування клієнта тестування перед кожним тестом."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_product_page(self):
        """Тест маршруту /product/<name>."""
        response = self.client.get("/product/Vacuum cleaner?price=100")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"VACUUM CLEANER", response.data)
        self.assertIn(b"100", response.data)

    def test_theproduct_page(self):
        """Тест маршруту /theproduct, який перенаправляє."""
        response = self.client.get("/theproduct", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MAKBOOK", response.data)
        self.assertIn(b"900", response.data)


if __name__ == "__main__":
    unittest.main()
