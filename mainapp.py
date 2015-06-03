import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, HiddenField, DateTimeField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Shell
from flask.ext.migrate import Migrate, MigrateCommand
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'secretkey'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

class PostForm(Form):
    title = StringField('Title', validators=[Required()])
    text = StringField('Text', validators=[Required()])
    submit = SubmitField('Submit')

class Post(db.Model):
    __tablename__ = 'posts'
    title = db.Column(db.String(64), primary_key=True, unique=True)
    text = db.Column(db.String(64), unique=True)
    time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Post %r><Post %r><Post %r>' % (self.title, self.text, self.time)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    print "1"
    print Post.query.all()
    if form.validate_on_submit():
        print "2"
        post = Post.query.filter_by(text=form.text.data).first()
        print post
        print "3"
        if post is None:
            print form.title.data
            print "A"
            post = Post(title = form.title.data, text = form.text.data, time = datetime.now())
            print "B"
            db.session.add(post)
            print "C"
            db.session.commit()
            print "D"
        print "E"
        session['title'] = form.title.data
        print "F"
        session['text'] = form.text.data
        print "G"
        return redirect(url_for('index'))
    print "H"
    posts = Post.query.order_by(Post.time.desc())
    return render_template('index.html', form = form, title = session.get('title'), text = session.get('text'), posts = posts)

@app.route('/newpost', methods=['GET', 'POST'])
def employeeselfservice():
    form = PostForm()
    print Post.query.all()
    if form.validate_on_submit():
        post = Post.query.filter_by(text=form.text.data).first()
        print Post.query.all()
        if post is None:
            print form.title.data
            print "A"
            post = Post(title = form.title.data, text = form.text.data, time = datetime.now())
            print "B"
            db.session.add(post)
            print "C"
            db.session.commit()
            print "D"
        print "E"
        session['title'] = form.title.data
        print "F"
        session['text'] = form.text.data
        print "G"
        return redirect(url_for('index'))
    print "H"
    return render_template('newpost.html', form = form, title = session.get('title'), text = session.get('text'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def make_shell_context():
    return dict(app=app, db=db, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
