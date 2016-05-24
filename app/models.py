import bleach
from datetime import datetime
from markdown import markdown
from flask import current_app
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    """
    Define the permission codes for certain actions.
    """
    WRITE_ARTICLES = 0x04
    ADMINISTER = 0x80
    COMMENT = 0x02
    MODERATE_COMMENTS = 0x08


class Role(db.Model):
    """
    Define the Role class with the following columns and relationships:

    id -- Column: Integer, PrimaryKey
    name -- Column: String(64), Unique
    default -- Column: Boolean, Default = False
    permissions -- Column: Integer
    users -- Relationship: 'User', 'role'
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """Insert permissions for each role: employee, director, and administrator."""
        roles = {
            'Employee': (Permission.COMMENT, True),
            'Director': (Permission.COMMENT |
                         Permission.WRITE_ARTICLES |
                         Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """
    Define the User class with the following columns and relationships:

    id -- Column: Integer, PrimaryKey
    email -- Column: String(64), Unique
    username -- Column: String(64), Unique
    role_id -- Column: Integer, ForeignKey = roles.id
    posts -- Relationship: 'Post', 'author'
    comments -- Relationship: 'Comment', 'author'
    avatar -- Column: String(64), default = 'avatars/default.png'
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    avatar = db.Column(db.String(64), default="avatars/default.png")
    division = db.Column(db.String(64))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        # print "is_administrator:", self.can(Permission.ADMINISTER)
        # print "self.email:", self.email
        return self.can(Permission.ADMINISTER)

    def is_director(self):
        # print "is_director:", self.can(Permission.COMMENT) and self.can(Permission.WRITE_ARTICLES) and self.can(Permission.MODERATE_COMMENTS)
        # print "self.email:", self.email
        return self.can(Permission.COMMENT) and self.can(Permission.WRITE_ARTICLES) and self.can(Permission.MODERATE_COMMENTS)

    def is_employee(self):
        # print "is_employee:", self.can(Permission.COMMENT)
        return self.can(Permission.COMMENT)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN1']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.email == current_app.config['ADMIN2']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.email == current_app.config['ADMIN3']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.email == current_app.config['DIRECTOR1']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR2']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR3']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR4']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR5']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR6']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR7']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR8']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR9']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.email == current_app.config['DIRECTOR10']:
                self.role = Role.query.filter_by(permissions=14).first()
            if self.role == current_app.config['EMPLOYEE']:
                self.role = Role.query.filter_by(permissions=2).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_director(self):
        return False

    def is_employee(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    """
    Define the Post class with the following columns and relationships:

    id -- Column: Integer, PrimaryKey
    title -- Column: String(64), Unique
    text -- Column: UnicodeText
    time -- Column: DateTime
    author_id -- Column: Intger, ForeignKey = 'user.id'
    text_html -- Column: Text
    comments -- Relationship: 'Comment', 'post'
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.UnicodeText)
    time = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text_html = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % (self.title)

    @staticmethod
    def on_changed_text(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.text_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.text, 'set', Post.on_changed_text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Tag(db.Model):
    """
    Define the Tag class with the following columns:

    id -- Column: Integer, PrimaryKey
    name -- Column: String(64)
    """
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<Tag %r>' % (self.name)


class PostTag(db.Model):
    """
    Define the PostTag class with the following columns:

    post_id -- Column: Integer, ForeignKey = 'Post.id'
    tag_id -- Column: Integer, ForeignKey = 'Tag.id'
    """
    __tablename__ = "posttag"
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.id), primary_key=True)

    def __repr__(self):
        return '<Post %r><Tag %r>' % (self.post_id, self.tag_id)


class Comment(db.Model):
    """
    Define the Comment class with the following columns:

    id -- Column: Integer, PrimaryKey
    body -- Column: Text
    body_html -- Column: Text
    timestamp -- Column: DateTime, Default = dateimte.utcnow
    disabled -- Column: Boolean
    author_id -- Column: Integer, ForeignKey = 'users.id'
    post_id -- Column: Integer, ForeignKey = 'posts.id'
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

