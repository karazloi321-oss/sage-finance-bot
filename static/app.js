// =====================================================
// TELEGRAM
// =====================================================

let userId = "demo_user";

if(window.Telegram?.WebApp){

    Telegram.WebApp.ready();

    Telegram.WebApp.expand();

    if(Telegram.WebApp.initDataUnsafe?.user){

        userId = String(
            Telegram.WebApp.initDataUnsafe.user.id
        );

        authUser(
            Telegram.WebApp.initDataUnsafe.user
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

        console.log(error);

    }

}

// =====================================================
// SIDEBAR
// =====================================================

function openSidebar(){

    document
        .getElementById("sidebar")
        .classList.add("open");

    document
        .getElementById("overlay")
        .classList.add("show");

}

function closeSidebar(){

    document
        .getElementById("sidebar")
        .classList.remove("open");

    document
        .getElementById("overlay")
        .classList.remove("show");

}

// =====================================================
// SECTIONS
// =====================================================

function openSection(id, element=null){

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove(
                "active-section"
            );

        });

    const current = document
        .getElementById(id);

    if(current){

        current.classList.add(
            "active-section"
        );

    }

    document
        .querySelectorAll(".nav-item")
        .forEach(item => {

            item.classList.remove(
                "active"
            );

        });

    if(element){

        element.classList.add(
            "active"
        );

    }

    closeSidebar();

}

// =====================================================
// MODAL
// =====================================================

function openModal(){

    document
        .getElementById("modal")
        .classList.add("show");

}

function closeModal(){

    document
        .getElementById("modal")
        .classList.remove("show");

}

function outsideModalClose(event){

    const modal = document
        .getElementById("modal");

    if(event.target === modal){

        closeModal();

    }

}

// =====================================================
// UPDATE CATEGORIES
// =====================================================

function updateCategories(){

    const account = document
        .getElementById("account");

    const type = document
        .getElementById("type");

    const category = document
        .getElementById("category");

    if(
        !account ||
        !type ||
        !category
    ){
        return;
    }

    const accountValue = account.value;

    const typeValue = type.value;

    category.innerHTML = "";

    categories[accountValue][typeValue]
        .forEach(item => {

            category.innerHTML += `

            <option value="${item}">
                ${item}
            </option>

            `;

        });

}

// =====================================================
// TRANSACTIONS
// =====================================================

async function addTransaction(){

    const account = document
        .getElementById("account")
        .value;

    const type = document
        .getElementById("type")
        .value;

    const amount = parseFloat(

        document
            .getElementById("amount")
            .value

    );

    const category = document
        .getElementById("category")
        .value;

    if(!amount || amount <= 0){

        alert("Введите сумму");

        return;

    }

    try{

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

        document
            .getElementById("amount")
            .value = "";

        closeModal();

        loadTransactions();

        loadStats();

        loadAI();

        loadBusinessAnalytics();

    }catch(error){

        console.log(error);

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

        const history = document
            .getElementById("historyList");

        if(!history){
            return;
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
                        ${item.account}
                    </div>

                </div>

                <div class="history-right">

                    <div
                    style="color:${color}"
                    >

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

        const personalBalance = document.getElementById(
            "personalBalance"
        );

        const businessBalance = document.getElementById(
            "businessBalance"
        );

        const totalBalance = document.getElementById(
            "totalBalance"
        );

        if(personalBalance){

            personalBalance.innerHTML =
                `${personal} ₽`;

        }

        if(businessBalance){

            businessBalance.innerHTML =
                `${business} ₽`;

        }

        if(totalBalance){

            totalBalance.innerHTML =
                `${personal + business} ₽`;

        }

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// DELETE
// =====================================================

async function deleteTransaction(id){

    try{

        await fetch(

            `/delete_transaction/${id}`,

            {
                method:"DELETE"
            }

        );

        loadTransactions();

        loadStats();

        loadAI();

        loadBusinessAnalytics();

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// STATS
// =====================================================

async function loadStats(){

    try{

        const response = await fetch(

            `/transactions/${userId}`

        );

        const data = await response.json();

        let income = 0;
        let expense = 0;

        data.forEach(item => {

            if(item.type === "income"){

                income += item.amount;

            }else{

                expense += item.amount;

            }

        });

        const incomeStat = document.getElementById(
            "incomeStat"
        );

        const expenseStat = document.getElementById(
            "expenseStat"
        );

        if(incomeStat){

            incomeStat.innerHTML =
                `${income} ₽`;

        }

        if(expenseStat){

            expenseStat.innerHTML =
                `${expense} ₽`;

        }

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// AI
// =====================================================

async function loadAI(){

    try{

        const response = await fetch(

            `/ai/${userId}`

        );

        const data = await response.json();

        const aiText = document
            .getElementById("aiText");

        if(aiText){

            aiText.innerHTML = data.text;

        }

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// BUSINESS ANALYTICS
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

        const profit = income - expense;

        let margin = 0;

        if(income > 0){

            margin = (
                (profit / income) * 100
            ).toFixed(1);

        }

        const businessIncome = document.getElementById(
            "businessIncome"
        );

        const businessExpense = document.getElementById(
            "businessExpense"
        );

        const businessProfit = document.getElementById(
            "businessProfit"
        );

        const businessMargin = document.getElementById(
            "businessMargin"
        );

        if(businessIncome){

            businessIncome.innerHTML =
                `${income} ₽`;

        }

        if(businessExpense){

            businessExpense.innerHTML =
                `${expense} ₽`;

        }

        if(businessProfit){

            businessProfit.innerHTML =
                `${profit} ₽`;

        }

        if(businessMargin){

            businessMargin.innerHTML =
                `${margin}%`;

        }

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// START APP
// =====================================================

document.addEventListener(

    "DOMContentLoaded",

    () => {

        try{

            updateCategories();

            loadTransactions();

            loadStats();

            loadAI();

            loadBusinessAnalytics();

        }catch(error){

            console.log(
                "INIT ERROR",
                error
            );

        }

    }

);
