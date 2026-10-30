import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase

from api.models import Vaga
from api.services.permanencia_service import _calcular_valor


class ApiTestCase(TestCase):
    def enviar(self, metodo, url, dados=None):
        corpo = json.dumps(dados) if dados is not None else ''
        return getattr(self.client, metodo)(url, corpo, content_type='application/json')

    def criar_veiculo(self, cpf='111', placa='ABC-1234'):
        cliente = self.enviar('post', '/api/clientes', {'nome': 'Ana', 'cpf': cpf}).json()
        return self.enviar('post', '/api/veiculos', {
            'placa': placa, 'marca': 'Fiat', 'modelo': 'Uno', 'cor': 'Azul', 'clienteId': cliente['id'],
        }).json()


class CalculoValorTests(TestCase):
    def valor(self, **duracao):
        entrada = datetime(2026, 1, 1, 10, 0)
        return _calcular_valor(entrada, entrada + timedelta(**duracao))

    def test_regras_de_cobranca(self):
        self.assertEqual(self.valor(seconds=0), Decimal('5.00'))
        self.assertEqual(self.valor(minutes=59), Decimal('5.00'))
        self.assertEqual(self.valor(minutes=60), Decimal('5.00'))
        self.assertEqual(self.valor(minutes=60, seconds=59), Decimal('5.00'))
        self.assertEqual(self.valor(minutes=61), Decimal('10.00'))
        self.assertEqual(self.valor(hours=3, minutes=1), Decimal('20.00'))


class ClienteTests(ApiTestCase):
    def test_crud_com_e_sem_barra_final(self):
        criado = self.enviar('post', '/api/clientes/', {'nome': 'Ana', 'cpf': '1', 'telefone': '', 'email': ''})
        self.assertEqual(criado.status_code, 201)
        id = criado.json()['id']
        self.assertEqual(self.client.get(f'/api/clientes/{id}').json()['nome'], 'Ana')
        self.assertEqual(self.enviar('put', f'/api/clientes/{id}', {'nome': 'Bia', 'cpf': '1'}).json()['nome'], 'Bia')
        self.assertEqual(len(self.client.get('/api/clientes').json()), 1)
        self.assertEqual(self.client.delete(f'/api/clientes/{id}/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/clientes/{id}').status_code, 404)

    def test_validacoes(self):
        self.assertEqual(self.enviar('post', '/api/clientes', {'cpf': '1'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/clientes', {'nome': ' ', 'cpf': '1'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/clientes', {'nome': 'A'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/clientes', {'nome': 'A', 'cpf': '1' * 15}).status_code, 400)
        self.assertEqual(self.client.post('/api/clientes', 'x{', content_type='application/json').status_code, 400)
        self.assertEqual(self.enviar('put', '/api/clientes/999', {'nome': 'A', 'cpf': '1'}).status_code, 404)
        self.assertEqual(self.client.patch('/api/clientes').status_code, 405)

    def test_cpf_duplicado(self):
        self.enviar('post', '/api/clientes', {'nome': 'A', 'cpf': '1'})
        outro = self.enviar('post', '/api/clientes', {'nome': 'B', 'cpf': '2'}).json()
        self.assertEqual(self.enviar('post', '/api/clientes', {'nome': 'C', 'cpf': '1'}).status_code, 409)
        self.assertEqual(self.enviar('put', f"/api/clientes/{outro['id']}", {'nome': 'B', 'cpf': '1'}).status_code, 409)


class VeiculoTests(ApiTestCase):
    def test_inclui_nome_do_cliente(self):
        self.criar_veiculo()
        self.assertEqual(self.client.get('/api/veiculos').json()[0]['clienteNome'], 'Ana')

    def test_validacoes(self):
        veiculo = self.criar_veiculo()
        base = {'placa': 'X', 'marca': 'M', 'modelo': 'O', 'cor': 'C', 'clienteId': veiculo['clienteId']}
        for campo in base:
            self.assertEqual(self.enviar('post', '/api/veiculos', {**base, campo: None}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/veiculos', {**base, 'clienteId': 999}).status_code, 404)
        self.assertEqual(self.enviar('post', '/api/veiculos', {**base, 'placa': 'ABC-1234'}).status_code, 409)

    def test_excluir_cliente_remove_veiculos_sem_historico(self):
        veiculo = self.criar_veiculo()
        self.assertEqual(self.client.delete(f"/api/clientes/{veiculo['clienteId']}").status_code, 200)
        self.assertEqual(self.client.get('/api/veiculos').json(), [])


class VagaTests(ApiTestCase):
    def test_vagas_iniciais_e_filtro(self):
        self.assertEqual(len(self.client.get('/api/vagas').json()), 15)
        self.assertEqual(len(self.client.get('/api/vagas?status=OCUPADA').json()), 0)

    def test_validacoes(self):
        self.assertEqual(self.enviar('post', '/api/vagas', {'tipo': 'CARRO'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/vagas', {'numero': 'Z1', 'tipo': 'VAN'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/vagas', {'numero': 'A01', 'tipo': 'CARRO'}).status_code, 409)
        criada = self.enviar('post', '/api/vagas', {'numero': 'Z1', 'tipo': 'MOTO', 'status': 'OCUPADA'})
        self.assertEqual(criada.status_code, 201)
        self.assertEqual(criada.json()['status'], 'LIVRE')


class PermanenciaTests(ApiTestCase):
    def setUp(self):
        self.veiculo = self.criar_veiculo()
        self.vaga = Vaga.objects.get(numero='A01')

    def entrar(self, veiculo_id=None, vaga_id=None):
        return self.enviar('post', '/api/permanencias/entrada', {
            'veiculoId': veiculo_id or self.veiculo['id'],
            'vagaId': vaga_id or self.vaga.id,
        })

    def test_fluxo_completo(self):
        entrada = self.entrar()
        self.assertEqual(entrada.status_code, 201)
        dados = entrada.json()
        self.assertEqual((dados['veiculoPlaca'], dados['veiculoModelo'], dados['vagaNumero'], dados['status']),
                         ('ABC-1234', 'Uno', 'A01', 'ABERTO'))
        self.assertEqual(self.client.get('/api/dashboard').json(), {
            'totalVagas': 15, 'vagasLivres': 14, 'vagasOcupadas': 1, 'veiculosEstacionados': 1,
        })

        saida = self.enviar('put', f"/api/permanencias/{dados['id']}/saida")
        self.assertEqual(saida.status_code, 200)
        self.assertEqual(saida.json()['valorTotal'], 5.0)
        self.assertEqual(saida.json()['status'], 'FINALIZADO')
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, 'LIVRE')
        self.assertEqual(len(self.client.get('/api/permanencias?status=FINALIZADO').json()), 1)
        self.assertEqual(self.client.get('/api/permanencias?status=ABERTO').json(), [])
        self.assertEqual(self.enviar('put', f"/api/permanencias/{dados['id']}/saida").status_code, 409)

    def test_conflitos(self):
        self.entrar()
        outra_vaga = Vaga.objects.get(numero='A02')
        self.assertEqual(self.entrar(vaga_id=outra_vaga.id).status_code, 409)
        outro = self.criar_veiculo(cpf='222', placa='XYZ-9999')
        self.assertEqual(self.entrar(veiculo_id=outro['id']).status_code, 409)

    def test_inexistentes_nao_ocupam_vaga(self):
        self.assertEqual(self.entrar(veiculo_id=999).status_code, 404)
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, 'LIVRE')
        self.assertEqual(self.entrar(vaga_id=999).status_code, 404)
        self.assertEqual(self.enviar('put', '/api/permanencias/999/saida').status_code, 404)

    def test_campos_obrigatorios(self):
        self.assertEqual(self.enviar('post', '/api/permanencias/entrada', {'veiculoId': 1}).status_code, 400)

    def test_exclusao_bloqueada_com_historico(self):
        self.entrar()
        self.assertEqual(self.client.delete(f"/api/veiculos/{self.veiculo['id']}").status_code, 409)
        self.assertEqual(self.client.delete(f'/api/vagas/{self.vaga.id}').status_code, 409)
        self.assertEqual(self.client.delete(f"/api/clientes/{self.veiculo['clienteId']}").status_code, 409)


class InfraTests(ApiTestCase):
    def test_cors(self):
        preflight = self.client.options('/api/clientes')
        self.assertEqual(preflight.status_code, 204)
        self.assertEqual(preflight['Access-Control-Allow-Origin'], '*')
        self.assertIn('PUT', preflight['Access-Control-Allow-Methods'])
        self.assertEqual(self.client.get('/api/vagas')['Access-Control-Allow-Origin'], '*')

    def test_404_em_json(self):
        resposta = self.client.get('/api/nada')
        self.assertEqual(resposta.status_code, 404)
        self.assertIn('error', resposta.json())
