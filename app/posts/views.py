from __future__ import annotations

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db

from . import posts_bp
from .forms import PostForm
from .models import Post, Tag


@posts_bp.route("/")
def list_posts():
    posts = db.session.execute(
        db.select(Post).order_by(Post.created_at.desc(), Post.id.desc())
    ).scalars()
    return render_template("posts/posts.html", posts=posts)


@posts_bp.route("/<int:post_id>")
def detail_post(post_id: int):
    post = db.get_or_404(Post, post_id)
    return render_template("posts/detail_post.html", post=post)


@posts_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            tags=_resolve_tags(form.tags.data),
        )
        db.session.add(post)
        db.session.commit()
        flash("Пост успішно створено.", "success")
        return redirect(url_for("posts.detail_post", post_id=post.id))

    return render_template("posts/add_post.html", form=form, page_title="Новий пост")


@posts_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    post = db.get_or_404(Post, post_id)
    _ensure_author(post)
    form = PostForm(obj=post)

    if not form.is_submitted():
        form.tags.data = [tag.id for tag in post.tags]

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.tags = _resolve_tags(form.tags.data)
        db.session.commit()
        flash("Пост оновлено.", "success")
        return redirect(url_for("posts.detail_post", post_id=post.id))

    return render_template(
        "posts/add_post.html",
        form=form,
        page_title=f"Редагування: {post.title}",
    )


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post = db.get_or_404(Post, post_id)
    _ensure_author(post)
    db.session.delete(post)
    db.session.commit()
    flash("Пост видалено.", "success")
    return redirect(url_for("posts.list_posts"))


def _resolve_tags(tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []

    return list(
        db.session.execute(
            db.select(Tag).where(Tag.id.in_(tag_ids)).order_by(Tag.name)
        ).scalars()
    )


def _ensure_author(post: Post) -> None:
    if post.author_id != current_user.id:
        abort(403)
