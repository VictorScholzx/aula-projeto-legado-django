from django.http import JsonResponse

from api.models import Permanencia
from api.services import permanencia_service
from api.services.permanencia_service import RecursoNaoEncontrado
from api.views.utils import erro, ler_json, metodo_nao_permitido, para_id


def permanencia_to_dict(permanencia):
    valor = permanencia.valor_total
    saida = permanencia.data_hora_saida
    return {
        'id':              permanencia.id,
        'veiculoId':       permanencia.veiculo_id,
        'veiculoPlaca':    permanencia.veiculo.placa,
        'veiculoModelo':   permanencia.veiculo.modelo,
        'vagaId':          permanencia.vaga_id,
        'vagaNumero':      permanencia.vaga.numero,
        'dataHoraEntrada': permanencia.data_hora_entrada.isoformat(),
        'dataHoraSaida':   saida.isoformat() if saida else None,
        # float só na saída JSON, para manter o número do backend Java; o cálculo usa Decimal.
        'valorTotal':      float(valor) if valor is not None else None,
        'status':          permanencia.status,
    }


def lista_permanencias(request):
    if request.method != 'GET':
        return metodo_nao_permitido()

    permanencias = Permanencia.objects.select_related('veiculo', 'vaga').order_by('-data_hora_entrada')
    status = request.GET.get('status')
    if status:
        permanencias = permanencias.filter(status=status)
    return JsonResponse([permanencia_to_dict(p) for p in permanencias], safe=False)


def entrada(request):
    if request.method != 'POST':
        return metodo_nao_permitido()

    try:
        dados = ler_json(request)
    except ValueError:
        return erro('JSON inválido', 400)

    veiculo_id = para_id(dados.get('veiculoId'))
    vaga_id = para_id(dados.get('vagaId'))
    if veiculo_id is None or vaga_id is None:
        return erro("Campos 'veiculoId' e 'vagaId' são obrigatórios", 400)

    try:
        permanencia = permanencia_service.registrar_entrada(veiculo_id, vaga_id)
    except RecursoNaoEncontrado as e:
        return erro(str(e), 404)
    except ValueError as e:
        return erro(str(e), 409)
    return JsonResponse(permanencia_to_dict(permanencia), status=201)


def saida(request, id):
    if request.method != 'PUT':
        return metodo_nao_permitido()

    try:
        permanencia = permanencia_service.registrar_saida(id)
    except RecursoNaoEncontrado as e:
        return erro(str(e), 404)
    except ValueError as e:
        return erro(str(e), 409)
    return JsonResponse(permanencia_to_dict(permanencia))
