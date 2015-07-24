from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import DeleteForm, CommentForm
from .. import db
from ..models import Role, User, Post, Tag, Permission, PostTag, Comment
from datetime import datetime
from ..decorators import admin_required, permission_required
import mysql.connector

@main.route('/', methods=['GET', 'POST'])
def index():
    tagList = Tag.query.with_entities(Tag.name).all()
    tagList = [r[0].encode('utf-8') for r in tagList]
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    #Select tag for all tags with post_id = Post.id
    # cnx = mysql.connector.connect(host='localhost', port=3306, user='root', database='intranet')
    # cursor = cnx.cursor()
    # query = ("SELECT tag_id FROM posttag"
    #         "WHERE post_id = %s")
    # postid = Post.id
    # tags = cursor.execute(query, (postid))
    # print 'tags:', tags
    # cursor.close()
    # cnx.close()
    return render_template('index.html', posts=posts, pagination=pagination, tagList=tagList)

@main.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('error.html')

@main.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost(data=None):
    tagList = Tag.query.with_entities(Tag.name).all()
    tagList = [r[0].encode('utf-8') for r in tagList]
    print tagList
    if data or request.method == 'POST':
        data = request.form.copy()
        post = Post.query.filter_by(text=data['editor1']).first()
        if data['editor1'] == "":
            return render_template('error.html', message="Please fill out the text!")
        if post is None:
            title = data['input_title']
            print "title:", title
            text = data['editor1']
            print "text:", text
            print "time:", datetime.now()
            print "author:", current_user._get_current_object()
            post = Post(title=title, text=text, time=datetime.now(), author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
        tagsplit = data['input_tag'].split(', ')
        for eachtag in tagsplit:
            print "eachtag:", eachtag
            if eachtag not in tagList:
                print "1"
                newtag = Tag(name=eachtag)
                db.session.add(newtag)
                db.session.commit()
                posttag = PostTag(post_id=post.id, tag_id=newtag.id)
                db.session.add(posttag)
                db.session.commit()
            # else:
            #     print "2"
            #     cnx = mysql.connector.connect(host='localhost', port=3306, user='root', database='intranet')
            #     cursor = cnx.cursor()
            #     query = ("SELECT id FROM tags"
            #             "WHERE name = %s")
            #     tagname = eachtag
            #     oldtag = cursor.execute(query, (tagname))
            #     print 'oldtagid:', oldtag
            #     cursor.close()
            #     cnx.close()
            #     posttag = PostTag(post_id=post.id, tag_id=oldtag)
            #     db.session.add(posttag)
            #     db.session.commit()
        return redirect(url_for('.index'))
    return render_template('new_post.html', tagList=tagList)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        db.session.commit()
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if request.method == 'POST':
        data = request.form.copy()
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
    #Select posts for post with tag_id = Tag.id
    return render_template('tagged_posts.html', posts=posts)

@main.route('/mis')
def mis():
    return render_template('mis.html')

@main.route('/lmt')
def lmt():
    return render_template('lmt.html')

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
