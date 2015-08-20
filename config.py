import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Intranet]'
    FLASKY_MAIL_SENDER = 'Admin <tangbrandon1@gmail.com>'

    ADMIN1 = os.environ.get('ADMIN1') or 'tangbrandon1@gmail.com'
    ADMIN2 = os.environ.get('ADMIN2') or 'tangbrandon2@gmail.com'
    ADMIN3 = os.environ.get('ADMIN3') or 'tangbrandon3@gmail.com'
    ADMIN4 = 'tangbrandon4@gmail.com'
    ADMIN5 = os.environ.get('ADMIN5')
    ADMIN6 = os.environ.get('ADMIN6') or 'tangbrandon6@gmail.com'
    ADMINLIST = 'tangbrandon7@gmail.com' or 'tangbrandon8@gmail.com'
    DIRECTOR1 = os.environ.get('DIRECTOR1') or 'brandontang1@gmail.com' or 'brandontang3@gmail.com'
    DIRECTOR2 = os.environ.get('DIRECTOR2') or 'brandontang2@gmail.com'
    EMPLOYEE = os.environ.get('EMPLOYEE')
    POSTS_PER_PAGE = 5
    COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://root:@localhost/intranet'
    ADMIN1 = 'tangbrandon1@gmail.com'
    ADMIN2 = 'tangbrandon2@gmail.com'
    DIRECTOR1 = 'brandontang1@gmail.com'
    DIRECTOR2 = 'brandontang2@gmail.com'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/intranet'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/intranet'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
