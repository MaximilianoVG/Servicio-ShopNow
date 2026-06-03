async function cargarProductos(){

    const token =
        localStorage.getItem("token");

    try{

        const response =
        await fetch(
            `${API_URL}/v2/productos`,
            {
                headers:{
                    "Authorization":
                    `Bearer ${token}`
                }
            }
        );

        const productos =
            await response.json();

        console.log(productos);

        const tbody =
        document.querySelector(
            "#tablaProductos tbody"
        );

        tbody.innerHTML = "";

        productos.forEach(producto => {

            tbody.innerHTML += `
                <tr>
                    <td>${producto.id_producto}</td>
                    <td>${producto.nombre}</td>
                    <td>$${producto.precio}</td>
                    <td>${producto.stock}</td>
                    <td>${producto.categoria}</td>
                    <td>
                        ${producto.disponible
                            ? "Sí"
                            : "No"}
                    </td>
                </tr>
            `;
        });

    }catch(error){

        console.error(
            "Error cargando productos",
            error
        );
    }
}

cargarProductos();  