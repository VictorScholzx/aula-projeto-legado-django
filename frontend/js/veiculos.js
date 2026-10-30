const Veiculos = (() => {
  let _lista = [];

  async function carregar() {
    try {
      _lista = await API.get('/api/veiculos');
      renderizar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function renderizar() {
    const tbody = document.getElementById('tbody-veiculos');
    if (_lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#9ca3af;padding:24px">Nenhum veículo cadastrado</td></tr>';
      return;
    }
    tbody.innerHTML = _lista.map(v => `
      <tr>
        <td>${v.id}</td>
        <td><strong>${esc(v.placa)}</strong></td>
        <td>${esc(v.marca)}</td>
        <td>${esc(v.modelo)}</td>
        <td>${esc(v.cor)}</td>
        <td>${esc(v.clienteNome || '–')}</td>
        <td>
          <div class="btn-group">
            <button class="btn btn-outline btn-sm" onclick="Veiculos.abrirFormEditar(${v.id})">Editar</button>
            <button class="btn btn-danger  btn-sm" onclick="Veiculos.excluir(${v.id})">Excluir</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  function abrirFormNovo() {
    openModal('Novo Veículo', formHtml());
  }

  function abrirFormEditar(id) {
    const v = _lista.find(x => x.id === id);
    if (!v) return;
    openModal('Editar Veículo', formHtml(v));
  }

  function formHtml(v = {}) {
    const clientes = Clientes.getLista();
    const optsClientes = clientes.map(c =>
      `<option value="${c.id}" ${v.clienteId === c.id ? 'selected' : ''}>${esc(c.nome)}</option>`
    ).join('');

    return `
      <form class="modal-form" onsubmit="Veiculos.salvar(event, ${v.id || 'null'})">
        <div class="form-group">
          <label>Placa *</label>
          <input name="placa" value="${esc(v.placa || '')}" required placeholder="ABC-1234"
                 style="text-transform:uppercase" />
        </div>
        <div class="form-group">
          <label>Marca *</label>
          <input name="marca" value="${esc(v.marca || '')}" required placeholder="Ex: Toyota" />
        </div>
        <div class="form-group">
          <label>Modelo *</label>
          <input name="modelo" value="${esc(v.modelo || '')}" required placeholder="Ex: Corolla" />
        </div>
        <div class="form-group">
          <label>Cor *</label>
          <input name="cor" value="${esc(v.cor || '')}" required placeholder="Ex: Branco" />
        </div>
        <div class="form-group">
          <label>Cliente *</label>
          <select name="clienteId" required>
            <option value="">Selecione o cliente</option>
            ${optsClientes}
          </select>
        </div>
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
      placa:     form.placa.value.trim().toUpperCase(),
      marca:     form.marca.value.trim(),
      modelo:    form.modelo.value.trim(),
      cor:       form.cor.value.trim(),
      clienteId: parseInt(form.clienteId.value, 10),
    };
    try {
      if (id) {
        await API.put(`/api/veiculos/${id}`, dados);
        showToast('Veículo atualizado com sucesso', 'success');
      } else {
        await API.post('/api/veiculos', dados);
        showToast('Veículo cadastrado com sucesso', 'success');
      }
      closeModal();
      await carregar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  async function excluir(id) {
    if (!confirm('Deseja excluir este veículo?')) return;
    try {
      await API.delete(`/api/veiculos/${id}`);
      showToast('Veículo excluído', 'success');
      await carregar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function getLista() { return _lista; }

  return { carregar, abrirFormNovo, abrirFormEditar, salvar, excluir, getLista };
})();
