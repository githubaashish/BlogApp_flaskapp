import secrets
import os
from flask_project.models import User, Post
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_project.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                                       RequestResetForm, ResetPasswordForm)
from flask_project.posts.forms import (PostForm, PostUpdateForm)
from flask_project import app, bcrypt, db, mail
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from flask_project.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm() 
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'account created for {form.username.data}', 'success')
        return redirect(url_for('main.hello'))
    return render_template("register.html",form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('you have been logged in','success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else  render_template("success.html")
        else : 
            flash('Login credentails incorrect')
    return render_template("login.html", form=form)



@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.hello'))



@users.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data: 
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        return render_template("account.html", form=form)
    elif request.method == 'GET' : 
        form.username.data = current_user.username
        form.email.data = current_user.email 
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", form=form, image_file=image_file)



@users.route("/user/<string:username>")
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=2)
    return render_template("user_post.html", posts=posts, user=user)



@users.route("/reset_password", methods=['GET','POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('email send to your mail id , please click the link to reset the password')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", form=form)


@users.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None : 
        flash('token is expired or invalid')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
        user.password = hashed_password
        db.session.commit()
        flash(f'password is updated , Please login')
        return render_template("login.html")
    return render_template("reset_password.html", form=form)


