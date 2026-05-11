from flask import Blueprint, render_template, redirect
from .forms import PostForm
from .models import Post, Tag
from app import db

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            posted=form.publish_date.data,
            user_id=form.author_id.data,
        )
        if len(form.tags.data) == 0:
            return redirect("/")
        tag_ids = form.tags.data
        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        for tag in tags:
            post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        return redirect("/")

    posts = Post.query.all()

    return render_template("index.html", posts=posts, form=form)
