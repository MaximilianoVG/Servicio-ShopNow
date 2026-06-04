const BASE_URL = 'https://servicio-shopnow-inventario.onrender.com';
const TOKEN_KEY = 'shopnow_inventario_token';

function setStatus(id, text, ok = true) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = `status ${ok ? 'ok' : 'err'}`;
}

function getToken() { return localStorage.getItem(TOKEN_KEY) || ''; }
function authHeaders() { return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` }; }

async function loginInventario() {
  try {
    const response = await fetch(`${BASE_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: document.getElementById('invUser').value, password: document.getElementById('invPass').value }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Credenciales inválidas');
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setStatus('loginStatus', 'Token generado correctamente.', true);
  } catch (error) {
    setStatus('loginStatus', error.message, false);
  }
}

async function cargarInventario() {
  try {
    const response = await fetch(`${BASE_URL}/v2/inventario`, { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'No se pudo cargar el inventario');
    const tbody = document.querySelector('#tablaInventario tbody');
    tbody.innerHTML = '';
    (data.inventario || []).forEach((item) => {
      tbody.insertAdjacentHTML('beforeend', `<tr><td>${item.id_producto}</td><td>${item.cantidad}</td></tr>`);
    });
    setStatus('inventarioStatus', `Mostrando ${data.inventario?.length || 0} productos.`, true);
  } catch (error) {
    setStatus('inventarioStatus', error.message, false);
  }
}

async function actualizarInventario() {
  try {
    const body = { id_producto: Number(document.getElementById('inventarioId').value), cantidad: Number(document.getElementById('inventarioCantidad').value) };
    const response = await fetch(`${BASE_URL}/v2/inventario`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al actualizar inventario');
    setStatus('inventarioStatus', data.mensaje || 'Inventario actualizado.', true);
    cargarInventario();
  } catch (error) {
    setStatus('inventarioStatus', error.message, false);
  }
}

async function descontarInventario() {
  try {
    const body = { id_producto: Number(document.getElementById('inventarioId').value), cantidad: Number(document.getElementById('inventarioCantidad').value) };
    const response = await fetch(`${BASE_URL}/v2/inventario/desc`, { method: 'DELETE', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al descontar inventario');
    setStatus('inventarioStatus', data.mensaje || 'Inventario descontado.', true);
    cargarInventario();
  } catch (error) {
    setStatus('inventarioStatus', error.message, false);
  }
}

document.getElementById('loginBtn').addEventListener('click', loginInventario);
document.getElementById('actualizarInventarioBtn').addEventListener('click', actualizarInventario);
document.getElementById('descontarInventarioBtn').addEventListener('click', descontarInventario);
document.getElementById('cargarInventarioBtn').addEventListener('click', cargarInventario);

cargarInventario();
