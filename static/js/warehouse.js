let warehouseProducts = [];

// ====================================
// LOAD STATS
// ====================================

async function loadWarehouseStats() {

    if (!userId) return;

    const res = await fetch(
        `/api/warehouse/stats/${userId}`
    );

    const data = await res.json();

    const productsEl =
        document.getElementById(
            "warehouse-products"
        );

    const stockEl =
        document.getElementById(
            "warehouse-stock"
        );

    const profitEl =
        document.getElementById(
            "warehouse-profit"
        );

    if (productsEl)
        productsEl.innerText =
            data.total_products;

    if (stockEl)
        stockEl.innerText =
            data.stock_value.toFixed(2);

    if (profitEl)
        profitEl.innerText =
            data.profit_value.toFixed(2);

}

// ====================================
// LOAD PRODUCTS
// ====================================

async function loadProducts() {

    if (!userId) return;

    const res = await fetch(
        `/api/products/${userId}`
    );

    warehouseProducts =
        await res.json();

    renderProducts();

}

// ====================================
// RENDER
// ====================================

function renderProducts() {

    const list =
        document.getElementById(
            "warehouse-list"
        );

    if (!list) return;

    const searchInput =
        document.getElementById(
            "warehouse-search"
        );

    const search =
        searchInput
            ? searchInput.value.toLowerCase()
            : "";

    const filtered =
        warehouseProducts.filter(
            p =>
                (p.name || "")
                    .toLowerCase()
                    .includes(search)
        );

    list.innerHTML = "";

    filtered.forEach(product => {

        const margin =
            product.buy_price > 0
                ? (
                    (
                        product.sell_price -
                        product.buy_price
                    ) /
                    product.buy_price
                ) * 100
                : 0;

        const card =
            document.createElement(
                "div"
            );

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

<div
style="
font-weight:700;
font-size:15px;
"
>
${product.name}
</div>

<div
style="
opacity:.6;
font-size:12px;
margin-top:2px;
"
>
${product.category}
</div>

</div>

<button
onclick="deleteProduct(${product.id})"
class="delete-btn"
>
🗑
</button>

</div>

<div
style="
margin-top:8px;
font-size:13px;
opacity:.85;
line-height:1.5;
"
>

📦 ${product.quantity}
•
Закупка ${product.buy_price}
•
Продажа ${product.sell_price}
•
Маржа ${margin.toFixed(0)}%

</div>

<div
style="
display:flex;
gap:6px;
margin-top:12px;
flex-wrap:wrap;
"
>

<button
class="button"
style="
width:auto;
padding:10px 14px;
margin-top:0;
"
onclick="editProduct(${product.id})"
>
✏️ Изменить
</button>

<button
class="button"
style="
width:auto;
padding:10px 14px;
margin-top:0;
"
onclick="stockIn(${product.id})"
>
➕ Приход
</button>

<button
class="button"
style="
width:auto;
padding:10px 14px;
margin-top:0;
"
onclick="stockOut(${product.id})"
>
➖ Расход
</button>

</div>

`;

        list.appendChild(card);

    });

}

// ====================================
// DELETE
// ====================================

async function deleteProduct(id) {

    if (
        !confirm(
            "Удалить товар?"
        )
    ) return;

    await fetch(
        `/api/products/${id}`,
        {
            method: "DELETE",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                user_id: userId
            })
        }
    );

    await loadProducts();
    await loadWarehouseStats();

}

// ====================================
// EDIT
// ====================================

async function editProduct(id) {

    const product =
        warehouseProducts.find(
            p => p.id === id
        );

    if (!product) return;

    const name =
        prompt(
            "Название",
            product.name
        );

    if (!name) return;

    const category =
        prompt(
            "Категория",
            product.category
        );

    const quantity =
        parseFloat(
            prompt(
                "Количество",
                product.quantity
            )
        ) || 0;

    const buy_price =
        parseFloat(
            prompt(
                "Закупка",
                product.buy_price
            )
        ) || 0;

    const sell_price =
        parseFloat(
            prompt(
                "Продажа",
                product.sell_price
            )
        ) || 0;

    await fetch(
        `/api/products/${id}`,
        {
            method: "PUT",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                user_id: userId,

                name,
                category,
                quantity,
                buy_price,
                sell_price

            })
        }
    );

    await loadProducts();
    await loadWarehouseStats();

}

// ====================================
// STOCK IN
// ====================================

async function stockIn(id) {

    const qty =
        parseFloat(
            prompt(
                "Количество прихода",
                "1"
            )
        );

    if (
        isNaN(qty) ||
        qty <= 0
    ) return;

    await fetch(
        `/api/products/${id}/stock`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                user_id: userId,

                quantity: qty

            })
        }
    );

    await loadProducts();
    await loadWarehouseStats();

}

// ====================================
// STOCK OUT
// ====================================

async function stockOut(id) {

    const qty =
        parseFloat(
            prompt(
                "Количество расхода",
                "1"
            )
        );

    if (
        isNaN(qty) ||
        qty <= 0
    ) return;

    await fetch(
        `/api/products/${id}/stock`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                user_id: userId,

                quantity: -qty

            })
        }
    );

    await loadProducts();
    await loadWarehouseStats();

}

// ====================================
// ADD PRODUCT
// ====================================

async function openAddProduct() {

    const name =
        prompt(
            "Название"
        );

    if (!name) return;

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
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                user_id: userId,

                name,
                category,
                quantity,
                buy_price,
                sell_price

            })
        }
    );

    await loadProducts();
    await loadWarehouseStats();

}

// ====================================
// INIT
// ====================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const search =
            document.getElementById(
                "warehouse-search"
            );

        if (search) {

            search.addEventListener(
                "input",
                renderProducts
            );

        }

        loadProducts();
        loadWarehouseStats();

    }
);
