from django.db.models import ProtectedError
from django.http import JsonResponse

from api.models import Cliente
from api.views.utils import campo_faltando, erro, erro_de_campos, ler_json, metodo_nao_permitido


def cliente_to_dict(cliente):
    return {
        'id':       cliente.id,
        'nome':     cliente.nome,
        'cpf':      cliente.cpf,
        'telefone': cliente.telefone,
        'email':    cliente.email,
    }


def lista_clientes(request):
    if request.method == 'GET':
        clientes = Cliente.objects.order_by('nome')
        return JsonResponse([cliente_to_dict(c) for c in clientes], safe=False)
    if request.method == 'POST':
        return _salvar(request, Cliente(), 201)
    return metodo_nao_permitido()


def detalhe_cliente(request, id):
    try:
        cliente = Cliente.objects.get(id=id)
    except Cliente.DoesNotExist:
        return erro('Cliente não encontrado', 404)

    if request.method == 'GET':
        return JsonResponse(cliente_to_dict(cliente))
    if request.method == 'PUT':
        return _salvar(request, cliente, 200)
    if request.method == 'DELETE':
        try:
            cliente.delete()
        except ProtectedError:
            return erro('Não é possível excluir cliente com veículos cadastrados', 409)
        return JsonResponse({'message': 'Cliente excluído com sucesso'})
    return metodo_nao_permitido()


def _salvar(request, cliente, status):
    try:
        dados = ler_json(request)
    except ValueError:
        return erro('JSON inválido', 400)

    faltando = campo_faltando(dados, ['nome', 'cpf'])
    if faltando:
        return erro(f"Campo '{faltando}' é obrigatório", 400)

    cliente.nome = dados['nome']
    cliente.cpf = dados['cpf']
    cliente.telefone = dados.get('telefone')
    cliente.email = dados.get('email')

    invalido = erro_de_campos(cliente)
    if invalido:
        return erro(invalido, 400)

    if Cliente.objects.filter(cpf=cliente.cpf).exclude(id=cliente.id).exists():
        return erro('CPF já cadastrado', 409)

    cliente.save()
    return JsonResponse(cliente_to_dict(cliente), status=status)
