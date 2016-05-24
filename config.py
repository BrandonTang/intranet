import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = os.environ.get('SQLALCHEMY_COMMIT_ON_TEARDOWN')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    FLASKY_MAIL_SUBJECT_PREFIX = os.environ.get('FLASKY_MAIL_SUBJECT_PREFIX')
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    ADMIN1 = os.environ.get('ADMIN1')
    ADMIN2 = os.environ.get('ADMIN2')
    ADMIN3 = os.environ.get('ADMIN3')
    DIRECTOR1 = os.environ.get('DIRECTOR1')
    DIRECTOR2 = os.environ.get('DIRECTOR2')
    DIRECTOR3 = os.environ.get('DIRECTOR3')
    DIRECTOR4 = os.environ.get('DIRECTOR4')
    DIRECTOR5 = os.environ.get('DIRECTOR5')
    DIRECTOR6 = os.environ.get('DIRECTOR6')
    DIRECTOR7 = os.environ.get('DIRECTOR7')
    DIRECTOR8 = os.environ.get('DIRECTOR8')
    DIRECTOR9 = os.environ.get('DIRECTOR9')
    DIRECTOR10 = os.environ.get('DIRECTOR10')
    DIRECTOR11 = os.environ.get('DIRECTOR11')
    EMPLOYEE = os.environ.get('EMPLOYEE')
    USE_LDAP = os.environ.get('USE_LDAP')
    LDAP_SERVER = os.environ.get('LDAP_SERVER')
    LDAP_PORT = os.environ.get('LDAP_PORT')
    LDAP_USE_TLS = os.environ.get('LDAP_USE_TLS')
    LDAP_CERT_PATH = os.environ.get('LDAP_CERT_PATH')
    LDAP_SA_BIND_DN = os.environ.get('LDAP_SA_BIND_DN')
    LDAP_SA_PASSWORD = os.environ.get('LDAP_SA_PASSWORD')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN')

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
