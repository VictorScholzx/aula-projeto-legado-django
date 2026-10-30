from django.http import JsonResponse

from api.models import Permanencia, Vaga
from api.views.utils import metodo_nao_permitido


def dashboard(request):
    if request.method != 'GET':
        return metodo_nao_permitido()

    return JsonResponse({
        'totalVagas':           Vaga.objects.count(),
        'vagasLivres':          Vaga.objects.filter(status='LIVRE').count(),
        'vagasOcupadas':        Vaga.objects.filter(status='OCUPADA').count(),
        'veiculosEstacionados': Permanencia.objects.filter(status='ABERTO').count(),
    })
