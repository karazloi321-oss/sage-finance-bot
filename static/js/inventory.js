// =====================================================
// INVENTORY
// =====================================================

let inventory = [];

// =====================================================
// LOAD INVENTORY
// =====================================================

function loadInventory(){

    try{

        const saved = localStorage.getItem(
            "sage_inventory"
        );

        if(saved){

            inventory = JSON.parse(saved);

        }

        renderInventory();

    }catch(error){

        console.log(
            "INVENTORY LOAD ERROR",
            error
        );

    }

}

// =====================================================
// SAVE INVENTORY
// =====================================================

function saveInventory(){

    try{

        localStorage.setItem(

            "sage_inventory",

            JSON.stringify(inventory)

        );

    }catch(error){

        console.log(
            "INVENTORY SAVE ERROR",
            error
        );

    }

}

// =====================================================
// ADD PRODUCT
// =====================================================

function addProduct(){

    try{

        const name = document
            .getElementById("productName")
            .value
            .trim();

        const quantity = parseInt(

            document
                .getElementById(
                    "productQuantity"
                )
                .value

        );

        const purchasePrice = parseFloat(

            document
                .getElementById(
                    "purchasePrice"
                )
                .value

        );

        const sellPrice = parseFloat(

            document
                .getElementById(
                    "sellPrice"
                )
                .value

        );

        if(
            !name ||
            !quantity ||
            !purchasePrice ||
            !sellPrice
        ){

            alert(
                "Заполните поля"
            );

            return;

        }

        const product = {

            id:Date.now(),

            name:name,

            quantity:quantity,

            purchase:purchasePrice,

            sell:sellPrice,

            profit:
                sellPrice - purchasePrice,

            total:

                quantity *
                purchasePrice

        };

        inventory.push(product);

        saveInventory();

        renderInventory();

        clearInventoryInputs();

    }catch(error){

        console.log(
            "ADD PRODUCT ERROR",
            error
        );

    }

}

// =====================================================
// RENDER INVENTORY
// =====================================================

function renderInventory(){

    try{

        const list = document
            .getElementById(
                "inventoryList"
            );

        if(!list){
            return;
        }

        list.innerHTML = "";

        if(inventory.length === 0){

            list.innerHTML = `

            <div class="history-sub">

                Склад пуст

            </div>

            `;

            return;

        }

        let totalWarehouse = 0;

        inventory.forEach(item => {

            totalWarehouse += item.total;

            list.innerHTML += `

            <div class="history-item">

                <div>

                    <div class="history-title">

                        ${item.name}

                    </div>

                    <div class="history-sub">

                        Кол-во:
                        ${item.quantity}

                    </div>

                    <div class="history-sub">

                        Закупка:
                        ${item.purchase} ₽

                    </div>

                    <div class="history-sub">

                        Продажа:
                        ${item.sell} ₽

                    </div>

                </div>

                <div class="history-right">

                    <div>

                        <div
                        style="
                        color:#79d279;
                        font-weight:900;
                        "
                        >

                            +${item.profit} ₽

                        </div>

                    </div>

                    <button
                    class="delete-btn"
                    onclick="deleteProduct(${item.id})"
                    >

                    ✕

                    </button>

                </div>

            </div>

            `;

        });

        list.innerHTML += `

        <div
        class="card"
        style="margin-top:18px;"
        >

            <div class="small-title">

                💰 Стоимость склада

            </div>

            <div class="small-value">

                ${totalWarehouse} ₽

            </div>

        </div>

        `;

    }catch(error){

        console.log(
            "RENDER INVENTORY ERROR",
            error
        );

    }

}

// =====================================================
// DELETE PRODUCT
// =====================================================

function deleteProduct(id){

    try{

        inventory = inventory.filter(

            item => item.id !== id

        );

        saveInventory();

        renderInventory();

    }catch(error){

        console.log(
            "DELETE PRODUCT ERROR",
            error
        );

    }

}

// =====================================================
// CLEAR INPUTS
// =====================================================

function clearInventoryInputs(){

    document.getElementById(
        "productName"
    ).value = "";

    document.getElementById(
        "productQuantity"
    ).value = "";

    document.getElementById(
        "purchasePrice"
    ).value = "";

    document.getElementById(
        "sellPrice"
    ).value = "";

}
