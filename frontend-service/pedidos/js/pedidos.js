const BASE_URL = 'https://servicio-shopnow-pedidos.onrender.com';
const TOKEN_KEY = 'shopnow_pedidos_token';

function setStatus(id, text, ok = true) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = `status ${ok ? 'ok' : 'err'}`;
}

function getToken() { return localStorage.getItem(TOKEN_KEY) || ''; }
function authHeaders() { return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` }; }

async function loginPedido() {
  try {
    const response = await fetch(`${BASE_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: document.getElementById('pedUser').value, password: document.getElementById('pedPass').value }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Credenciales inválidas');
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setStatus('loginStatus', 'Token generado correctamente.', true);
  } catch (error) {
    setStatus('loginStatus', error.message, false);
  }
}

async function cargarPedidos() {
  try {
    const response = await fetch(`${BASE_URL}/v2/pedidos/`, { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'No se pudieron cargar los pedidos');
    const tbody = document.querySelector('#tablaPedidos tbody');
    tbody.innerHTML = '';
    (data.pedidos || []).forEach((pedido) => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${pedido.id_pedido}</td>
          <td>${pedido.id_cliente}</td>
          <td>${pedido.id_producto}</td>
          <td>${pedido.cantidad}</td>
          <td>${pedido.estado || 'pendiente'}</td>
          <td>${Number(pedido.total || 0).toFixed(2)}</td>
        </tr>
      `);
    });
    setStatus('pedidoStatus', `Mostrando ${data.pedidos?.length || 0} pedidos.`, true);
  } catch (error) {
    setStatus('pedidoStatus', error.message, false);
  }
}

async function crearPedido() {
  try {
    const body = {
      id_cliente: Number(document.getElementById('pedidoCliente').value),
      id_producto: Number(document.getElementById('pedidoProducto').value),
      cantidad: Number(document.getElementById('pedidoCantidad').value),
      descuento: Number(document.getElementById('pedidoDescuento').value || 0)
    };
    const response = await fetch(`${BASE_URL}/v2/pedidos/`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al crear pedido');
    setStatus('pedidoStatus', data.mensaje || 'Pedido creado.', true);
    cargarPedidos();
  } catch (error) {
    setStatus('pedidoStatus', error.message, false);
  }
}

document.getElementById('loginBtn').addEventListener('click', loginPedido);
document.getElementById('crearPedidoBtn').addEventListener('click', crearPedido);
document.getElementById('cargarPedidosBtn').addEventListener('click', cargarPedidos);

cargarPedidos();
