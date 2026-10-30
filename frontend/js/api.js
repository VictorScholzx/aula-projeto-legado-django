/**
 * Wrapper simples para a Fetch API.
 */
const API = {
  async _request(method, url, data) {
    const options = { method, headers: {} };
    if (data !== undefined) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(data);
    }
    const res = await fetch(url, options);

    // Sem corpo (204)
    if (res.status === 204) return null;

    const json = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = (json && json.error) ? json.error : `Erro ${res.status}`;
      throw new Error(msg);
    }
    return json;
  },

  get:    (url)       => API._request('GET',    url),
  post:   (url, data) => API._request('POST',   url, data),
  put:    (url, data) => API._request('PUT',    url, data),
  delete: (url)       => API._request('DELETE', url),
};
