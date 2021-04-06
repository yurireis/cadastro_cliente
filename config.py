class BaseConfig(object):
    SECRET_KEY = 'ExemploDemonstracao'
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:booser101@localhost/cadastro_cliente"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = "55921898334-l8f03698heh66thlp4ovag58jcvrgshv.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "VfWYLMdOiZ9giIReJp0plmJK"
    
    
class Development(BaseConfig):
    PORT = 5000
    DEBUG = True
    TESTING = True
    ENV = 'dev'
    APP_NAME = "CadastraCliente"
    
'''class Production(BaseConfig):
    PORT = 8080
    DEBUG = False
    TESTING = False
    ENV = 'production'
    APP_NAME = "CadastraCliente"'''
