from flask import Flask
from flask_marshmallow import Marshmallow
from entidades.cliente import Cliente

app = Flask(__name__)
marsh = Marshmallow(app)

class ClienteSchema(marsh.SQLAlchemyAutoSchema):
	class Meta:
		model = Cliente
		load_instance = True
		fields = ('id','nome','email','cpf','pis','senha')
		
