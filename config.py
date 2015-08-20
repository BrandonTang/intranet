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
    ADMIN1 = os.environ.get('ADMIN1') or 'btang@records.nyc.gov'
    ADMIN2 = os.environ.get('ADMIN2') or 'jocastillo@records.nyc.gov'
    DIRECTOR1 = os.environ.get('DIRECTOR1') or 'ptoole@records.nyc.gov'
    DIRECTOR2 = os.environ.get('DIRECTOR2') or 'kcobb@records.nyc.gov'
    DIRECTOR3 = os.environ.get('DIRECTOR3') or 'napacheco@records.nyc.gov'
    DIRECTOR4 = os.environ.get('DIRECTOR4') or 'skollar@records.nyc.gov'
    DIRECTOR5 = os.environ.get('DIRECTOR5') or 'mlorenzini@records.nyc.gov'
    DIRECTOR6 = os.environ.get('DIRECTOR6') or 'pboatswain@records.nyc.gov'
    DIRECTOR7 = os.environ.get('DIRECTOR7') or 'tmccormick@records.nyc.gov'
    DIRECTOR8 = os.environ.get('DIRECTOR8') or 'aakuesson@records.nyc.gov'
    DIRECTOR9 = os.environ.get('DIRECTOR9')
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
