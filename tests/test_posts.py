from __future__ import annotations

import os
import tempfile
import unittest

os.environ["FLASK_CONFIG"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db
from app.models import User
from app.posts.models import Post, Tag


class PostsTestCase(unittest.TestCase):
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

        self.user_1 = User(username="anna", email="anna@example.com")
        self.user_1.set_password("secret1")
        self.user_2 = User(username="bob", email="bob@example.com")
        self.user_2.set_password("secret2")
        self.tag_python = Tag(name="python")
        self.tag_flask = Tag(name="flask")
        db.session.add_all([self.user_1, self.user_2, self.tag_python, self.tag_flask])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.upload_dir.cleanup()

    def test_home_redirects_to_posts(self):
        response = self.client.get("/", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пости, автори та теги".encode("utf-8"), response.data)

    def test_create_edit_and_delete_post_with_relationships(self):
        response = self.client.post(
            "/post/add",
            data={
                "title": "Перший пост",
                "content": "Контент для перевірки ORM зв'язків.",
                "author_id": self.user_2.id,
                "tags": [self.tag_python.id, self.tag_flask.id],
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пост успішно створено.".encode("utf-8"), response.data)
        self.assertIn("Автор: bob".encode("utf-8"), response.data)
        self.assertIn("#python".encode("utf-8"), response.data)
        self.assertIn("#flask".encode("utf-8"), response.data)

        post = db.session.execute(db.select(Post)).scalar_one()
        self.assertEqual(post.author.username, "bob")
        self.assertEqual({tag.name for tag in post.tags}, {"python", "flask"})
        self.assertEqual([item.title for item in self.user_2.posts], ["Перший пост"])
        self.assertEqual(list(self.tag_python.posts)[0].title, "Перший пост")

        response = self.client.post(
            f"/post/{post.id}/edit",
            data={
                "title": "Оновлений пост",
                "content": "Новий зміст",
                "author_id": self.user_1.id,
                "tags": [self.tag_flask.id],
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пост оновлено.".encode("utf-8"), response.data)
        self.assertIn("Автор: anna".encode("utf-8"), response.data)
        self.assertIn("#flask".encode("utf-8"), response.data)

        db.session.refresh(post)
        self.assertEqual(post.author.username, "anna")
        self.assertEqual([tag.name for tag in post.tags], ["flask"])

        response = self.client.post(f"/post/{post.id}/delete", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пост видалено.".encode("utf-8"), response.data)
        self.assertEqual(db.session.execute(db.select(Post)).scalars().all(), [])

    def test_form_requires_required_fields(self):
        response = self.client.post(
            "/post/add",
            data={
                "title": "",
                "content": "",
                "author_id": "",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.".encode("utf-8"), response.data)

    def test_missing_post_returns_404(self):
        response = self.client.get("/post/999")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Сторінку не знайдено".encode("utf-8"), response.data)
