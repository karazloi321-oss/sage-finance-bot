// =====================================================
// TELEGRAM
// =====================================================

let userId = "demo_user";

if(window.Telegram?.WebApp){

    Telegram.WebApp.ready();

    Telegram.WebApp.expand();

    if(
        Telegram.WebApp
        .initDataUnsafe?.user
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
// ADD TRANSACTION
// =====================================================



    closeModal();

    loadTransactions();

    loadStats();

    loadBusinessAnalytics();

    loadAI();

    loadCharts();

}
