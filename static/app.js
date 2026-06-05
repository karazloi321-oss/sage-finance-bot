const tg = window.Telegram.WebApp;

tg.expand();

const user = tg.initDataUnsafe.user;

let USER_ID = "guest";

let CURRENT_TYPE = "income";

if(user){

    USER_ID = user.id;

    document.getElementById("avatar")
        .innerHTML = user.first_name[0];

    fetch("/auth", {

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

}

async function loadTransactions(){

    const res = await fetch(
        `/transactions/${USER_ID}`
    );

    const data = await res.json();

    const history =
        document.getElementById("history");

    history.innerHTML = "";

    let balance = 0;

let personal = 0;
let business = 0;
let savings = 0;

    data.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "history-item";

        let icon = "📈";
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

if(item.account === "savings"){

    if(item.type === "income"){
        savings += item.amount;
    }else{
        savings -= item.amount;
    }

}
        if(item.type === "expense"){

            icon = "📉";

            balance -= item.amount;

        }else{

            balance += item.amount;
        }

        div.innerHTML = `
        <div class="history-left">

            <div class="icon">
                ${icon}
            </div>

            <div>
                <div>${item.category}</div>
            </div>

        </div>

        <div class="amount">
            ${item.amount} ₽
        </div>
        `;

        history.appendChild(div);

    });

    document.getElementById("balance")
        .innerHTML = balance + " ₽";

    loadAnalytics();
}

async function loadAnalytics(){

    const res = await fetch(
        `/analytics/${USER_ID}`
    );

    const data = await res.json();

    const labels = [];
    const values = [];

    data.forEach(item => {

        labels.push(item.category);
        values.push(item.total);

    });

    const ctx =
        document.getElementById("chart");

    if(window.financeChart){
        window.financeChart.destroy();
    }

    window.financeChart =
        new Chart(ctx, {

        type:"doughnut",

        data:{
            labels:labels,

            datasets:[{
                data:values
            }]
        }

    });

}

function openModal(type){

    CURRENT_TYPE = type;

    document
        .getElementById("modal")
        .classList.add("show");

    tg.MainButton.setText("Сохранить");
    tg.MainButton.show();

    tg.MainButton.onClick(saveTransaction);
}

function closeModal(){

    document
        .getElementById("modal")
        .classList.remove("show");

    tg.MainButton.hide();
}

async function saveTransaction(){

    const amount =
        document.getElementById("amount").value;

    const category =
        document.getElementById("category").value;
const account =
    document.getElementById("account").value;
    if(!amount || !category){
        return;
    }

    await fetch("/add_transaction", {

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            user_id:USER_ID,

            type:CURRENT_TYPE,

            amount:amount,

            category:category,
account:account

        })

    });

    closeModal();

    document.getElementById("amount").value = "";
    document.getElementById("category").value = "";

    loadTransactions();
}

loadTransactions();
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
document.getElementById(
    "personalBalance"
).innerHTML =
    personal + " ₽";

document.getElementById(
    "businessBalance"
).innerHTML =
    business + " ₽";
