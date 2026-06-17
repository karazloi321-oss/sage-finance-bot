// =====================================================
// TELEGRAM
// =====================================================

let userId = "demo_user";

if(window.Telegram?.WebApp){

    Telegram.WebApp.ready();

    Telegram.WebApp.expand();

    if(
        Telegram.WebApp.initDataUnsafe?.user
    ){

        userId = String(
            Telegram.WebApp
            .initDataUnsafe
            .user.id
        );

    }

}

// =====================================================
// CATEGORIES
// =====================================================

const categories = {

    personal: {

        income: [

            "💼 Зарплата",
            "💸 Подработка",
            "🏦 Перевод",
            "📈 Инвестиции",
            "📦 Другое"

        ],

        expense: [

            "🍔 Еда",
            "🚕 Транспорт",
            "🏠 Дом",
            "💊 Здоровье",
            "🎮 Развлечения",
            "👕 Одежда",
            "📱 Подписки",
            "📦 Другое"

        ]

    },

    business: {

        income: [

            "🛒 Продажи",
            "💻 Онлайн",
            "📦 Опт",
            "🧾 Услуги",
            "📈 Другое"

        ],

        expense: [

            "📦 Закупка",
            "📢 Реклама",
            "🏢 Аренда",
            "👨‍💼 Зарплата",
            "💸 Налоги",
            "🚚 Логистика",
            "🏦 Комиссии",
            "📉 Другое"

        ]

    }

};

// =====================================================
// UPDATE CATEGORIES
// =====================================================

function updateCategories(){

    const account =
        document.getElementById(
            "account"
        );

    const type =
        document.getElementById(
            "type"
        );

    const category =
        document.getElementById(
            "category"
        );

    if(
        !account ||
        !type ||
        !category
    ){
        return;
    }

    category.innerHTML = "";

    categories[
        account.value
    ][
        type.value
    ].forEach(item => {

        category.innerHTML += `
            <option value="${item}">
                ${item}
            </option>
        `;

    });

}

// =====================================================
// PRODUCTS SELECT
// =====================================================



// =====================================================
// ADD TRANSACTION
// =====================================================

async function addTransaction(){

    const amount = parseFloat(
        document
        .getElementById(
            "amount"
        )
        .value
    );

    if(
        !amount ||
        amount <= 0
    ){

        alert(
            "Введите сумму"
        );

        return;

    }

    try{

        await fetch(

            "/add_transaction",

            {

                method:"POST",

                headers:{

                    "Content-Type":
                    "application/json"

                },

                body:JSON.stringify({

                    user_id:userId,

                    account:
                    document.getElementById(
                        "account"
                    ).value,

                    type:
                    document.getElementById(
                        "type"
                    ).value,

                    amount:amount,

                    category:
                    document.getElementById(
                        "category"
                    ).value,

                    product_id:
                    document.getElementById(
                        "productSelect"
                    )?.value || null,

                    quantity:
                    parseFloat(

                        document.getElementById(
                            "productQty"
                        )?.value

                    ) || null

                })

            }

        );

        document
            .getElementById(
                "amount"
            )
            .value = "";

        if(
            document.getElementById(
                "productQty"
            )
        ){

            document.getElementById(
                "productQty"
            ).value = 1;

        }

        closeModal();

        loadTransactions?.();

        loadStats?.();

        loadBusinessAnalytics?.();

        loadCharts?.();

        loadAI?.();

        loadProducts?.();

        loadWarehouseStats?.();

    }

    catch(error){

        console.log(error);

        alert(
            "Ошибка сохранения"
        );

    }

}
