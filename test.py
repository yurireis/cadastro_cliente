import unittest

from app import valida_form
class TesteValidaForm(unittest.TestCase):
	
	def teste_email_sucesso(self):
		data = {'email':'email@certo.com'}
		result = valida_form(data)
		self.assertEqual(result['auth'],1)
	
	def teste_email_fracasso(self):
		data = {'email':'emailerrado.invalido'}
		result = valida_form(data)
		self.assertEqual(result['auth'],0)
		self.assertEqual(result['mensagem'],"Email invalido.")
		
	def teste_cpf_sucesso(self):
		data = {'cpf':'44444444444'}
		result = valida_form(data)
		self.assertEqual(result['auth'],1)
	
	def teste_cpf_fracasso(self):
		data = {'cpf':'44444a44444'}
		result = valida_form(data)
		self.assertEqual(result['auth'],0)
		self.assertEqual(result['mensagem'],"Numero cpf invalido")

if __name__=="__main__":
	unittest.main()
