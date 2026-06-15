let warehouseProducts = [];

async function loadWarehouseStats() {

    const res = await fetch(
        "/api/warehouse/stats"
    );

    const data = await res.json();

    document.getElementById(
        "warehouse-products"
    ).innerText =
    data.total_products;

    document.getElementById(
        "warehouse-stock"
    ).innerText =
    data.stock_value.toFixed(2);

    document.getElementById(
        "warehouse-profit"
    ).innerText =
    data.profit_value.toFixed(2);

}

async function loadProducts() {

    const res = await fetch(
        "/api/products"
    );

    warehouseProducts =
    await res.json();

    renderProducts();

}

function renderProducts() {

    const list = document.getElementById(
        "warehouse-list"
    );

    const search =
    document.getElementById(
        "warehouse-search"
    ).value.toLowerCase();

    const filtered =
    warehouseProducts.filter(p =>
        p.name.toLowerCase().includes(search)
    );

    list.innerHTML = "";

    filtered.forEach(product => {

        const margin =
        product.buy_price > 0
        ?
        (
            (
                product.sell_price -
                product.buy_price
            )
            /
            product.buy_price
        ) * 100
        :
        0;

        const card =
        document.createElement("div");

        card.className = "card";

        card.innerHTML = `

            <div
            style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            "
            >

                <div>

                    <b>
                    ${product.name}
                    </b>

                    <br>

                    <small>
                    ${product.category}
                    </small>

                </div>

                <button
                onclick="deleteProduct(${product.id})"
                >
                    🗑
                </button>

            </div>

            <div
            style="
            margin-top:10px;
            "
            >

                Количество:
                ${product.quantity}

                <br>

                Закупка:
                ${product.buy_price}

                <br>

                Продажа:
                ${product.sell_price}

                <br>

                Маржа:
                ${margin.toFixed(0)}%

            </div>

        `;

        list.appendChild(card);

    });

}

async function deleteProduct(id) {

    if(
        !confirm(
            "Удалить товар?"
        )
    ) return;

    await fetch(

        `/api/products/${id}`,

        {
            method:"DELETE"
        }

    );

    loadProducts();

    loadWarehouseStats();

}

async function openAddProduct() {

    const name =
    prompt("Название");

    if(!name) return;

    const category =
    prompt(
        "Категория",
        "Другое"
    );

    const quantity =
    parseFloat(
        prompt(
            "Количество",
            "0"
        )
    ) || 0;

    const buy_price =
    parseFloat(
        prompt(
            "Цена закупки",
            "0"
        )
    ) || 0;

    const sell_price =
    parseFloat(
        prompt(
            "Цена продажи",
            "0"
        )
    ) || 0;

    await fetch(

        "/api/products",

        {

            method:"POST",

            headers:{
                "Content-Type":
                "application/json"
            },

            body:JSON.stringify({

                name,
                category,
                quantity,
                buy_price,
                sell_price

            })

        }

    );

    loadProducts();

    loadWarehouseStats();

}

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const search =
        document.getElementById(
            "warehouse-search"
        );

        if(search){

            search.addEventListener(
                "input",
                renderProducts
            );

        }

        loadProducts();

        loadWarehouseStats();

    }
);
