from django.db.models import ProtectedError
from django.http import JsonResponse

from api.models import Vaga
from api.views.utils import campo_faltando, erro, erro_de_campos, ler_json, metodo_nao_permitido

TIPOS = ('CARRO', 'MOTO')
STATUS = ('LIVRE', 'OCUPADA')


def vaga_to_dict(vaga):
    return {
        'id':     vaga.id,
        'numero': vaga.numero,
        'tipo':   vaga.tipo,
        'status': vaga.status,
    }


def lista_vagas(request):
    if request.method == 'GET':
        vagas = Vaga.objects.order_by('numero')
        status = request.GET.get('status')
        if status:
            vagas = vagas.filter(status=status)
        return JsonResponse([vaga_to_dict(v) for v in vagas], safe=False)
    if request.method == 'POST':
        return _salvar(request, Vaga(), 201)
    return metodo_nao_permitido()


def detalhe_vaga(request, id):
    try:
        vaga = Vaga.objects.get(id=id)
    except Vaga.DoesNotExist:
        return erro('Vaga não encontrada', 404)

    if request.method == 'GET':
        return JsonResponse(vaga_to_dict(vaga))
    if request.method == 'PUT':
        return _salvar(request, vaga, 200)
    if request.method == 'DELETE':
        try:
            vaga.delete()
        except ProtectedError:
            return erro('Não é possível excluir vaga com permanências registradas', 409)
        return JsonResponse({'message': 'Vaga excluída com sucesso'})
    return metodo_nao_permitido()


def _salvar(request, vaga, status):
    try:
        dados = ler_json(request)
    except ValueError:
        return erro('JSON inválido', 400)

    faltando = campo_faltando(dados, ['numero'])
    if faltando:
        return erro(f"Campo '{faltando}' é obrigatório", 400)
    if dados.get('tipo') not in TIPOS:
        return erro("Campo 'tipo' deve ser CARRO ou MOTO", 400)

    vaga.numero = dados['numero']
    vaga.tipo = dados['tipo']
    # Como no backend Java: toda vaga nasce LIVRE e status inválido no PUT vira LIVRE.
    if status == 201 or dados.get('status') not in STATUS:
        vaga.status = 'LIVRE'
    else:
        vaga.status = dados['status']

    invalido = erro_de_campos(vaga)
    if invalido:
        return erro(invalido, 400)

    if Vaga.objects.filter(numero=vaga.numero).exclude(id=vaga.id).exists():
        return erro('Número de vaga já cadastrado', 409)

    vaga.save()
    return JsonResponse(vaga_to_dict(vaga), status=status)
