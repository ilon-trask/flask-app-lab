from __future__ import annotations

import io
import os
import tempfile
import unittest

os.environ["FLASK_CONFIG"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db
from app.models import User


class AccountTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.upload_dir = tempfile.TemporaryDirectory()
        self.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PROFILE_PICS_FOLDER=self.upload_dir.name,
        )
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.session.remove()
        db.drop_all()
        db.create_all()

        self.user = User(username="anna", email="anna@example.com")
        self.user.set_password("secret1")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.upload_dir.cleanup()

    def test_register_login_and_update_account(self):
        response = self.client.post(
            "/register",
            data={
                "username": "maria",
                "email": "maria@example.com",
                "password": "secret123",
                "confirm_password": "secret123",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Реєстрація пройшла успішно".encode("utf-8"), response.data)

        response = self.client.post(
            "/login",
            data={"email": "maria@example.com", "password": "secret123"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Вхід виконано успішно.".encode("utf-8"), response.data)
        self.assertIn("maria@example.com".encode("utf-8"), response.data)

        response = self.client.post(
            "/account",
            data={
                "account-username": "maria_new",
                "account-email": "maria_new@example.com",
                "account-about_me": "Люблю Flask.",
                "account-image": (io.BytesIO(b"fake-image-data"), "avatar.jpg"),
                "account-submit": "1",
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Профіль оновлено.".encode("utf-8"), response.data)

        user = db.session.execute(
            db.select(User).where(User.username == "maria_new")
        ).scalar_one()
        self.assertEqual(user.email, "maria_new@example.com")
        self.assertEqual(user.about_me, "Люблю Flask.")
        self.assertNotEqual(user.image, "profile_default.jpg")
        self.assertTrue(os.path.exists(os.path.join(self.upload_dir.name, user.image)))
        self.assertIsNotNone(user.last_seen)

    def test_change_password(self):
        self.client.post(
            "/login",
            data={"email": "anna@example.com", "password": "secret1"},
            follow_redirects=True,
        )

        response = self.client.post(
            "/account",
            data={
                "password-current_password": "secret1",
                "password-new_password": "newsecret",
                "password-confirm_new_password": "newsecret",
                "password-submit": "1",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пароль успішно змінено.".encode("utf-8"), response.data)

        user = db.session.get(User, self.user.id)
        self.assertTrue(user.check_password("newsecret"))

    def test_account_requires_login(self):
        response = self.client.get("/account", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Увійдіть, щоб отримати доступ до профілю.".encode("utf-8"), response.data)
