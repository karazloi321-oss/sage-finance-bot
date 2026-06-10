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

    Telegram.WebApp.setHeaderColor(
        "#08111f"
    );

    Telegram.WebApp.setBackgroundColor(
        "#08111f"
    );

    if(
        Telegram.WebApp
        .initDataUnsafe?.user
    ){

        userId = String(

            Telegram.WebApp
            .initDataUnsafe
            .user.id

        );

        authUser(

            Telegram.WebApp
            .initDataUnsafe
            .user

        );

    }

}

// =====================================================
// CHARTS
// =====================================================

let expenseChart = null;

let financeChart = null;

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

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

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

    categories[
        accountValue
    ][
        typeValue
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

async function addTransaction(){

    try{

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

            alert(
                "Введите сумму"
            );

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

        document
            .getElementById("amount")
            .value = "";

        closeModal();

        await loadAllData();

    }catch(error){

        console.log(
            "ADD TRANSACTION ERROR",
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

        document.getElementById(
            "personalBalance"
        ).innerHTML = `${personal} ₽`;

        document.getElementById(
            "businessBalance"
        ).innerHTML = `${business} ₽`;

        document.getElementById(
            "totalBalance"
        ).innerHTML =
            `${personal + business} ₽`;

    }catch(error){

        console.log(
            "LOAD TRANSACTIONS ERROR",
            error
        );

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

        document.getElementById(
            "incomeStat"
        ).innerHTML = `${income} ₽`;

        document.getElementById(
            "expenseStat"
        ).innerHTML = `${expense} ₽`;

    }catch(error){

        console.log(
            "STATS ERROR",
            error
        );

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

        document.getElementById(
            "businessIncome"
        ).innerHTML = `${income} ₽`;

        document.getElementById(
            "businessExpense"
        ).innerHTML = `${expense} ₽`;

        document.getElementById(
            "businessProfit"
        ).innerHTML = `${profit} ₽`;

        document.getElementById(
            "businessMargin"
        ).innerHTML = `${margin}%`;

    }catch(error){

        console.log(
            "BUSINESS ERROR",
            error
        );

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

        console.log(
            "AI ERROR",
            error
        );

    }

}

// =====================================================
// CHARTS
// =====================================================

async function loadCharts(){

    try{

        const response = await fetch(

            `/transactions/${userId}`

        );

        const data = await response.json();

        let income = 0;
        let expense = 0;

        const categoriesData = {};

        data.forEach(item => {

            if(item.type === "income"){

                income += item.amount;

            }else{

                expense += item.amount;

                if(
                    !categoriesData[
                        item.category
                    ]
                ){

                    categoriesData[
                        item.category
                    ] = 0;

                }

                categoriesData[
                    item.category
                ] += item.amount;

            }

        });

        // PIE

        const expenseCanvas = document
            .getElementById(
                "expenseChart"
            );

        if(expenseCanvas){

            if(expenseChart){

                expenseChart.destroy();

            }

            expenseChart = new Chart(

                expenseCanvas,

                {

                    type:"doughnut",

                    data:{

                        labels:Object.keys(
                            categoriesData
                        ),

                        datasets:[{

                            data:Object.values(
                                categoriesData
                            ),

                            backgroundColor:[

                                "#6d8ea6",
                                "#9bb6c9",
                                "#7db1d4",
                                "#5d738a",
                                "#bfd3e2",
                                "#7f99ad",
                                "#89a8c0",
                                "#4e657d"

                            ],

                            borderWidth:0

                        }]

                    },

                    options:{

                        responsive:true,

                        plugins:{

                            legend:{

                                labels:{
                                    color:"white"
                                }

                            }

                        }

                    }

                }

            );

        }

        // BAR

        const financeCanvas = document
            .getElementById(
                "financeChart"
            );

        if(financeCanvas){

            if(financeChart){

                financeChart.destroy();

            }

            financeChart = new Chart(

                financeCanvas,

                {

                    type:"bar",

                    data:{

                        labels:[
                            "Доходы",
                            "Расходы"
                        ],

                        datasets:[{

                            data:[
                                income,
                                expense
                            ],

                            backgroundColor:[

                                "#79d279",
                                "#ff7d7d"

                            ],

                            borderRadius:12

                        }]

                    },

                    options:{

                        responsive:true,

                        plugins:{

                            legend:{
                                display:false
                            }

                        },

                        scales:{

                            y:{

                                ticks:{
                                    color:"white"
                                },

                                grid:{
                                    color:"#2a3547"
                                }

                            },

                            x:{

                                ticks:{
                                    color:"white"
                                },

                                grid:{
                                    display:false
                                }

                            }

                        }

                    }

                }

            );

        }

    }catch(error){

        console.log(
            "CHART ERROR",
            error
        );

    }

}

// =====================================================
// LOAD ALL
// =====================================================

async function loadAllData(){

    await loadTransactions();

    await loadStats();

    await loadAI();

    await loadBusinessAnalytics();

    await loadCharts();

    if(window.loadGoals){

        await loadGoals();

    }

    if(window.loadDebts){

        await loadDebts();

    }

}

// =====================================================
// START
// =====================================================

document.addEventListener(

    "DOMContentLoaded",

    async () => {

        try{

            updateCategories();

            await loadAllData();

        }catch(error){

            console.log(
                "INIT ERROR",
                error
            );

        }

    }

);
