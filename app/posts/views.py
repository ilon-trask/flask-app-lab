from __future__ import annotations

from flask import flash, redirect, render_template, request, session, url_for

from .. import db
from . import posts_bp
from .forms import PostForm
from .models import Post, PostCategory


@posts_bp.route("", strict_slashes=False)
@posts_bp.route("/")
def list_posts():
    stmt = db.select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())
    posts = db.session.scalars(stmt).all()
    return render_template("posts/posts.html", posts=posts)


@posts_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            category=PostCategory(form.category.data),
            is_active=form.enabled.data,
            author=session.get("username", "Anonymous"),
        )
        db.session.add(post)
        db.session.commit()
        flash("Post added successfully.", "success")
        return redirect(url_for("posts.detail_post", id=post.id))

    return render_template("posts/add_post.html", form=form, page_title="Add Post")


@posts_bp.route("/<int:id>")
def detail_post(id: int):
    post = db.get_or_404(Post, id)
    return render_template("posts/detail_post.html", post=post)


@posts_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id: int):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)

    if request.method == "GET":
        form.publish_date.data = post.posted
        form.enabled.data = post.is_active
        form.category.data = post.category.value

    if form.validate_on_submit():
        form.populate_obj(post)
        post.is_active = form.enabled.data
        post.author = session.get("username", post.author or "Anonymous")
        post.category = PostCategory(form.category.data)
        db.session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for("posts.detail_post", id=post.id))

    return render_template("posts/add_post.html", form=form, page_title="Edit Post")


@posts_bp.route("/<int:id>/delete", methods=["POST"])
def delete_post(id: int):
    post = db.get_or_404(Post, id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for("posts.list_posts"))
