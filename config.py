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
    ADMIN = os.environ.get('ADMIN') or 'tangbrandon1@gmail.com'
    ADMIN2 = os.environ.get('ADMIN2') or 'tangbrandon2@gmail.com'
    DIRECTOR = os.environ.get('DIRECTOR') or 'brandontang1@gmail.com'
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
    DIR1 = 'brandontang1@gmail.com'
    DIR2 = 'brandontang2@gmail.com'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/intranet'
    ADMIN1 = 'tangbrandon1@gmail.com'
    ADMIN2 = 'tangbrandon2@gmail.com'
    DIR1 = 'brandontang1@gmail.com'
    DIR2 = 'brandontang2@gmail.com'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/intranet'
    ADMIN1 = 'tangbrandon1@gmail.com'
    ADMIN2 = 'tangbrandon2@gmail.com'
    DIR1 = 'brandontang1@gmail.com'
    DIR2 = 'brandontang2@gmail.com'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
