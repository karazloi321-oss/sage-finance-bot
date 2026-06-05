let currentType = "income";

let tg = window.Telegram.WebApp;

tg.expand();

let user = tg.initDataUnsafe.user;

let userId = "demo_user";

if(user){

    userId = user.id;

}

let totalBalance = 0;

let personalBalance = 0;

let businessBalance = 0;

let savingsBalance = 0;

async function auth(){

    await fetch("/auth", {

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            id:userId,

            first_name:user?.first_name || "",

            username:user?.username || ""

        })

    });

}

function openModal(type){

    currentType = type;

    document
        .getElementById("modal")
        .classList.add("show");

}

function closeModal(){

    document
        .getElementById("modal")
        .classList.remove("show");

}

async function saveTransaction(){

    const amount = parseFloat(

        document
            .getElementById("amount")
            .value
    );

    const category = document
        .getElementById("category")
        .value;

    const account = document
        .getElementById("account")
        .value;

    if(!amount || amount <= 0){

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

            type:currentType,

            amount:amount,

            category:category

        })

    });

    document
        .getElementById("amount")
        .value = "";

    document
        .getElementById("category")
        .value = "";

    closeModal();

    loadTransactions();

}

async function loadTransactions(){

    const response = await fetch(

        `/transactions/${userId}`
    );

    const data = await response.json();

    const history = document
        .getElementById("history");

    history.innerHTML = "";

    totalBalance = 0;

    personalBalance = 0;

    businessBalance = 0;

    savingsBalance = 0;

    data.forEach(item => {

        let sign = "+";

        let color = "#7ad97a";

        if(item.type === "expense"){

            sign = "-";

            color = "#ff6b6b";

        }

        if(item.type === "income"){

            totalBalance += item.amount;

        }else{

            totalBalance -= item.amount;

        }

        // PERSONAL

        if(item.account === "personal"){

            if(item.type === "income"){

                personalBalance += item.amount;

            }else{

                personalBalance -= item.amount;

            }

        }

        // BUSINESS

        if(item.account === "business"){

            if(item.type === "income"){

                businessBalance += item.amount;

            }else{

                businessBalance -= item.amount;

            }

        }

        // SAVINGS

        if(item.account === "savings"){

            if(item.type === "income"){

                savingsBalance += item.amount;

            }else{

                savingsBalance -= item.amount;

            }

        }

        history.innerHTML += `

        <div class="history-item">

            <div>

                <div class="history-category">
                    ${item.category}
                </div>

                <div class="history-account">
                    ${item.account}
                </div>

            </div>

            <div
            class="history-amount"
            style="color:${color}"
            >
                ${sign}${item.amount} ₽
            </div>

        </div>

        `;

    });

    document
        .getElementById("balance")
        .innerHTML =
        totalBalance + " ₽";

    document
        .getElementById("personalBalance")
        .innerHTML =
        personalBalance + " ₽";

    document
        .getElementById("businessBalance")
        .innerHTML =
        businessBalance + " ₽";

    renderChart(data);

}

function renderChart(data){

    const expenseMap = {};

    data.forEach(item => {

        if(item.type === "expense"){

            if(!expenseMap[item.category]){

                expenseMap[item.category] = 0;

            }

            expenseMap[item.category] += item.amount;

        }

    });

    const labels = Object.keys(expenseMap);

    const values = Object.values(expenseMap);

    const ctx = document
        .getElementById("chart");

    if(window.financeChart){

        window.financeChart.destroy();

    }

    window.financeChart = new Chart(ctx, {

        type:"doughnut",

        data:{

            labels:labels,

            datasets:[{

                data:values,

                backgroundColor:[

                    "#6d8ea6",
                    "#9bb6c9",
                    "#7db1d4",
                    "#4f6d88",
                    "#8ba8bd"

                ],

                borderWidth:0

            }]

        }

    });

}

function openSection(id, element){

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove(
                "active-section"
            );

        });

    document
        .getElementById(id)
        .classList.add(
            "active-section"
        );

    document
        .querySelectorAll(".nav-item")
        .forEach(item => {

            item.classList.remove(
                "active-nav"
            );

        });

    if(element){

        element.classList.add(
            "active-nav"
        );

    }

    closeSidebar();

}

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

auth();

loadTransactions();
