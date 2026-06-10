// =====================================================
// USER
// =====================================================

let userId = "demo_user";

// =====================================================
// TELEGRAM
// =====================================================

if(window.Telegram?.WebApp){

    Telegram.WebApp.ready();

    Telegram.WebApp.expand();

    Telegram.WebApp.disableVerticalSwipes();

    if(Telegram.WebApp.initDataUnsafe?.user){

        userId = String(

            Telegram.WebApp
            .initDataUnsafe
            .user
            .id

        );

        authUser(

            Telegram.WebApp
            .initDataUnsafe
            .user

        );

    }

}

// =====================================================
// AUTH
// =====================================================

async function authUser(user){

    try{

        await fetch("/auth", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                id:user.id,

                first_name:user.first_name,

                username:user.username

            })

        });

    }catch(error){

        console.log(
            "AUTH ERROR",
            error
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

    try{

        const account = document.getElementById(
            "account"
        );

        const type = document.getElementById(
            "type"
        );

        const category = document.getElementById(
            "category"
        );

        if(
            !account ||
            !type ||
            !category
        ){
            return;
        }

        const accountValue =
            account.value;

        const typeValue =
            type.value;

        category.innerHTML = "";

        categories
            [accountValue]
            [typeValue]
            .forEach(item => {

                category.innerHTML += `

                <option value="${item}">
                    ${item}
                </option>

                `;

            });

    }catch(error){

        console.log(
            "CATEGORY ERROR",
            error
        );

    }

}

// =====================================================
// ADD TRANSACTION
// =====================================================

async function addTransaction(){

    try{

        const account =
            document.getElementById(
                "account"
            ).value;

        const type =
            document.getElementById(
                "type"
            ).value;

        const amount = parseFloat(

            document.getElementById(
                "amount"
            ).value

        );

        const category =
            document.getElementById(
                "category"
            ).value;

        if(!amount || amount <= 0){

            alert("Введите сумму");

            return;

        }

        await fetch("/add_transaction", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                user_id:userId,

                account:account,

                type:type,

                amount:amount,

                category:category

            })

        });

        document.getElementById(
            "amount"
        ).value = "";

        closeModal();

        await loadAllData();

    }catch(error){

        console.log(
            "ADD ERROR",
            error
        );

    }

}

// =====================================================
// LOAD TRANSACTIONS
// =====================================================

async function loadTransactions(){

    try{

        const response = await fetch(

            `/transactions/${userId}`

        );

        const data = await response.json();

        const history = document.getElementById(
            "historyList"
        );

        if(!history){
            return [];
        }

        history.innerHTML = "";

        let personal = 0;
        let business = 0;

        data.forEach(item => {

            let sign = "+";
            let color = "#79d279";

            if(item.type === "expense"){

                sign = "-";

                color = "#ff7d7d";

            }

            if(item.account === "personal"){

                if(item.type === "income"){
                    personal += item.amount;
                }else{
                    personal -= item.amount;
                }

            }

            if(item.account === "business"){

                if(item.type === "income"){
                    business += item.amount;
                }else{
                    business -= item.amount;
                }

            }

            history.innerHTML += `

            <div class="history-item">

                <div>

                    <div class="history-title">
                        ${item.category}
                    </div>

                    <div class="history-sub">
                        ${item.created_at}
                    </div>

                </div>

                <div class="history-right">

                    <div style="color:${color}">

                        ${sign}${item.amount} ₽

                    </div>

                    <button
                    class="delete-btn"
                    onclick="deleteTransaction(${item.id})"
                    >

                    ✕

                    </button>

                </div>

            </div>

            `;

        });

        updateBalances(
            personal,
            business
        );

        return data;

    }catch(error){

        console.log(
            "LOAD ERROR",
            error
        );

        return [];

    }

}

// =====================================================
// DELETE TRANSACTION
// =====================================================

async function deleteTransaction(id){

    try{

        await fetch(

            `/delete_transaction/${id}`,

            {
                method:"DELETE"
            }

        );

        await loadAllData();

    }catch(error){

        console.log(
            "DELETE ERROR",
            error
        );

    }

}

// =====================================================
// BALANCES
// =====================================================

function updateBalances(
    personal,
    business
){

    const total = personal + business;

    const totalBalance =
        document.getElementById(
            "totalBalance"
        );

    const personalBalance =
        document.getElementById(
            "personalBalance"
        );

    const businessBalance =
        document.getElementById(
            "businessBalance"
        );

    if(totalBalance){
        totalBalance.innerHTML =
            `${total} ₽`;
    }

    if(personalBalance){
        personalBalance.innerHTML =
            `${personal} ₽`;
    }

    if(businessBalance){
        businessBalance.innerHTML =
            `${business} ₽`;
    }

}

// =====================================================
// LOAD AI
// =====================================================

async function loadAI(){

    try{

        const response = await fetch(

            `/ai/${userId}`

        );

        const data = await response.json();

        const aiText =
            document.getElementById(
                "aiText"
            );

        if(aiText){

            aiText.innerHTML =
                data.text;

        }

    }catch(error){

        console.log(
            "AI ERROR",
            error
        );

    }

}

// =====================================================
// LOAD BUSINESS
// =====================================================

async function loadBusinessAnalytics(){

    try{

        const response = await fetch(

            `/transactions/${userId}`

        );

        const data = await response.json();

        let income = 0;
        let expense = 0;

        data.forEach(item => {

            if(item.account !== "business"){
                return;
            }

            if(item.type === "income"){
                income += item.amount;
            }else{
                expense += item.amount;
            }

        });

        const profit =
            income - expense;

        const businessIncome =
            document.getElementById(
                "businessIncome"
            );

        const businessProfit =
            document.getElementById(
                "businessProfit"
            );

        if(businessIncome){

            businessIncome.innerHTML =
                `${income} ₽`;

        }

        if(businessProfit){

            businessProfit.innerHTML =
                `${profit} ₽`;

        }

    }catch(error){

        console.log(
            "BUSINESS ERROR",
            error
        );

    }

}

// =====================================================
// LOAD ALL
// =====================================================

async function loadAllData(){

    await loadTransactions();

    await loadAI();

    await loadBusinessAnalytics();

    if(window.loadCharts){

        await loadCharts();

    }

}
