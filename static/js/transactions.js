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

@transactions_bp.route(
    "/add_transaction",
    methods=["POST"]
)
def add_transaction():

    data = request.json

    user_id = str(data.get("user_id"))

    account = data.get("account")

    t_type = data.get("type")

    amount = float(data.get("amount", 0))

    category = data.get("category", "Другое")

    # ➕ НОВОЕ: товар из склада (опционально)
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if amount <= 0:
        return jsonify({"error": "invalid amount"}), 400

    conn = get_conn()
    c = conn.cursor()

    # 1. сохраняем транзакцию
    c.execute("""
        INSERT INTO transactions
        (
            user_id,
            account,
            type,
            amount,
            category,
            created_at,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        account,
        t_type,
        amount,
        category,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        time.time()
    ))

    # 2. ➕ ЕСЛИ ЭТО ПРОДАЖА ТОВАРА — списываем склад
    if account == "business" and t_type == "income" and product_id and quantity:

        c.execute("""
            SELECT quantity, buy_price, sell_price
            FROM products
            WHERE id=?
        """, (product_id,))

        product = c.fetchone()

        if product:

            new_qty = float(product["quantity"]) - float(quantity)

            if new_qty < 0:
                new_qty = 0

            c.execute("""
                UPDATE products
                SET quantity=?
                WHERE id=?
            """, (new_qty, product_id))

            # ➕ лог движения (если есть таблица)
            try:
                c.execute("""
                    INSERT INTO stock_movements
                    (product_id, movement_type, quantity, comment, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    product_id,
                    "sale",
                    quantity,
                    "Продажа через бизнес",
                    datetime.now().strftime("%d.%m.%Y %H:%M")
                ))
            except:
                pass

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

    closeModal();

    loadTransactions();

    loadStats();

    loadBusinessAnalytics();

    loadAI();

    loadCharts();

}
