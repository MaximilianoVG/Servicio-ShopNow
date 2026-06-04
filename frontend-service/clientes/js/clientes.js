const BASE_URL = 'https://servicio-shopnow-clientes.onrender.com';
const TOKEN_KEY = 'shopnow_clientes_token';

function setStatus(id, text, ok = true) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = `status ${ok ? 'ok' : 'err'}`;
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

async function loginCliente() {
  const username = document.getElementById('clientUser').value;
  const password = document.getElementById('clientPass').value;
  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Credenciales inválidas');
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setStatus('loginStatus', 'Token generado correctamente.', true);
  } catch (error) {
    setStatus('loginStatus', error.message, false);
  }
}

async function cargarClientes() {
  try {
    const response = await fetch(`${BASE_URL}/v2/clientes/`, { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'No se pudieron cargar los clientes');
    const tbody = document.querySelector('#tablaClientes tbody');
    tbody.innerHTML = '';
    (data.clientes || []).forEach((cliente) => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${cliente.id_cliente}</td>
          <td>${cliente.nombre}</td>
          <td>${cliente.correo}</td>
          <td>${cliente.telefono}</td>
          <td>${cliente.direccion}</td>
          <td>${cliente.activo ? 'Sí' : 'No'}</td>
        </tr>
      `);
    });
    setStatus('clienteStatus', `Mostrando ${data.clientes?.length || 0} clientes.`, true);
  } catch (error) {
    setStatus('clienteStatus', error.message, false);
  }
}

async function crearCliente() {
  try {
    const body = {
      nombre: document.getElementById('clienteNombre').value,
      correo: document.getElementById('clienteCorreo').value,
      telefono: document.getElementById('clienteTelefono').value,
      direccion: document.getElementById('clienteDireccion').value
    };
    const response = await fetch(`${BASE_URL}/v2/clientes/`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al crear cliente');
    setStatus('clienteStatus', data.mensaje || 'Cliente creado.', true);
    cargarClientes();
  } catch (error) {
    setStatus('clienteStatus', error.message, false);
  }
}

async function actualizarCliente() {
  try {
    const body = {
      id_cliente: Number(document.getElementById('clienteId').value),
      nombre: document.getElementById('clienteNombre').value || null,
      correo: document.getElementById('clienteCorreo').value || null,
      telefono: document.getElementById('clienteTelefono').value || null,
      direccion: document.getElementById('clienteDireccion').value || null,
      activo: document.getElementById('clienteActivo').value === 'true'
    };
    const response = await fetch(`${BASE_URL}/v2/clientes/`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al actualizar cliente');
    setStatus('clienteStatus', data.mensaje || 'Cliente actualizado.', true);
    cargarClientes();
  } catch (error) {
    setStatus('clienteStatus', error.message, false);
  }
}

async function eliminarCliente() {
  try {
    const body = { id_cliente: Number(document.getElementById('clienteId').value) };
    const response = await fetch(`${BASE_URL}/v2/clientes/`, { method: 'DELETE', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al eliminar cliente');
    setStatus('clienteStatus', data.mensaje || 'Cliente eliminado.', true);
    cargarClientes();
  } catch (error) {
    setStatus('clienteStatus', error.message, false);
  }
}

document.getElementById('loginBtn').addEventListener('click', loginCliente);
document.getElementById('crearClienteBtn').addEventListener('click', crearCliente);
document.getElementById('actualizarClienteBtn').addEventListener('click', actualizarCliente);
document.getElementById('eliminarClienteBtn').addEventListener('click', eliminarCliente);
document.getElementById('cargarClientesBtn').addEventListener('click', cargarClientes);

cargarClientes();
