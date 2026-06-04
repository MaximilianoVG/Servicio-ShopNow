const BASE_URL = 'https://servicio-shopnow-productos-jlsr.onrender.com';
const TOKEN_KEY = 'shopnow_productos_token';

function setStatus(id, text, ok = true) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = `status ${ok ? 'ok' : 'err'}`;
}

function getToken() { return localStorage.getItem(TOKEN_KEY) || ''; }
function authHeaders() { return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` }; }

async function loginProducto() {
  try {
    const response = await fetch(`${BASE_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: document.getElementById('prodUser').value, password: document.getElementById('prodPass').value }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Credenciales inválidas');
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setStatus('loginStatus', 'Token generado correctamente.', true);
  } catch (error) {
    setStatus('loginStatus', error.message, false);
  }
}

async function cargarProductos() {
  try {
    const response = await fetch(`${BASE_URL}/v2/productos/`, { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'No se pudieron cargar los productos');
    const tbody = document.querySelector('#tablaProductos tbody');
    tbody.innerHTML = '';
    (data.productos || []).forEach((producto) => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${producto.id_producto}</td>
          <td>${producto.descripcion}</td>
          <td>$${Number(producto.precio).toFixed(2)}</td>
          <td>${producto.activo ? 'Sí' : 'No'}</td>
        </tr>
      `);
    });
    setStatus('productoStatus', `Mostrando ${data.productos?.length || 0} productos.`, true);
  } catch (error) {
    setStatus('productoStatus', error.message, false);
  }
}

async function crearProducto() {
  try {
    const body = { descripcion: document.getElementById('productoDescripcion').value, precio: Number(document.getElementById('productoPrecio').value) };
    const response = await fetch(`${BASE_URL}/v2/productos/`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al crear producto');
    setStatus('productoStatus', data.mensaje || 'Producto creado.', true);
    cargarProductos();
  } catch (error) {
    setStatus('productoStatus', error.message, false);
  }
}

async function actualizarProducto() {
  try {
    const body = {
      id_producto: Number(document.getElementById('productoId').value),
      descripcion: document.getElementById('productoDescripcion').value || null,
      precio: Number(document.getElementById('productoPrecio').value) || null,
      activo: document.getElementById('productoActivo').value === 'true'
    };
    const response = await fetch(`${BASE_URL}/v2/productos/`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al actualizar producto');
    setStatus('productoStatus', data.mensaje || 'Producto actualizado.', true);
    cargarProductos();
  } catch (error) {
    setStatus('productoStatus', error.message, false);
  }
}

async function eliminarProducto() {
  try {
    const body = { id_producto: Number(document.getElementById('productoId').value) };
    const response = await fetch(`${BASE_URL}/v2/productos/`, { method: 'DELETE', headers: authHeaders(), body: JSON.stringify(body) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Error al eliminar producto');
    setStatus('productoStatus', data.mensaje || 'Producto eliminado.', true);
    cargarProductos();
  } catch (error) {
    setStatus('productoStatus', error.message, false);
  }
}

document.getElementById('loginBtn').addEventListener('click', loginProducto);
document.getElementById('crearProductoBtn').addEventListener('click', crearProducto);
document.getElementById('actualizarProductoBtn').addEventListener('click', actualizarProducto);
document.getElementById('eliminarProductoBtn').addEventListener('click', eliminarProducto);
document.getElementById('cargarProductosBtn').addEventListener('click', cargarProductos);

cargarProductos();
