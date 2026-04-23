from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from datetime import UTC, datetime, timedelta

from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy

os.environ["FLASK_CONFIG"] = "testing"
unittest.defaultTestLoader.sortTestMethodsUsing = None

BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
POSTS_DIR = APP_DIR / "posts"


def load_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def bootstrap_test_app():
    config_module = load_module("_lab6_test_config", APP_DIR / "config.py")

    flask_app = Flask(
        "app",
        root_path=str(APP_DIR),
        instance_path=str(BASE_DIR / "instance"),
        instance_relative_config=True,
        template_folder=str(APP_DIR / "templates"),
        static_folder=str(APP_DIR / "static"),
    )
    flask_app.config.from_object(config_module.config_by_name["testing"])
    Path(flask_app.instance_path).mkdir(parents=True, exist_ok=True)

    database = SQLAlchemy()
    database.init_app(flask_app)

    app_package = types.ModuleType("app")
    app_package.__file__ = str(APP_DIR / "__init__.py")
    app_package.__path__ = [str(APP_DIR)]
    app_package.app = flask_app
    app_package.db = database
    sys.modules["app"] = app_package

    app_models_module = types.ModuleType("app.models")
    app_models_module.db = database
    app_models_module.utcnow = utcnow
    sys.modules["app.models"] = app_models_module

    posts_package = types.ModuleType("app.posts")
    posts_package.__file__ = str(POSTS_DIR / "__init__.py")
    posts_package.__path__ = [str(POSTS_DIR)]
    posts_package.db = database
    posts_package.utcnow = utcnow
    posts_package.posts_bp = Blueprint(
        "posts",
        "app.posts",
        template_folder=str(POSTS_DIR / "templates"),
        static_folder=str(POSTS_DIR / "static"),
    )
    sys.modules["app.posts"] = posts_package

    posts_models_module = load_module("app.posts.models", POSTS_DIR / "models.py")
    load_module("app.posts.forms", POSTS_DIR / "forms.py")
    load_module("app.posts.views", POSTS_DIR / "views.py")
    load_module("app.views", APP_DIR / "views.py")

    flask_app.register_blueprint(posts_package.posts_bp, url_prefix="/post")
    return flask_app, database, posts_models_module.Post, posts_models_module.PostCategory


app, db, Post, PostCategory = bootstrap_test_app()


class PostsBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _create_post(self, **overrides):
        post = Post(
            title=overrides.get("title", "First post"),
            content=overrides.get("content", "This is enough content for testing."),
            posted=overrides.get("posted", utcnow()),
            category=overrides.get("category", PostCategory.NEWS),
            is_active=overrides.get("is_active", True),
            author=overrides.get("author", "Tester"),
        )
        db.session.add(post)
        db.session.commit()
        return post

    def test_create_post(self):
        with self.client.session_transaction() as flask_session:
            flask_session["username"] = "LabUser"

        response = self.client.post(
            "/post/create",
            data={
                "title": "ORM in Flask",
                "content": "This post explains how SQLAlchemy helps with persistence.",
                "publish_date": "2026-04-20T10:30",
                "category": "tech",
                "enabled": "y",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post added successfully.", response.data)
        self.assertIn(b"LabUser", response.data)

        with self.app.app_context():
            posts = db.session.scalars(db.select(Post)).all()
            self.assertEqual(len(posts), 1)
            self.assertEqual(posts[0].author, "LabUser")
            self.assertTrue(posts[0].is_active)

    def test_list_posts(self):
        with self.app.app_context():
            self._create_post(
                title="Older visible",
                posted=utcnow() - timedelta(days=2),
                is_active=True,
            )
            self._create_post(
                title="Newest visible",
                posted=utcnow(),
                is_active=True,
            )
            self._create_post(
                title="Hidden post",
                posted=utcnow() + timedelta(days=1),
                is_active=False,
            )

        response = self.client.get("/post/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Newest visible", page)
        self.assertIn("Older visible", page)
        self.assertNotIn("Hidden post", page)
        self.assertLess(page.index("Newest visible"), page.index("Older visible"))

    def test_view_post_detail(self):
        with self.app.app_context():
            post = self._create_post(title="Detail page")
            post_id = post.id

        response = self.client.get(f"/post/{post_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Detail page", response.data)

    def test_update_post(self):
        with self.app.app_context():
            post = self._create_post(title="Old title", category=PostCategory.NEWS)
            post_id = post.id

        with self.client.session_transaction() as flask_session:
            flask_session["username"] = "Editor"

        response = self.client.post(
            f"/post/{post_id}/update",
            data={
                "title": "Updated title",
                "content": "Updated content that still meets the minimum requirement.",
                "publish_date": "2026-04-21T08:45",
                "category": "publication",
                "enabled": "",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post updated successfully.", response.data)

        with self.app.app_context():
            updated_post = db.get_or_404(Post, post_id)
            self.assertEqual(updated_post.title, "Updated title")
            self.assertEqual(updated_post.author, "Editor")
            self.assertEqual(updated_post.category, PostCategory.PUBLICATION)
            self.assertFalse(updated_post.is_active)

    def test_delete_post(self):
        with self.app.app_context():
            post = self._create_post(title="Delete me")
            post_id = post.id

        detail_response = self.client.get(f"/post/{post_id}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Delete", detail_response.data)

        response = self.client.post(f"/post/{post_id}/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post deleted successfully.", response.data)

        with self.app.app_context():
            self.assertIsNone(db.session.get(Post, post_id))

    def test_404_not_found(self):
        response = self.client.get("/missing-page")

        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page not found", response.data)


def load_tests(loader, tests, pattern):
    ordered_suite = unittest.TestSuite()
    for test_name in (
        "test_create_post",
        "test_list_posts",
        "test_view_post_detail",
        "test_update_post",
        "test_delete_post",
        "test_404_not_found",
    ):
        ordered_suite.addTest(PostsBlueprintTestCase(test_name))
    return ordered_suite


if __name__ == "__main__":
    unittest.main()
