from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from entidades.base import Base

app = Flask(__name__)
banco = SQLAlchemy(app)


class Cliente(Base):
	__tablename__ = 'cliente'
	id = banco.Column(banco.Integer, primary_key=True)
	nome = banco.Column(banco.String(150))
	email = banco.Column(banco.String(50), unique=True)
	cpf = banco.Column(banco.String(11), unique=True)
	pis = banco.Column(banco.String(11), unique=True)
	senha = banco.Column(banco.String(15))
	
	##relacionamento
	endereco_cliente = banco.relationship("Endereco",uselist = True, foreign_keys="Endereco.id_cliente")
	

	def __init__(self, nome:str, email:str, cpf:str, pis:str, senha:str):
		self.nome = nome
		self.email = email
		self.cpf = cpf
		self.pis = pis
		self.senha = senha
