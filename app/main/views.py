from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import PostForm, DeleteForm
from .. import db
from ..models import Role, User, Post, Category, Permission
from datetime import datetime

@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)

@main.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('error.html')

@main.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost(data=None):
    if data or request.method == 'POST':
        data = request.form.copy()
        post = Post.query.filter_by(text=data['editor1']).first()
        if data['editor1'] == "":
            return render_template('error.html', message="Please fill out the text!")
        if post is None:
            tag = data['input_tag']
            categories = data['input_category']
            title = data['input_title']
            text = data['editor1']
            post = Post(tag=tag, title=title, text=text, time=datetime.now(), author=current_user._get_current_object())
            db.session.add(post)
            categories = categories.split(',')
            for eachcategory in categories:
                category = Category(name=eachcategory, categorypost=post)
                db.session.add(category)
            db.session.commit()
        return redirect(url_for('.index'))
    return render_template('new_post.html')

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
    if request.method == 'POST':
        data = request.form.copy()
        post.tag = data['input_tag']
        post.category = data['input_category']
        post.title = data['input_title']
        post.text = data['editor1']
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    return render_template('edit_post.html', post=post)

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
    posts = Post.query.all()
    for post in Post.query.all():
        if post.tag != tag:
            posts.remove(post)
    posts.sort(reverse=True)
    return render_template('tagged_posts.html', posts=posts)

@main.route('/category/<string:category>', methods=['GET', 'POST'])
def category(category):
    posts = Posts.query.all()
    for post in Post.query.all():
        for eachcategory in post.categories:
            if eachcategory != category:
                posts.remove(post)
    posts.sort(reverse=True)
    return render_template('categorized_posts.html', posts=posts)

@main.route('/mis')
def mis():
    return render_template('mis.html')

@main.route('/lmt')
def lmt():
    return render_template('lmt.html')