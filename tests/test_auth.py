from __future__ import annotations

import os
import unittest

os.environ["FLASK_CONFIG"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db
from app.models import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.session.remove()
        db.drop_all()
        db.create_all()

        self.user = User(username="maria", email="maria@example.com")
        self.user.set_password("secret12")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_register_login_account_and_logout_flow(self):
        register_response = self.client.post(
            "/register",
            data={
                "username": "ivan",
                "email": "ivan@example.com",
                "password": "super123",
                "confirm_password": "super123",
            },
            follow_redirects=True,
        )

        self.assertEqual(register_response.status_code, 200)
        self.assertIn(
            "Реєстрація успішна. Тепер увійдіть у систему.".encode("utf-8"),
            register_response.data,
        )

        user = db.session.execute(
            db.select(User).where(User.email == "ivan@example.com")
        ).scalar_one()
        self.assertTrue(user.check_password("super123"))

        login_response = self.client.post(
            "/login",
            data={"email": "ivan@example.com", "password": "super123", "remember": "y"},
            follow_redirects=True,
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Дані поточного користувача".encode("utf-8"), login_response.data)
        self.assertIn("ivan@example.com".encode("utf-8"), login_response.data)

        logout_response = self.client.get("/logout", follow_redirects=True)

        self.assertEqual(logout_response.status_code, 200)
        self.assertIn("Ви вийшли з акаунта.".encode("utf-8"), logout_response.data)
        self.assertIn("Увійти до системи".encode("utf-8"), logout_response.data)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/login",
            data={"email": "maria@example.com", "password": "wrongpass"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Неправильна електронна пошта або пароль.".encode("utf-8"),
            response.data,
        )

    def test_account_requires_authenticated_user(self):
        response = self.client.get("/account", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Увійти до системи".encode("utf-8"), response.data)

    def test_users_page_shows_registered_users_and_count(self):
        response = self.client.get("/users")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Registered Users".encode("utf-8"), response.data)
        self.assertIn("Total users: 1".encode("utf-8"), response.data)
        self.assertIn("maria".encode("utf-8"), response.data)
        self.assertIn("maria@example.com".encode("utf-8"), response.data)

    def test_users_page_shows_empty_state_when_no_users(self):
        db.session.delete(self.user)
        db.session.commit()

        response = self.client.get("/users")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Total users: 0".encode("utf-8"), response.data)
        self.assertIn("No registered users yet".encode("utf-8"), response.data)
