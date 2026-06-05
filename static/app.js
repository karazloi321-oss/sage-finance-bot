const tg = window.Telegram.WebApp;

tg.expand();

const user = tg.initDataUnsafe.user;

let USER_ID = "guest";

if(user){

    USER_ID = user.id;

    document.getElementById("avatar").innerHTML =
        user.first_name[0];

    // AUTH
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

    data.forEach(item => {

        const div =
            document.createElement("div");

        div.className = "history-item";

        let icon = "📈";

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
}

async function addTransaction(type){

    const amount = prompt("Сумма");

    if(!amount) return;

    const category = prompt("Категория");

    if(!category) return;

    await fetch("/add_transaction", {

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            user_id:USER_ID,

            type:type,

            amount:amount,

            category:category

        })

    });

    loadTransactions();
}

function openIncome(){
    addTransaction("income");
}

function openExpense(){
    addTransaction("expense");
}

loadTransactions();
