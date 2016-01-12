from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import DeleteForm, CommentForm
from .. import db
from ..models import Role, User, Post, Tag, Permission, PostTag, Comment
from datetime import datetime, timedelta
from ..decorators import admin_required, permission_required
import tweepy
import os
from os import environ, pardir

@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=int(os.environ.get('POSTS_PER_PAGE')), error_out=False)
    posts = pagination.items
    allTags = Tag.query.all()
    page_posts = []
    auth = tweepy.OAuthHandler(os.environ.get('consumer_key'), os.environ.get('consumer_secret'))
    auth.set_access_token(os.environ.get('auth_token'), os.environ.get('auth_secret'))
    api = tweepy.API(auth)
    recent_tweet = api.user_timeline(screen_name = 'nycrecords', count = 1, include_rts = True)
    for tweet in recent_tweet:
        tweet_datetime = (tweet.created_at - timedelta(hours=5)).strftime('%B %d, %Y %l:%M%p')
    for post in posts:
        id = post.id
        title = post.title
        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
        text = post.text
        comments = post.comments.count()
        author = ' '.join((post.author.username).split('_'))
        postTag = PostTag.query.filter_by(post_id=post.id).all()
        tags = []
        for tag in postTag:
            name = Tag.query.filter_by(id=tag.tag_id).first().name
            tags.append([tag.tag_id, name])
        page_posts.append([id, title, time, text, comments, tags, author])
    for page_post in page_posts:
        for tag in page_post[5]:
            if tag[1] == "#sticky":
                page_posts.insert(0, page_posts.pop(page_posts.index(page_post)))
    if request.method == 'POST':
        page_posts = []
        searchterm = request.form.get('search_term')
        searchoption = request.form.get('select_search_option')
        selecttags = request.form.getlist('select_tags')
        if searchterm == '':
            if selecttags == '':
                return render_template('index.html', pagination=pagination, page_posts=page_posts, allTags=allTags)
        else:
            if searchoption == 'all':
                for post in Post.query.all():
                    if searchterm in post.title:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        postTag = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in postTag:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
                    elif searchterm in post.text:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        postTag = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in postTag:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
            elif searchoption == 'title':
                for post in Post.query.all():
                    if searchterm in post.title:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        postTag = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in postTag:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
            elif searchoption == 'text':
                for post in Post.query.all():
                    if searchterm in post.text:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        postTag = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in postTag:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
        selecttags = request.form.getlist('select_tags')
        for tag in selecttags:
            tagid = Tag.query.filter_by(name=tag).first().id
            posttags = PostTag.query.filter_by(tag_id=tagid).all()
            posts = []
            for posttag in posttags:
                post = Post.query.filter_by(id=posttag.post_id).first()
                posts.append(post)
            posts.reverse()
            for post in posts:
                id = post.id
                title = post.title
                time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                text = post.text
                comments = post.comments.count()
                author = ' '.join((post.author.username).split('_'))
                postTag = PostTag.query.filter_by(post_id=post.id).all()
                tags = []
                for tag in postTag:
                    name = Tag.query.filter_by(id=tag.tag_id).first().name
                    tags.append([tag.tag_id, name])
                page_posts.append([id, title, time, text, comments, tags, author])
        page_posts_without_duplicates = []
        for page_post in page_posts:
            if page_post not in page_posts_without_duplicates:
                page_posts_without_duplicates.append(page_post)
        return render_template('tagged_posts.html', page_posts=page_posts_without_duplicates)
    return render_template('index.html', pagination=pagination, page_posts=page_posts, allTags=allTags, recent_tweet=recent_tweet, tweet_datetime=tweet_datetime)


@main.route('/newpost', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def newpost(data=None):
    tagList = Tag.query.with_entities(Tag.name).all()
    tagList = [r[0].encode('utf-8') for r in tagList]
    if data or request.method == 'POST':
        data = request.form.copy()
        post = Post.query.filter_by(text=data['editor1']).first()
        if data['editor1'] == "":
            return render_template('error.html', message="Please fill out the text!")
        if post is None:
            if data['input_tag'] == '':
                return render_template('error.html', message="Please include tags!")
            title = data['input_title']
            text = data['editor1']
            textLength = len(text)
            if len(text) > 8000:
                return render_template('error.html', message="Text is too long! Please lower number of characters or remove some text formatting.")
            time = datetime.now() - timedelta(hours=4)
            post = Post(title=title, text=text, time=time, author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
        tagsplit = data['input_tag'].split(', ')
        for eachtag in tagsplit:
            if eachtag not in tagList:
                newtag = Tag(name=eachtag)
                db.session.add(newtag)
                db.session.commit()
                posttag = PostTag(post_id=post.id, tag_id=newtag.id)
                db.session.add(posttag)
                db.session.commit()
            else:
                oldtag = Tag.query.filter_by(name=eachtag).first().id
                posttag = PostTag(post_id=post.id, tag_id=oldtag)
                db.session.add(posttag)
                db.session.commit()
        return redirect(url_for('.index'))
    return render_template('new_post.html', tagList=tagList)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    page_posts = []
    id = post.id
    title = post.title
    time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
    text = post.text
    comments = post.comments.count()
    author = ' '.join((post.author.username).split('_'))
    avatar = post.author.avatar(32)
    postTag = PostTag.query.filter_by(post_id=post.id).all()
    tags = []
    for tag in postTag:
        name = Tag.query.filter_by(id=tag.tag_id).first().name
        tags.append([tag.tag_id, name])
    page_posts.append([id, title, time, text, comments, tags, author])
    form = CommentForm()
    allComments = []
    for comment in post.comments:
        allComments.append(comment)
    allComments.reverse()
    allCommentsCount = len(allComments)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been posted.')
        db.session.commit()
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               int(os.environ.get('COMMENTS_PER_PAGE')) + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=int(os.environ.get('COMMENTS_PER_PAGE')), error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, posts=[post], form=form, allComments=allComments, allCommentsCount=allCommentsCount,
                           comments=comments, pagination=pagination, page_posts=page_posts, avatar=avatar)


@main.route('/tag/<string:tag>', methods=['GET', 'POST'])
def tag(tag):
    page_posts = []
    tagid = Tag.query.filter_by(name=tag).first().id
    posttags = PostTag.query.filter_by(tag_id=tagid).all()
    posts = []
    for posttag in posttags:
        post = Post.query.filter_by(id=posttag.post_id).first()
        posts.append(post)
    posts.reverse()
    for post in posts:
        id = post.id
        title = post.title
        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
        text = post.text
        comments = post.comments.count()
        author = ' '.join((post.author.username).split('_'))
        postTag = PostTag.query.filter_by(post_id=post.id).all()
        tags = []
        for tag in postTag:
            name = Tag.query.filter_by(id=tag.tag_id).first().name
            tags.append([tag.tag_id, name])
        page_posts.append([id, title, time, text, comments, tags, author])
    return render_template('tagged_posts.html', page_posts=page_posts)


@main.route('/edit/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    tagList = Tag.query.with_entities(Tag.name).all()
    tagList = [r[0].encode('utf-8') for r in tagList]
    previousTagString = ""
    previousTagList = []
    postids = PostTag.query.filter_by(post_id=id).all()
    for postid in postids:
        tagid = postid.tag_id
        tagname = Tag.query.filter_by(id=tagid).first().name
        previousTagList.append(tagname)
        previousTagString += tagname
        previousTagString += ", "
    previousTagString = previousTagString[:-2]
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if request.method == 'POST':
        data = request.form.copy()
        post.title = data['input_title']
        post.text = data['editor1']
        db.session.add(post)
        db.session.commit()
        tagsplit = data['input_tag'].split(', ')
        for eachtag in tagsplit:
            if eachtag not in tagList:
                newtag = Tag(name=eachtag)
                db.session.add(newtag)
                db.session.commit()
                posttag = PostTag(post_id=post.id, tag_id=newtag.id)
                db.session.add(posttag)
                db.session.commit()
            elif eachtag not in previousTagList:
                oldtag = Tag.query.filter_by(name=eachtag).first().id
                posttag = PostTag(post_id=post.id, tag_id=oldtag)
                db.session.add(posttag)
                db.session.commit()
        for eachtag in previousTagList:
            if eachtag not in tagsplit:
                oldtag = Tag.query.filter_by(name=eachtag).first().id
                PostTag.query.filter_by(post_id=post.id, tag_id=oldtag).delete()
                db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    return render_template('edit_post.html', post=post, tagList=tagList, previousTagString=previousTagString)


@main.route('/delete/post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER) and not current_user.is_director():
        abort(403)
    form = DeleteForm()
    if form.validate_on_submit():
        posttags = PostTag.query.filter_by(post_id=id).all()
        for posttag in posttags:
            db.session.delete(posttag)
        comments = Comment.query.filter_by(post_id=id).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(post)
        db.session.commit()
        flash('The post has been deleted.')
        return redirect(url_for('.index'))
    return render_template('delete_post.html', form=form)


@main.route('/mis')
def mis():
    return render_template('mis.html')


@main.route('/lmt')
def lmt():
    return render_template('lmt.html')


@main.route('/agencypolicies')
def agencypolicies():
    return render_template('agencypolicies.html')


@main.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('error.html')


@main.route('/moderate/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate(id):
    post = Post.query.get_or_404(id)
    allComments = []
    comments = post.comments
    for comment in comments:
        allComments.append(comment)
    allComments.reverse()
    allCommentsCount = len(allComments)
    return render_template('moderate.html', allComments=allComments, allCommentsCount=allCommentsCount)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    post = Comment.query.filter_by(id=id).first().post
    return redirect(url_for('.moderate', id=post.id))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    post = Comment.query.filter_by(id=id).first().post
    return redirect(url_for('.moderate', id=post.id))


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    users = User.query.all()
    user = current_user.username
    role = current_user.role.name
    email = current_user.email
    posts = current_user.posts.count()
    comments = current_user.comments.count()
    avatar = current_user.avatar(128)
    employees = []
    directors = []
    for eachuser in User.query.all():
        if eachuser.role.name == 'Employee':
            employees.append(eachuser.username)
        elif eachuser.role.name == 'Director':
            directors.append(eachuser.username)
    if request.method == 'POST':
        editusername = request.form.getlist('edit_username')
        if len(editusername) > 0:
            editusername = [r.encode('utf-8') for r in editusername][0]
        selectemployee = request.form.getlist('select_employee')
        selectdirector = request.form.getlist('select_director')
        selectuser = request.form.getlist('select_account')
        if selectemployee == '':
            if selectdirector == '':
                if selectuser == '':
                    if editusername == user:
                        return render_template('profile.html', user=user, users=users, role=role, email=email, posts=posts, comments=comments, avatar=avatar,
                            employees=employees, directors=directors)
        else:
            if editusername != user and len(editusername) > 0:
                current_user.username = editusername
            for employee in selectemployee:
                for user in User.query.all():
                    if employee == user.username:
                        user.role = Role.query.filter_by(permissions=14).first()
            for director in selectdirector:
                for user in User.query.all():
                    if director == user.username:
                        user.role = Role.query.filter_by(permissions=0xff).first()
            for id in selectuser:
                account = User.query.get_or_404(id)
                db.session.delete(account)
                db.session.commit()
            return render_template('profile.html', user=user, users=users, role=role, email=email, posts=posts, comments=comments, avatar=avatar, 
                    employees=employees, directors=directors)
    return render_template('profile.html', user=user, users=users, role=role, email=email, posts=posts, comments=comments, avatar=avatar, 
        employees=employees, directors=directors)


@main.route('/edit/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    form = CommentForm()
    if current_user != comment.author and not current_user.can(Permission.COMMENT):
        abort(403)
    if form.validate_on_submit():
        if "[Edited]" not in form.body.data:
            comment.body = "[Edited] " + form.body.data
        else:
            comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash('The comment has been updated.')
        return redirect(url_for('.post', id=comment.post_id))
    form.body.data = comment.body
    return render_template('edit_comment.html', form=form, comment=comment)


@main.route('/delete/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    form = DeleteForm()
    if current_user != comment.author and not current_user.can(Permission.COMMENT):
        abort(403)
    if form.validate_on_submit():
        db.session.delete(comment)
        db.session.commit()
        flash('The comment has been deleted.')
        return redirect(url_for('.post', id=comment.post_id))
    return render_template('delete_comment.html', form=form, comment=comment)
