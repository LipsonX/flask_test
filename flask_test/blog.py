from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flask_test.auth import login_required
# from flask.db import get_db
from flask_test.orms import Post, db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    posts = Post.query.all()

    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    # post = Post.query.filter(Post.id == id).first()
    post = db.query(Post).filter(Post.id == id).first()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:

            post = Post(title, body, g.user.id)
            db.add(post)
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            # stmt = update(Post).where(Post.id == id).values(title=title, body=body)
            # db_session.execute(stmt)

            post.title = title
            post.body = body
            db.flush()
            db.commit()

            # stmt = Post.update().where(Post.id == id).values(title=title, body=body)
            # db.execute(stmt)
            #
            # stmt = update(Post).where(Post.id == id).values(title=title, body=body)
            # db.execute(stmt)
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db.delete(post)
    db.commit()
    return redirect(url_for("blog.index"))


@bp.route("/test")
def test():
    return {"fuck": "yeah"}
