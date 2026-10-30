from django.db.models import ProtectedError
from django.http import JsonResponse

from api.models import Cliente, Veiculo
from api.views.utils import (
    campo_faltando,
    erro,
    erro_de_campos,
    ler_json,
    metodo_nao_permitido,
    para_id,
)


def veiculo_to_dict(veiculo):
    return {
        'id':          veiculo.id,
        'placa':       veiculo.placa,
        'marca':       veiculo.marca,
        'modelo':      veiculo.modelo,
        'cor':         veiculo.cor,
        'clienteId':   veiculo.cliente_id,
        'clienteNome': veiculo.cliente.nome,
    }


def lista_veiculos(request):
    if request.method == 'GET':
        veiculos = Veiculo.objects.select_related('cliente').order_by('placa')
        return JsonResponse([veiculo_to_dict(v) for v in veiculos], safe=False)
    if request.method == 'POST':
        return _salvar(request, Veiculo(), 201)
    return metodo_nao_permitido()


def detalhe_veiculo(request, id):
    try:
        veiculo = Veiculo.objects.select_related('cliente').get(id=id)
    except Veiculo.DoesNotExist:
        return erro('Veículo não encontrado', 404)

    if request.method == 'GET':
        return JsonResponse(veiculo_to_dict(veiculo))
    if request.method == 'PUT':
        return _salvar(request, veiculo, 200)
    if request.method == 'DELETE':
        try:
            veiculo.delete()
        except ProtectedError:
            return erro('Não é possível excluir veículo com permanências registradas', 409)
        return JsonResponse({'message': 'Veículo excluído com sucesso'})
    return metodo_nao_permitido()


def _salvar(request, veiculo, status):
    try:
        dados = ler_json(request)
    except ValueError:
        return erro('JSON inválido', 400)

    faltando = campo_faltando(dados, ['placa', 'marca', 'modelo', 'cor', 'clienteId'])
    if faltando:
        return erro(f"Campo '{faltando}' é obrigatório", 400)

    cliente_id = para_id(dados['clienteId'])
    if cliente_id is None:
        return erro("Campo 'clienteId' inválido", 400)
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return erro('Cliente não encontrado', 404)

    veiculo.placa = dados['placa']
    veiculo.marca = dados['marca']
    veiculo.modelo = dados['modelo']
    veiculo.cor = dados['cor']
    veiculo.cliente = cliente

    invalido = erro_de_campos(veiculo)
    if invalido:
        return erro(invalido, 400)

    if Veiculo.objects.filter(placa=veiculo.placa).exclude(id=veiculo.id).exists():
        return erro('Placa já cadastrada', 409)

    veiculo.save()
    return JsonResponse(veiculo_to_dict(veiculo), status=status)
