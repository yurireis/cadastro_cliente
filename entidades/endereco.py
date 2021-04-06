from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from entidades.base import Base

app = Flask(__name__)
banco = SQLAlchemy(app)


class Endereco(Base):
	__tablename__ = 'endereco'
	id_cliente = banco.Column(banco.Integer, ForeignKey('cliente.id'), primary_key = True)
	pais = banco.Column(banco.String(50))
	estado = banco.Column(banco.String(2))
	municipio = banco.Column(banco.String(150))
	cep = banco.Column(banco.String(8))
	rua = banco.Column(banco.String(250))
	numero = banco.Column(banco.String(10))
	complemento = banco.Column(banco.String(150))
	
	#relacionamento
	cliente_endereco = relationship("Cliente", backref="Cliente.id")
	
	def __init__(self, pais:str, estado:str, municipio:str, cep:str, rua:str, numero:str, complemento:str):
		self.pais = pais
		self.estado = estado
		self.municipio = municipio
		self.cep = cep
		self.rua = rua
		self.numero = numero
		self.complemento = complemento

