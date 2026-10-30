const Permanencias = (() => {

  async function carregarEstacionados() {
    try {
      const lista = await API.get('/api/permanencias?status=ABERTO');
      renderizarEstacionados(lista);
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  async function carregarHistorico() {
    try {
      const lista = await API.get('/api/permanencias?status=FINALIZADO');
      renderizarHistorico(lista);
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function renderizarEstacionados(lista) {
    const tbody = document.getElementById('tbody-estacionados');
    if (lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:24px">Nenhum veículo estacionado</td></tr>';
      return;
    }
    tbody.innerHTML = lista.map(p => `
      <tr>
        <td>${p.id}</td>
        <td>${esc(p.veiculoModelo || '–')}</td>
        <td><strong>${esc(p.veiculoPlaca || '–')}</strong></td>
        <td>${esc(p.vagaNumero || '–')}</td>
        <td>${formatDateTime(p.dataHoraEntrada)}</td>
        <td>
          <button class="btn btn-success btn-sm" onclick="Permanencias.registrarSaida(${p.id})">
            Registrar Saída
          </button>
        </td>
      </tr>
    `).join('');
  }

  function renderizarHistorico(lista) {
    const tbody = document.getElementById('tbody-historico');
    if (lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#9ca3af;padding:24px">Nenhuma permanência finalizada</td></tr>';
      return;
    }
    tbody.innerHTML = lista.map(p => `
      <tr>
        <td>${p.id}</td>
        <td>${esc(p.veiculoModelo || '–')}</td>
        <td><strong>${esc(p.veiculoPlaca || '–')}</strong></td>
        <td>${esc(p.vagaNumero || '–')}</td>
        <td>${formatDateTime(p.dataHoraEntrada)}</td>
        <td>${formatDateTime(p.dataHoraSaida)}</td>
        <td><strong>${formatCurrency(p.valorTotal)}</strong></td>
      </tr>
    `).join('');
  }

  async function popularSelectsEntrada() {
    try {
      const [veiculos, vagas] = await Promise.all([
        API.get('/api/veiculos'),
        API.get('/api/vagas?status=LIVRE'),
      ]);

      const selVeiculo = document.getElementById('entrada-veiculo');
      const selVaga    = document.getElementById('entrada-vaga');

      selVeiculo.innerHTML = '<option value="">Selecione o veículo</option>' +
        veiculos.map(v => `<option value="${v.id}">${esc(v.placa)} – ${esc(v.modelo)}</option>`).join('');

      selVaga.innerHTML = '<option value="">Selecione a vaga</option>' +
        vagas.map(v => `<option value="${v.id}">${esc(v.numero)} (${v.tipo})</option>`).join('');

    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  async function registrarEntrada(event) {
    event.preventDefault();
    const veiculoId = parseInt(document.getElementById('entrada-veiculo').value, 10);
    const vagaId    = parseInt(document.getElementById('entrada-vaga').value, 10);

    if (!veiculoId || !vagaId) {
      showToast('Selecione o veículo e a vaga', 'error');
      return;
    }

    try {
      await API.post('/api/permanencias/entrada', { veiculoId, vagaId });
      showToast('Entrada registrada com sucesso', 'success');
      document.getElementById('form-entrada').reset();
      await popularSelectsEntrada();
      await carregarEstacionados();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  async function registrarSaida(id) {
    if (!confirm('Confirmar saída do veículo?')) return;
    try {
      const p = await API.put(`/api/permanencias/${id}/saida`);
      showToast(`Saída registrada. Valor: ${formatCurrency(p.valorTotal)}`, 'success');
      await popularSelectsEntrada();
      await carregarEstacionados();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  // ─── helpers ────────────────────────────────────────────────────────────────

  function formatDateTime(isoStr) {
    if (!isoStr) return '–';
    const d = new Date(isoStr);
    return d.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  }

  function formatCurrency(value) {
    if (value == null) return '–';
    return 'R$ ' + parseFloat(value).toFixed(2).replace('.', ',');
  }

  return {
    carregarEstacionados,
    carregarHistorico,
    popularSelectsEntrada,
    registrarEntrada,
    registrarSaida,
  };
})();
