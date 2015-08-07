#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Post, Tag, PostTag, Comment
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.sqlalchemy import SQLAlchemy

manager = Manager(app)
migrate = Migrate(app, db)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Tag=Tag, PostTag=PostTag, Comment=Comment)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
