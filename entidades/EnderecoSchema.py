from flask import Flask
from flask_marshmallow import Marshmallow
from entidades.endereco import Endereco

app = Flask(__name__)
marsh = Marshmallow(app)

class EnderecoSchema(marsh.SQLAlchemyAutoSchema):
	class Meta:
		model = Endereco
		load_instance = True
		fields = ('id_cliente','pais','estado','municipio','cep','rua','numero','complemento')
