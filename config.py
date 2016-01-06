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
    ADMIN1 = 'btang@records.nyc.gov'
    ADMIN2 = 'jocastillo@records.nyc.gov'
    DIRECTOR1 = 'ptoole@records.nyc.gov'
    DIRECTOR2 = 'kcobb@records.nyc.gov'
    DIRECTOR3 = 'napacheco@records.nyc.gov'
    DIRECTOR4 = 'skollar@records.nyc.gov'
    DIRECTOR5 = 'mlorenzini@records.nyc.gov'
    DIRECTOR6 = 'pboatswain@records.nyc.gov'
    DIRECTOR7 = 'tmccormick@records.nyc.gov'
    DIRECTOR8 = 'aakuesson@records.nyc.gov'
    DIRECTOR9 = 'lcjones@records.nyc.gov'
    DIRECTOR10 = 'temccormick@records.nyc.gov'
    DIRECTOR11 = 'jewilson@records.nyc.gov'
    EMPLOYEE = os.environ.get('EMPLOYEE')
    POSTS_PER_PAGE = 5
    COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://root:@localhost/intranet'


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
