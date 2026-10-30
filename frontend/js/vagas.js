const Vagas = (() => {
  let _lista = [];

  async function carregar() {
    try {
      _lista = await API.get('/api/vagas');
      renderizar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function renderizar() {
    const tbody = document.getElementById('tbody-vagas');
    if (_lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#9ca3af;padding:24px">Nenhuma vaga cadastrada</td></tr>';
      return;
    }
    tbody.innerHTML = _lista.map(v => `
      <tr>
        <td>${v.id}</td>
        <td><strong>${esc(v.numero)}</strong></td>
        <td>${tipoBadge(v.tipo)}</td>
        <td>${statusBadge(v.status)}</td>
        <td>
          <div class="btn-group">
            <button class="btn btn-outline btn-sm" onclick="Vagas.abrirFormEditar(${v.id})">Editar</button>
            <button class="btn btn-danger  btn-sm" onclick="Vagas.excluir(${v.id})">Excluir</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  function tipoBadge(tipo) {
    return tipo === 'MOTO'
      ? '<span class="badge badge-blue">Moto</span>'
      : '<span class="badge badge-gray">Carro</span>';
  }

  function statusBadge(status) {
    return status === 'LIVRE'
      ? '<span class="badge badge-green">Livre</span>'
      : '<span class="badge badge-red">Ocupada</span>';
  }

  function abrirFormNovo() {
    openModal('Nova Vaga', formHtml());
  }

  function abrirFormEditar(id) {
    const v = _lista.find(x => x.id === id);
    if (!v) return;
    openModal('Editar Vaga', formHtml(v));
  }

  function formHtml(v = {}) {
    return `
      <form class="modal-form" onsubmit="Vagas.salvar(event, ${v.id || 'null'})">
        <div class="form-group">
          <label>Número *</label>
          <input name="numero" value="${esc(v.numero || '')}" required placeholder="Ex: A01" />
        </div>
        <div class="form-group">
          <label>Tipo *</label>
          <select name="tipo" required>
            <option value="">Selecione</option>
            <option value="CARRO" ${v.tipo === 'CARRO' ? 'selected' : ''}>Carro</option>
            <option value="MOTO"  ${v.tipo === 'MOTO'  ? 'selected' : ''}>Moto</option>
          </select>
        </div>
        ${v.id ? `
        <div class="form-group">
          <label>Status</label>
          <select name="status">
            <option value="LIVRE"   ${v.status === 'LIVRE'   ? 'selected' : ''}>Livre</option>
            <option value="OCUPADA" ${v.status === 'OCUPADA' ? 'selected' : ''}>Ocupada</option>
          </select>
        </div>` : ''}
        <div class="modal-actions">
          <button type="button" class="btn btn-outline" onclick="closeModal()">Cancelar</button>
          <button type="submit" class="btn btn-primary">Salvar</button>
        </div>
      </form>`;
  }

  async function salvar(event, id) {
    event.preventDefault();
    const form = event.target;
    const dados = {
      numero: form.numero.value.trim().toUpperCase(),
      tipo:   form.tipo.value,
      status: form.status ? form.status.value : 'LIVRE',
    };
    try {
      if (id) {
        await API.put(`/api/vagas/${id}`, dados);
        showToast('Vaga atualizada com sucesso', 'success');
      } else {
        await API.post('/api/vagas', dados);
        showToast('Vaga cadastrada com sucesso', 'success');
      }
      closeModal();
      await carregar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  async function excluir(id) {
    if (!confirm('Deseja excluir esta vaga?')) return;
    try {
      await API.delete(`/api/vagas/${id}`);
      showToast('Vaga excluída', 'success');
      await carregar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function getLista() { return _lista; }

  return { carregar, abrirFormNovo, abrirFormEditar, salvar, excluir, getLista };
})();
