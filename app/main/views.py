import datetime
from datetime import timedelta, datetime
import os
from os import environ
from flask import render_template, redirect, url_for, abort, flash, request, session
from flask.ext.login import login_required, current_user
import tweepy
from werkzeug import secure_filename
from . import main
from .forms import DeleteForm, CommentForm, NameForm
from .. import db
from ..models import Role, User, Post, Tag, Permission, PostTag, Comment
from ..decorators import permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    """
    Return the main homepage containing all submitted posts with their corresponding tags,
    search bar, and a new post button.

    Only directors or administrators will be able to see or use the new post feature.
    """
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=int(os.environ.get('POSTS_PER_PAGE')),
                                                                error_out=False)
    posts = pagination.items
    all_tags = Tag.query.all()
    page_posts = []
    auth = tweepy.OAuthHandler(os.environ.get('consumer_key'), os.environ.get('consumer_secret'))
    auth.set_access_token(os.environ.get('auth_token'), os.environ.get('auth_secret'))
    api = tweepy.API(auth)
    recent_tweet = api.user_timeline(screen_name='nycrecords', count=1, include_rts=True)
    for tweet in recent_tweet:
        tweet_datetime = (tweet.created_at - timedelta(hours=4)).strftime('%B %d, %Y %l:%M%p')
        if Post.query.filter_by(text=tweet.text).first() is None:
            tweet_title = 'Twitter - @nycrecords: ' + str((tweet.created_at - timedelta(hours=4)).strftime('%B %d, %Y'))
            post = Post(title=tweet_title, text=tweet.text, time=(tweet.created_at - timedelta(hours=4)), author=User.query.filter_by(username='testuser1').first())
            db.session.add(post)
            db.session.commit()
            add_twitter_tag = Tag(name='#twitter')
            db.session.add(add_twitter_tag)
            db.session.commit()
            twitter_tag = PostTag(post_id=post.id, tag_id=Tag.query.filter_by(name='#twitter').first().id)
            db.session.add(twitter_tag)
            db.session.commit()
    for post in posts:
        id = post.id
        title = post.title
        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
        text = post.text
        comments = post.comments.count()
        author = post.author
        post_tags = PostTag.query.filter_by(post_id=post.id).all()
        tags = []
        for tag in post_tags:
            name = Tag.query.filter_by(id=tag.tag_id).first().name
            tags.append([tag.tag_id, name])
        page_posts.append([id, title, time, text, comments, tags, author])
    for page_post in page_posts:
        for tag in page_post[5]:
            if tag[1] == "#sticky":
                page_posts.insert(0, page_posts.pop(page_posts.index(page_post)))
    if request.method == 'POST':
        page_posts = []
        search_term = request.form.get('search_term')
        search_option = request.form.get('select_search_option')
        select_tags = request.form.getlist('select_tags')
        if search_term == '':
            if select_tags == '':
                return render_template('index.html', pagination=pagination, page_posts=page_posts,
                                       all_tags=all_tags)
        else:
            if search_option == 'all':
                for post in Post.query.all():
                    if search_term in post.title:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        post_tags = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in post_tags:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
                    elif search_term in post.text:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        post_tags = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in post_tags:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
            elif search_option == 'title':
                for post in Post.query.all():
                    if search_term in post.title:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        post_tags = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in post_tags:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
            elif search_option == 'text':
                for post in Post.query.all():
                    if search_term in post.text:
                        id = post.id
                        title = post.title
                        time = post.time.strftime("%B %d, %Y %l:%M%p %Z")
                        text = post.text
                        comments = post.comments.count()
                        author = ' '.join((post.author.username).split('_'))
                        post_tags = PostTag.query.filter_by(post_id=post.id).all()
                        tags = []
                        for tag in post_tags:
                            name = Tag.query.filter_by(id=tag.tag_id).first().name
                            tags.append([tag.tag_id, name])
                        page_posts.append([id, title, time, text, comments, tags, author])
        select_tags = request.form.getlist('select_tags')
        for tag in select_tags:
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
                post_tags = PostTag.query.filter_by(post_id=post.id).all()
                tags = []
                for tag in post_tags:
                    name = Tag.query.filter_by(id=tag.tag_id).first().name
                    tags.append([tag.tag_id, name])
                page_posts.append([id, title, time, text, comments, tags, author])
        page_posts_without_duplicates = []
        for page_post in page_posts:
            if page_post not in page_posts_without_duplicates:
                page_posts_without_duplicates.append(page_post)
        return render_template('tagged_posts.html', page_posts=page_posts_without_duplicates)
    return render_template('index.html', pagination=pagination, page_posts=page_posts,
                           all_tags=all_tags, recent_tweet=recent_tweet, tweet_datetime=tweet_datetime)


@main.route('/newpost', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def newpost(data=None):
    """
    Return the page for creating a new post containing tags, title, and text.

    Keyword arguments:
    data -- initialization of data (default None)
    """
    tag_list = Tag.query.with_entities(Tag.name).all()
    tag_list = [r[0].encode('utf-8') for r in tag_list]
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
            if len(text) > 8000:
                return render_template('error.html', message='Text is too long! Please lower number of characters or remove some text formatting.')
            time = datetime.now()
            post = Post(title=title, text=text, time=time, author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
        tag_split = data['input_tag'].split(', ')
        for each_tag in tag_split:
            if Tag.query.filter_by(name='').first() != None:
                db.session.delete(Tag.query.filter_by(name='').first())
            if each_tag[0] != '#':
                each_tag = '#' + each_tag
            if each_tag not in tag_list:
                newtag = Tag(name=each_tag)
                db.session.add(newtag)
                db.session.commit()
                posttag = PostTag(post_id=post.id, tag_id=newtag.id)
                db.session.add(posttag)
                db.session.commit()
            else:
                oldtag = Tag.query.filter_by(name=each_tag).first().id
                posttag = PostTag(post_id=post.id, tag_id=oldtag)
                db.session.add(posttag)
                db.session.commit()
        return redirect(url_for('.index'))
    return render_template('new_post.html', tag_list=tag_list)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    """
    Return the page of a specific post containing the post itself, comments, and comment box if logged in.

    Keyword arguments:
    id -- the post id
    """
    post = Post.query.get_or_404(id)
    page_posts = []
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
    return render_template('post.html', post=post, posts=[post], form=form, allComments=allComments,
                           allCommentsCount=allCommentsCount, comments=comments, pagination=pagination,
                           page_posts=page_posts)


@main.route('/tag/<string:tag>', methods=['GET', 'POST'])
def tag(tag):
    """
    Return the page containing all posts with the chosen tag.

    Keyword arguments:
    tag -- the selected tag
    """
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
    """
    Return the page for editing a specific post containing possible edits for tags, title, and text.

    Keyword arguments:
    id -- the post id
    """
    tag_list = Tag.query.with_entities(Tag.name).all()
    tag_list = [r[0].encode('utf-8') for r in tag_list]
    previous_tag_string = ""
    previous_tag_list = []
    postids = PostTag.query.filter_by(post_id=id).all()
    for postid in postids:
        tagid = postid.tag_id
        tagname = Tag.query.filter_by(id=tagid).first().name
        previous_tag_list.append(tagname)
        previous_tag_string += tagname
        previous_tag_string += ", "
    previous_tag_string = previous_tag_string[:-2]
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if request.method == 'POST':
        data = request.form.copy()
        post.title = data['input_title']
        post.text = data['editor1']
        db.session.add(post)
        db.session.commit()
        tag_split = data['input_tag'].split(', ')
        for each_tag in tag_split:
            if Tag.query.filter_by(name='').first() != None:
                db.session.delete(Tag.query.filter_by(name='').first())
            if len(tag_split[0]) != 0 and each_tag[0] != '#':
                each_tag = '#' + each_tag
            if each_tag not in tag_list:
                newtag = Tag(name=each_tag)
                db.session.add(newtag)
                db.session.commit()
                posttag = PostTag(post_id=post.id, tag_id=newtag.id)
                db.session.add(posttag)
                db.session.commit()
            elif each_tag not in previous_tag_list:
                oldtag = Tag.query.filter_by(name=each_tag).first().id
                posttag = PostTag(post_id=post.id, tag_id=oldtag)
                db.session.add(posttag)
                db.session.commit()
        for each_tag in previous_tag_list:
            if each_tag not in tag_split:
                oldtag = Tag.query.filter_by(name=each_tag).first().id
                PostTag.query.filter_by(post_id=post.id, tag_id=oldtag).delete()
                db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    return render_template('edit_post.html', post=post, tag_list=tag_list, previous_tag_string=previous_tag_string)


@main.route('/delete/post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    """
    Return the confirmation page for deleting a post.

    Keyword arguments:
    id -- the post id
    """
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
    """
    Return the Management and Information Services information page.
    """
    return render_template('mis.html')


@main.route('/lmt')
def lmt():
    """
    Return the Labor Management Team information page.
    """
    return render_template('lmt.html')


@main.route('/archives')
def archives():
    """
    Return the Municipal Archives information page.
    """
    return render_template('archives.html')


@main.route('/agencypolicies')
def agencypolicies():
    """
    Return the agency policies page.
    """
    return render_template('agencypolicies.html')


@main.route('/eeo')
def eeo():
    """
    Return the EEO information page.
    """
    return render_template('eeo.html')


@main.route('/error', methods=['GET', 'POST'])
def error():
    """
    Return the error page.
    """
    return render_template('error.html')


@main.route('/tweets')
def tweets():
    """
    Return all tweets posted on the intranet.
    """
    previous_tweets = []
    for post in Post.query.all():
        if 'Twitter - @nycrecords: ' in post.title:
            previous_tweets.append(post)
    for post in previous_tweets:
        post.time = post.time.strftime('%B %d, %Y %l:%M%p')
    previous_tweets.reverse()
    return render_template('tweets.html', previous_tweets=previous_tweets)


@main.route('/moderate/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate(id):
    """
    Return the moderation page for comments from a specific post.

    Keyword arguments:
    id -- the post id
    """
    avatar = current_user.avatar
    post = Post.query.get_or_404(id)
    allComments = []
    comments = post.comments
    for comment in comments:
        allComments.append(comment)
    allComments.reverse()
    allCommentsCount = len(allComments)
    return render_template('moderate.html', avatar=avatar, allComments=allComments, allCommentsCount=allCommentsCount)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    """
    Enable a comment and redirect to the moderation page.

    Keyword arguments:
    id -- the comment id
    """
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    post = Comment.query.filter_by(id=id).first().post
    return redirect(url_for('.moderate', id=post.id))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    """
    Disable a comment and redirect to the moderation page.

    Keyword arguments:
    id -- the comment id
    """
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    post = Comment.query.filter_by(id=id).first().post
    return redirect(url_for('.moderate', id=post.id))


def allowed_file(filename):
    """
    Define the extension types of a file allowed for uploading.

    Keyword arguments:
    filename -- the uploaded filename
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in os.environ.get('ALLOWED_EXTENSIONS')


@main.route('/edituserinfo', methods=['GET', 'POST'])
@login_required
def edituserinfo():
    """
    Return a page with ability to uprade user information.

    Only administrators can upgrade user information.
    """
    users = User.query.all()
    employees = []
    directors = []
    allusers = []
    divisions = ['A', 'B', 'C']
    for eachuser in User.query.all():
        if eachuser.role.name == 'Employee':
            employees.append(eachuser.username)
        elif eachuser.role.name == 'Director':
            directors.append(eachuser.username)
        allusers.append(eachuser.username)
    # print 'employees: ', employees
    # print 'directors: ', directors
    if request.method == 'POST':
        selectemployee = request.form.getlist('select_employee')[0]
        print 'selectemployee: ', selectemployee
        selectdirector = request.form.getlist('select_director')[0]
        print 'selectdirector: ', selectdirector
        selectaccount = request.form.getlist('select_account')[0]
        print 'selectaccount: ', selectaccount
        selectuser = request.form.getlist('select_user')[0]
        print 'selectuser: ', selectuser
        selectdivision = request.form.getlist('select_division')[0]
        print 'selectdivision: ', selectdivision
        if (len(selectemployee) == 0) and (len(selectdirector) == 0) and (len(selectaccount) == 0) and (len(selectuser) == 0) and (len(selectdivision) == 0):
            return render_template('edituserinfo.html', users=users, employees=employees, directors=directors, allusers=allusers)
        else:
            if len(selectemployee) > 0:
                for user in User.query.all():
                    if selectemployee == user.username:
                        user.role = Role.query.filter_by(permissions=14).first()
                        flash('Employee role has been updated.')
            if len(selectdirector) > 0:
                for user in User.query.all():
                    if selectdirector == user.username:
                        user.role = Role.query.filter_by(permissions=0xff).first()
                        flash('Director role has been updated.')
            if len(selectaccount) > 0:
                for id in request.form.getlist('select_account'):
                    account = User.query.get_or_404(id)
                    db.session.delete(account)
                    db.session.commit()
                    flash('Account has been deleted.')
            if (len(selectuser) > 0) and (len(selectdivision) > 0):
                for user in User.query.all():
                    if selectuser == user.username:
                        user.division = selectdivision
                        flash('User division has been updated.')
            employees = []
            directors = []
            for eachuser in User.query.all():
                if eachuser.role.name == 'Employee':
                    employees.append(eachuser.username)
                elif eachuser.role.name == 'Director':
                    directors.append(eachuser.username)
            return render_template('edituserinfo.html', users=users, employees=employees, directors=directors, divisions=divisions, allusers=allusers)
    return render_template('edituserinfo.html', users=users, employees=employees, directors=directors, divisions=divisions, allusers=allusers)


@main.route('/profile/<string:username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    """
    Return the profile page of a user including the user's avatar, username, role,
    email, number of comments, and number of posts.

    Users can edit their email, and avatar by uploading a image file.
    """
    if User.query.filter_by(username=username).first() is None:
        return render_template('error.html', message='User not found.')
    users = User.query.all()
    user = User.query.filter_by(username=username).first().username
    role = User.query.filter_by(username=username).first().role.name
    email = User.query.filter_by(username=username).first().email
    division = User.query.filter_by(username=username).first().division
    posts = User.query.filter_by(username=username).first().posts.count()
    comments = User.query.filter_by(username=username).first().comments.count()
    avatar = User.query.filter_by(username=username).first().avatar
    if request.method == 'POST':
        file = request.files['profile_picture']
        editusername = request.form.getlist('edit_username')
        if len(editusername) > 0:
            editusername = [r.encode('utf-8') for r in editusername][0]
        if ((len(editusername) == 0) or (editusername == user)) and (bool(file) is False):
            return render_template('profile.html', user=user, users=users, role=role, email=email, division=division,
                                   posts=posts, comments=comments, avatar=avatar, employees=employees, directors=directors)
        else:
            if bool(file) is True:
                avatarfile = "userid" + str(current_user.id) + secure_filename(file.filename)
                saveaddress = os.path.join(os.environ.get('UPLOAD_FOLDER'), avatarfile)
                if allowed_file(file.filename):
                    if current_user.avatar != None and current_user.avatar != "avatars/default.png":
                        oldAvatar = os.path.join(os.environ.get('UPLOAD_FOLDER'), current_user.avatar[8:])
                        if os.path.exists(oldAvatar):
                            os.remove(oldAvatar)
                        else:
                            pass
                    file.save(saveaddress)
                    current_user.avatar = 'avatars/' + "userid" + str(current_user.id) + str(file.filename)
                    flash('Avatar has been updated.')
                else:
                    flash('The uploaded file cannot be used.')
            if editusername != user and (len(editusername) > 1):
                if User.query.filter_by(username=editusername).first() is None:
                    current_user.username = editusername
                    flash('Username has been updated.')
                else:
                    flash('Username is already taken. Please choose another username.')
            return redirect(url_for('.profile', user=user, users=users, role=role, email=email, division=division,
                                    posts=posts, comments=comments, avatar=avatar, username=editusername))
    return render_template('profile.html', user=user, users=users, role=role, email=email, division=division, posts=posts,
                           comments=comments, avatar=avatar, username=username)


@main.route('/edit/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    """
    Return the page for editing a specific comment.

    Keyword arguments:
    id -- the comment id
    """
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
    """
    Return the confirmation page for deleting a comment.

    Keyword arguments:
    id -- the comment id
    """
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


@main.route('/enfg/', methods=['GET', 'POST'])
def enfg():
    """
    Return the Easy Not Found Generator template.
    """
    form = NameForm()
    if form.validate_on_submit():
        session['type'] = form.type.data
        session['name'] = form.name.data
        session['bride_name'] = form.bride_name.data
        session['year'] = form.year.data
        session['borough'] = ', '.join(form.borough.data)
        session['signature'] = form.signature.data
        if not session['signature']:
            return redirect(url_for('.result'))
        else:
            return redirect(url_for('.result_nosig'))
    return render_template('enfg.html', form=form,
                           type=session.get('type'),
                           name=session.get('name'),
                           bride_name=session.get('bride_name'),
                           year=session.get('year'),
                           borough=session.get('borough'),
                           now=datetime.today())


@main.route('/enfg/result', methods=['GET', 'POST'])
def result():
    """
    Return the Easy Not Found Generator result.
    """
    session['date'] = datetime.today().strftime('%m/%d/%y')
    return render_template('result.html',
                           date=session.get('date'),
                           type=session.get('type'),
                           name=session.get('name'),
                           bride_name=session.get('bride_name'),
                           year=session.get('year'),
                           borough=session.get('borough'),
                           now=datetime.today())


@main.route('/enfg/result_nosig', methods=['GET', 'POST'])
def result_nosig():
    """
    Return the Easy Not Found Generator result without a signature.
    """
    session['date'] = datetime.today().strftime('%m/%d/%y')
    return render_template('result_nosig.html',
                           date=session.get('date'),
                           type=session.get('type'),
                           name=session.get('name'),
                           bride_name=session.get('bride_name'),
                           year=session.get('year'),
                           borough=session.get('borough'),
                           now=datetime.today())
