from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import DeleteForm, CommentForm
from .. import db
from ..models import Role, User, Post, Tag, Permission, PostTag, Comment
from datetime import datetime
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    allTags = Tag.query.all()
    page_posts = []
    for post in posts:
        id = post.id
        title = post.title
        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
        text = post.text
        comments = post.comments.count()
        author = post.author
        postTag = PostTag.query.filter_by(post_id=post.id).all()
        tags = []
        for tag in postTag:
            name = Tag.query.filter_by(id=tag.tag_id).first().name
            tags.append([tag.tag_id, name])
        page_posts.append([id, title, time, text, comments, tags, author])
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
                        author = post.author
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
                        author = post.author
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
                        author = post.author
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
                        author = post.author
                        postTag = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in postTag:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
        selecttags = request.form.getlist('select_tags')
        for tag in selecttags:
            print tag
            tagid = Tag.query.filter_by(name=tag).first().id
            print "TagID:", tagid
            posttags = PostTag.query.filter_by(tag_id=tagid).all()
            posts = []
            for posttag in posttags:
                print "posttag:", posttag
                print "posttag.post_id:", posttag.post_id
                print "Post Query:", Post.query.filter_by(id=posttag.post_id).all()
                post = Post.query.filter_by(id=posttag.post_id).first()
                posts.append(post)
                print "posts:", posts
            posts.reverse()
            for post in posts:
                id = post.id
                title = post.title
                time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                text = post.text
                comments = post.comments.count()
                author = post.author
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
    return render_template('index.html', pagination=pagination, page_posts=page_posts, allTags=allTags)

@main.route('/newpost', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
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
            print "tags:", len(data['input_tag'])
            if data['input_tag'] == '':
                return render_template('error.html', message="Please include tags!")
            title = data['input_title']
            print "title:", title
            text = data['editor1']
            textLength = len(text)
            print textLength
            if len(text) > 3000:
                print len(text)
                return render_template('error.html', message="Text is too long! Please lower number of characters or remove some text edits.")
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
                print "posttag.post_id:", posttag.post_id
                print "posttag.tag_id:", posttag.tag_id
                db.session.add(posttag)
                db.session.commit()
            else:
                print "2"
                oldtag = Tag.query.filter_by(name=eachtag).first().id
                print oldtag
                posttag = PostTag(post_id=post.id, tag_id=oldtag)
                print "posttag.post_id:", posttag.post_id
                print "posttag.tag_id:", posttag.tag_id
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
    author = post.author
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
    return render_template('post.html', post=post, posts=[post], form=form, allComments=allComments,
                           comments=comments, pagination=pagination, page_posts=page_posts)

@main.route('/tag/<string:tag>', methods=['GET', 'POST'])
def tag(tag):
    page_posts = []
    tagid = Tag.query.filter_by(name=tag).first().id
    print "TagID:", tagid
    posttags = PostTag.query.filter_by(tag_id=tagid).all()
    posts = []
    for posttag in posttags:
        print "posttag:", posttag
        print "posttag.post_id:", posttag.post_id
        print "Post Query:", Post.query.filter_by(id=posttag.post_id).all()
        post = Post.query.filter_by(id=posttag.post_id).first()
        posts.append(post)
        print "posts:", posts
    posts.reverse()
    for post in posts:
        id = post.id
        title = post.title
        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
        text = post.text
        comments = post.comments.count()
        author = post.author
        postTag = PostTag.query.filter_by(post_id=post.id).all()
        tags = []
        for tag in postTag:
            name = Tag.query.filter_by(id=tag.tag_id).first().name
            tags.append([tag.tag_id, name])
        page_posts.append([id, title, time, text, comments, tags, author])
    return render_template('tagged_posts.html', page_posts=page_posts)

@main.route('/edit/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    form = CommentForm()
    if current_user != comment.author and not current_user.can(Permission.COMMENT):
        abort(403)
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash('The comment has been updated.')
    form.body.data = comment.body
    return render_template('edit_comment.html', form=form, comment=comment)

@main.route('/edit/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    tagList = Tag.query.with_entities(Tag.name).all()
    tagList = [r[0].encode('utf-8') for r in tagList]
    previousTagString = ""
    previousTagList = []
    postids = PostTag.query.filter_by(post_id=id).all()
    for postid in postids:
        print "tag_id:", postid.tag_id
        tagid = postid.tag_id
        print "tag_name:", Tag.query.filter_by(id=tagid).first().name
        tagname = Tag.query.filter_by(id=tagid).first().name
        previousTagList.append(tagname)
        previousTagString += tagname
        previousTagString += ", "
    previousTagString = previousTagString[:-2]
    print "previousTagString:", previousTagString
    print "previousTagList:", previousTagList
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if request.method == 'POST':
        data = request.form.copy()
        post.title = data['input_title']
        post.text = data['editor1']
        db.session.add(post)
        db.session.commit()
        print "newtags:", data['input_tag']
        tagsplit = data['input_tag'].split(', ')
        print "tagsplit:", tagsplit
        for eachtag in tagsplit:
            print "eachtag:", eachtag
            if eachtag not in tagList:
                print "1"
                newtag = Tag(name=eachtag)
                db.session.add(newtag)
                db.session.commit()
                posttag = PostTag(post_id=post.id, tag_id=newtag.id)
                print "posttag.post_id:", posttag.post_id
                print "posttag.tag_id:", posttag.tag_id
                db.session.add(posttag)
                db.session.commit()
            elif eachtag not in previousTagList:
                print "2"
                oldtag = Tag.query.filter_by(name=eachtag).first().id
                print "oldtag", oldtag
                posttag = PostTag(post_id=post.id, tag_id=oldtag)
                print "posttag.post_id:", posttag.post_id
                print "posttag.tag_id:", posttag.tag_id
                db.session.add(posttag)
                db.session.commit()
        for eachtag in previousTagList:
            if eachtag not in tagsplit:
                print "3"
                oldtag = Tag.query.filter_by(name=eachtag).first().id
                print "oldtag", oldtag
                print "post_id", post.id
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
    return render_template('moderate.html', allComments=allComments)

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
