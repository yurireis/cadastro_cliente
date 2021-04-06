from flask import Flask,session,redirect,request,url_for,jsonify,make_response,render_template,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, update
from sqlalchemy.orm import relationship
from flask_marshmallow import Marshmallow
from authlib.integrations.flask_client import OAuth
import json
import jwt
import datetime
import re
from sqlalchemy import create_engine
from entidades.cliente import Cliente
from entidades.endereco import Endereco
from entidades.EnderecoSchema import EnderecoSchema
from entidades.ClienteSchema import ClienteSchema
from config import Development, BaseConfig
import entidades.base
from decouple import config

API_TEMPO_SESSAO = config('TEMPO_SESSAO')

app = Flask(__name__)
app.config.from_object(Development)
banco = SQLAlchemy(app)
marsh = Marshmallow(app)
oauth = OAuth(app)
engine = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
entidades.base.Base.metadata.create_all(engine, checkfirst=True)


google = oauth.register(
	name = 'google',
	client_id = app.config["GOOGLE_CLIENT_ID"],
	client_secret = app.config["GOOGLE_CLIENT_SECRET"],
	access_token_url = 'https://accounts.google.com/o/oauth2/token',
	access_token_params = None,
	authorize_url = 'https://accounts.google.com/o/oauth2/auth',
	authorize_params = None,
	api_base_url = 'https://www.googleapis.com/oauth2/vi/',
	userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',
	client_kwargs = {'scope':'openid email profile'}
)


	
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


	
	
	
	
	

####################################################

def carrega_cliente(id):
	cliente_query = banco.session.query(Cliente).get(id)
	cliente_schema = ClienteSchema()
	cliente_json = cliente_schema.dump(cliente_query)
	endereco_query = banco.session.query(Endereco).get(id)
	endereco_schema = EnderecoSchema()
	cliente_json['endereco'] = endereco_schema.dump(endereco_query)
	cliente_json['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(API_TEMPO_SESSAO))
	return cliente_json
	


def valida_sessao(token):
	if not session.get('logged_in'):
		resposta = {'auth': 0,'mensagem':''}
	else:
		try: 
			cliente_json = jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256']) 
			resposta = {'auth': 1,'token':cliente_json}
			## no caso de haver jwt implementado em fe, acima nao seria passado o cliente_json, e sim seria criado um novo jwt para setar o cookie
		except jwt.ExpiredSignatureError:
			resposta = {'auth': 0,'mensagem':'Token expirado, favor realizar novamente o login.'}
		except jwt.DecodeError:
			resposta = {'auth': 0,'mensagem':'Token invalido, favor realizar o login.'}
		except Exception as e:
			print(e)
			resposta = {'auth': 0,'mensagem':'Erro desconhecido :('}
	return resposta

def redireciona(token,pagina):
	validacao = valida_sessao(token)
	if validacao['auth'] == 0:
		resposta = render_template('index.html',mensagem=validacao['mensagem'])
	else:
		resposta = render_template(pagina, token=validacao['token']) 	
	return resposta

def valida_form(json):
##valida se as entradas estao de acordo com as restricoes de banco
##bem como se estao de acordo com as restricoes dos dados em si
	for i in json:
		if json[i]=='' and i!='complemento':
			##considera-se que 'complemento' e o unico campo que pode ser vazio
			return {'auth':0, 'mensagem':"O campo "+i+" nao foi preenchido"}
		if i in('nome','complemento','municipio') and len(json[i]) > 150: 
			return {'auth':0, 'mensagem':"O campo "+i+" possui mais de 150 caracteres"}
		elif i=='email' and not(re.search('^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$',json[i])):
			return {'auth':0, 'mensagem':"Email invalido."}
		elif i in ('cpf','pis') and (len(json[i]) != 11 or not(json[i].isnumeric())):
			return {'auth':0, 'mensagem':"Numero "+i+" invalido"}
		elif i =='cep' and (len(json[i]) != 8 or not(json[i].isnumeric())):
			return {'auth':0, 'mensagem':"Numero "+i+" invalido"}
		elif i == 'estado' and json[i] not in("AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"):
			return {'auth':0, 'mensagem':"Estado invalido."}
		elif i == 'rua' and len(json[i]) > 250:
			return {'auth':0, 'mensagem':"Campo Rua com limite excedido"}
		elif i == 'numero' and len(json[i]) > 10:
			return {'auth':0, 'mensagem':"Campo Numero com limite excedido"}
	return {'auth':1, 'mensagem':''}

			

####################################################




@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/cadastrar', methods=['POST','GET'])
def cadastrar():
	if request.method == 'POST':
		form_json = json.loads(json.dumps(request.form))
		validacao_form = valida_form(form_json)
		if validacao_form['auth']==0:
			resposta = render_template('cadastrar.html',mensagem=validacao_form['mensagem'])
		else:
			cliente_query = banco.session.query(Cliente).filter(banco.or_(form_json['email'] == Cliente.email, form_json['cpf'] == Cliente.cpf, form_json['pis'] == Cliente.pis))
			## confirmando se existe outra entidade que ja possui o mesmo valor para as colunas 'unique'
			if cliente_query.count() == 0:
				cliente = Cliente(nome = form_json['nome'],
									email = form_json['email'],
									cpf = form_json['cpf'],
									pis = form_json['pis'],
									senha = form_json['senha'])
				endereco = Endereco(pais = form_json['pais'],
									estado = form_json['estado'],
									rua = form_json['rua'],
									cep = form_json['cep'],
									numero = form_json['numero'],
									complemento = form_json['complemento'],
									municipio = form_json['municipio'])
				cliente.endereco_cliente.append(endereco)
				banco.session.add(cliente)
				banco.session.flush()
				banco.session.commit()
				resposta = render_template('index.html', mensagem='Cliente cadastrado com sucesso! Faça login para acessar')
			else:
				resposta = render_template('cadastrar.html', mensagem='Ja existe usuario cadastrado com uma das chaves de email, CPF ou PIS informadas')
	else: resposta = render_template('cadastrar.html')
	return resposta
	
		
@app.route('/login',methods=['POST'])
def submit():
		
		login = request.form['login']
		senha = request.form['senha']
		
		##informacao acima a vir encoded de FE
		
		if login != '' and senha != '':
			cliente_query = banco.session.query(Cliente).filter(banco.and_(banco.or_(login == Cliente.email, login == Cliente.cpf, login == Cliente.pis), senha == Cliente.senha))
			if cliente_query.count() == 0:
				return render_template('index.html',mensagem='Usuario e/ou senha invalido(s)')
			else:
				session['logged_in']=True
				cliente_json = carrega_cliente(cliente_query.first().id)
				token = jwt.encode(cliente_json,app.config['SECRET_KEY'])
				resposta = redirect(url_for('userPage'))
				resposta.set_cookie('token',token)
				return resposta
		else:
			return render_template('index.html',mensagem='Favor preencher todos os campos :)')


@app.route('/googleLogin', methods=['POST'])
def googleLogin():
	google = oauth.create_client('google')
	resposta = url_for('authGoogle',_external=True)
	return google.authorize_redirect(resposta)
	

@app.route('/authGoogle')
def authGoogle():
	google = oauth.create_client('google')
	token = google.authorize_access_token()
	resp = google.get('userinfo')
	user = oauth.google.userinfo()
	cliente_query = banco.session.query(Cliente).filter(user['email'] == Cliente.email)
	if cliente_query.count() == 0:
		resposta = render_template('index.html',mensagem='Nao encontrado usuario cadastrado com o gmail informado')
	else:
		session['logged_in']=True
		cliente_json = carrega_cliente(cliente_query.first().id)
		token = jwt.encode(cliente_json,app.config['SECRET_KEY'])
		resposta = redirect(url_for('userPage'))
		resposta.set_cookie('token',token)
	return resposta

@app.route('/userPage')
def userPage():
	token = request.cookies.get('token')
	return redireciona(token,'pag2.html')
	

@app.route('/editar',methods=['POST'])
def editar():
	token = request.cookies.get('token')
	return redireciona(token, 'editUser.html')


@app.route('/salvar',methods=['POST'])
def salvar():
	token = request.cookies.get('token')
	validacao = valida_sessao(token)
	##aqui, no caso de jwt estar implementado em fe, seria feito um decode do novo token gerado em 'valida_sessao'. Porem, atualmente a funcao ja retorna o json
	if validacao['auth'] == 0:
		resposta= render_template('index.html',mensagem=validacao['mensagem'])
	else:
		form_json = json.loads(json.dumps(request.form))
		validacao_form = valida_form(form_json)
		if validacao_form['auth']==0:
			resposta = render_template('editUser.html',token=validacao['token'],mensagem=validacao_form['mensagem'])
		else:
			#informacao acima a vir encoded de fe
			cliente_query = banco.session.query(Cliente).filter( validacao['token']['id'] == Cliente.id).first()
			cliente_schema = ClienteSchema()
			endereco_query = banco.session.query(Endereco).filter( validacao['token']['id'] == Endereco.id_cliente).first()
			endereco_schema = EnderecoSchema()
			cliente_json = cliente_schema.dump(cliente_query)
			endereco_json = endereco_schema.dump(endereco_query)
			for i in cliente_json:
				if i not in ('id','id_cliente'):
					if cliente_json[i]!=form_json[i]:
						setattr(cliente_query,i,form_json[i])
			for i in endereco_json: 
				if i not in ('id','id_cliente'):
					if endereco_json[i]!=form_json[i]:
						setattr(endereco_query,i,form_json[i])
			banco.session.commit()
			cliente_json = carrega_cliente(cliente_query.id)
			token = jwt.encode(cliente_json,app.config['SECRET_KEY'])
			resposta = redirect(url_for('userPage'))
			resposta.set_cookie('token',token)
	return resposta



@app.route('/excluir',methods=['POST'])
def excluir():
	token = request.cookies.get('token')
	validacao = valida_sessao(token)
	if validacao['auth'] == 1:
		banco.session.query(Endereco).filter(Endereco.id_cliente == validacao['token']['id']).delete()
		banco.session.query(Cliente).filter(Cliente.id == validacao['token']['id']).delete()
		banco.session.commit()
		session['logged_in']=False
		resposta = make_response(render_template('index.html', mensagem='Cliente excluido.'))
		resposta.set_cookie('token','')
	else: resposta = render_template('index.html', mensagem=validacao['mensagem'])
	return resposta


@app.route('/logout',methods=['POST'])
def logout():
	session['logged_in']=False
	resposta =  make_response(render_template('index.html', mensagem='Log out com sucesso.'))
	resposta.set_cookie('token','')
	return resposta


if __name__=="__main__":
	
	app.run()
