from django.urls import re_path

from api.views import (
    cliente_views,
    dashboard_views,
    permanencia_views,
    vaga_views,
    veiculo_views,
)

# A barra final é opcional porque o frontend chama /api/clientes (sem barra),
# e o redirecionamento do APPEND_SLASH não funciona para POST e PUT.
urlpatterns = [
    re_path(r'^clientes/?$', cliente_views.lista_clientes),
    re_path(r'^clientes/(?P<id>\d+)/?$', cliente_views.detalhe_cliente),
    re_path(r'^veiculos/?$', veiculo_views.lista_veiculos),
    re_path(r'^veiculos/(?P<id>\d+)/?$', veiculo_views.detalhe_veiculo),
    re_path(r'^vagas/?$', vaga_views.lista_vagas),
    re_path(r'^vagas/(?P<id>\d+)/?$', vaga_views.detalhe_vaga),
    re_path(r'^permanencias/entrada/?$', permanencia_views.entrada),
    re_path(r'^permanencias/(?P<id>\d+)/saida/?$', permanencia_views.saida),
    re_path(r'^permanencias/?$', permanencia_views.lista_permanencias),
    re_path(r'^dashboard/?$', dashboard_views.dashboard),
]
