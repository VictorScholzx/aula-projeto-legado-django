const Clientes = (() => {
  let _lista = [];

  async function carregar() {
    try {
      _lista = await API.get('/api/clientes');
      renderizar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function renderizar() {
    const tbody = document.getElementById('tbody-clientes');
    if (_lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:24px">Nenhum cliente cadastrado</td></tr>';
      return;
    }
    tbody.innerHTML = _lista.map(c => `
      <tr>
        <td>${c.id}</td>
        <td>${esc(c.nome)}</td>
        <td>${esc(c.cpf)}</td>
        <td>${esc(c.telefone || '–')}</td>
        <td>${esc(c.email || '–')}</td>
        <td>
          <div class="btn-group">
            <button class="btn btn-outline btn-sm" onclick="Clientes.abrirFormEditar(${c.id})">Editar</button>
            <button class="btn btn-danger  btn-sm" onclick="Clientes.excluir(${c.id})">Excluir</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  function abrirFormNovo() {
    openModal('Novo Cliente', formHtml());
  }

  function abrirFormEditar(id) {
    const c = _lista.find(x => x.id === id);
    if (!c) return;
    openModal('Editar Cliente', formHtml(c));
  }

  function formHtml(c = {}) {
    return `
      <form class="modal-form" onsubmit="Clientes.salvar(event, ${c.id || 'null'})">
        <div class="form-group">
          <label>Nome *</label>
          <input name="nome" value="${esc(c.nome || '')}" required placeholder="Nome completo" />
        </div>
        <div class="form-group">
          <label>CPF *</label>
          <input name="cpf" value="${esc(c.cpf || '')}" required placeholder="000.000.000-00" />
        </div>
        <div class="form-group">
          <label>Telefone</label>
          <input name="telefone" value="${esc(c.telefone || '')}" placeholder="(11) 99999-9999" />
        </div>
        <div class="form-group">
          <label>E-mail</label>
          <input name="email" type="email" value="${esc(c.email || '')}" placeholder="email@exemplo.com" />
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
      nome:     form.nome.value.trim(),
      cpf:      form.cpf.value.trim(),
      telefone: form.telefone.value.trim(),
      email:    form.email.value.trim(),
    };
    try {
      if (id) {
        await API.put(`/api/clientes/${id}`, dados);
        showToast('Cliente atualizado com sucesso', 'success');
      } else {
        await API.post('/api/clientes', dados);
        showToast('Cliente cadastrado com sucesso', 'success');
      }
      closeModal();
      await carregar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  async function excluir(id) {
    if (!confirm('Deseja excluir este cliente?')) return;
    try {
      await API.delete(`/api/clientes/${id}`);
      showToast('Cliente excluído', 'success');
      await carregar();
    } catch (e) {
      showToast(e.message, 'error');
    }
  }

  function getLista() { return _lista; }

  return { carregar, abrirFormNovo, abrirFormEditar, salvar, excluir, getLista };
})();
