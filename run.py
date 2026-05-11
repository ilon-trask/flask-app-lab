from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


# from .models import Post, User, Tag
# from app import db

# user1 = User(username="user1", email="user1@example.com", password="password123")
# user2 = User(username="user2", email="user2@example.com", password="password123")

# post1 = Post(
#     title="post1 user1",
#     content="Lorem ipsum dolor sit amet",
#     category="publication",
#     user=user1,
# )
# post2 = Post(
#     title="post2 user2",
#     content="Lorem ipsum dolor sit amet",
#     category="publication",
#     user=user2,
# )
# post3 = Post(
#     title="post3 user1",
#     content="Lorem ipsum dolor sit amet",
#     category="publication",
#     user=user1,
# )
# post4 = Post(
#     title="post4 user2",
#     content="Lorem ipsum dolor sit amet",
#     category="publication",
#     user=user2,
# )


# db.session.add_all([post1, post2, post3, post4])
# db.session.commit()


# from .models import Post, User, Tag
# from app import db

# tag1 = Tag(name="animals")
# tag2 = Tag(name="tech")
# tag3 = Tag(name="cooking")
# tag4 = Tag(name="writing")

# post1 = Post.query.where(Post.id == 1).first()
# post3 = Post.query.where(Post.id == 3).first()


# post1.tags.append(tag1)
# post1.tags.append(tag3)

# post3.tags.append(tag1)
# post3.tags.append(tag2)
# post3.tags.append(tag4)

# db.session.add_all([tag1, tag2, tag3, tag4])
# db.session.add_all([post1, post3])

# db.session.commit()


# from app.models import Post, User, Tag

# post1 = Post.query.where(Post.id == 1).first()

# tag1 = Tag.query.where(Tag.id == 1).first()

# print("tags of post1 \n")
# for tag in post1.tags:
#     print("name:", tag.name, ", ")

# print("\n")

# print("posts of tag1")
# for post in tag1.posts:
#     print("title:", post.title, ", ")
