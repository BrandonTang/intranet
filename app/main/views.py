from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import PostForm, DeleteForm
from .. import db
from ..models import Role, User, Post, Permission
from datetime import datetime
import markdown2

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(tag=form.tag.data, title=form.title.data, text=form.text.data, time=datetime.now(), author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
        db.session.commit()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)

@main.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(text=form.text.data).first()
        if post is None:
            post = Post(tag=form.tag.data, title=form.title.data, text=form.text.data, time=datetime.now(), author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('.index'))
    return render_template('new_post.html', form=form)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.tag = form.tag.data
        post.title = form.title.data
        post.text = form.text.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.tag.data = post.tag
    form.title.data = post.title
    form.text.data = post.text
    return render_template('edit_post.html', form=form)

@main.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('The post has been deleted.')
        return redirect(url_for('.index'))
    return render_template('delete_post.html', form=form)

@main.route('/tag/<string:tag>', methods=['GET', 'POST'])
def tag(tag):
    post = Post.query.all()
    print post
    for posts in Post.query.all():
        print posts.tag, tag
        if posts.tag != tag:
            post.remove(posts)
    return render_template('tagged_posts.html', posts=post)

@main.route('/mis')
def mis():
    return render_template('mis.html')

@main.route('/lmt')
def lmt():
    return render_template('lmt.html')