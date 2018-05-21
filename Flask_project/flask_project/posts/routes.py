import secrets
import os
from flask_project.models import User, Post
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_project.posts.forms import (PostForm, PostUpdateForm)
from flask_project import app, bcrypt, db, mail
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('your post has been created')
        return redirect(url_for('main.hello'))
    return render_template('create_post.html', title='New Post', form=form)



@posts.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_update.html', form=form)


@posts.route("/post/<int:post_id>/delete", methods=['GET','POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.hello'))


