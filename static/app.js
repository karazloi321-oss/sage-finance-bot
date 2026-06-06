# ✅ ФИНАЛЬНЫЙ `static/app.js`

// =====================================================
// TELEGRAM
// =====================================================

let userId = "demo_user";

if(window.Telegram?.WebApp){

```
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
```

}

// =====================================================
// AUTH
// =====================================================

async function authUser(user){

```
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
```

}

// =====================================================
// SIDEBAR
// =====================================================

function openSidebar(){

```
document
    .getElementById("sidebar")
    .classList.add("open");

document
    .getElementById("overlay")
    .classList.add("show");
```

}

function closeSidebar(){

```
document
    .getElementById("sidebar")
    .classList.remove("open");

document
    .getElementById("overlay")
    .classList.remove("show");
```

}

// =====================================================
// SECTIONS
// =====================================================

function openSection(id, element=null){

```
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
```

}

// =====================================================
// MODAL
// =====================================================

function openModal(){

```
document
    .getElementById("modal")
    .classList.add("show");
```

}

function closeModal(){

```
document
    .getElementById("modal")
    .classList.remove("show");
```

}

function outsideModalClose(event){

```
const modal = document
    .getElementById("modal");

if(event.target === modal){

    closeModal();

}
```

}

// =====================================================
// TRANSACTIONS
// =====================================================

async function addTransaction(){

```
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

    closeModal();

    loadTransactions();

    loadStats();

    loadAI();

}catch(error){

    console.log(error);

}
```

}

// =====================================================
// LOAD TRANSACTIONS
// =====================================================

async function loadTransactions(){

```
try{

    const response = await fetch(

        `/transactions/${userId}`

    );

    const data = await response.json();

    const history = document
        .getElementById("historyList");

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

            <div
            class="history-right"
            >

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

    document
        .getElementById("personalBalance")
        .innerHTML = `${personal} ₽`;

    document
        .getElementById("businessBalance")
        .innerHTML = `${business} ₽`;

    document
        .getElementById("totalBalance")
        .innerHTML = `${personal + business} ₽`;

}catch(error){

    console.log(error);

}
```

}

// =====================================================
// DELETE
// =====================================================

async function deleteTransaction(id){

```
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

}catch(error){

    console.log(error);

}
```

}

// =====================================================
// STATS
// =====================================================

async function loadStats(){

```
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

    document
        .getElementById("incomeStat")
        .innerHTML = `${income} ₽`;

    document
        .getElementById("expenseStat")
        .innerHTML = `${expense} ₽`;

}catch(error){

    console.log(error);

}
```

}

// =====================================================
// BUDGETS
// =====================================================

async function saveBudget(){

```
const category = document
    .getElementById("budgetCategory")
    .value;

const amount = parseFloat(

    document
        .getElementById("budgetAmount")
        .value

);

if(!amount || amount <= 0){

    return;

}

try{

    await fetch("/save_budget", {

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            user_id:userId,

            category:category,

            amount:amount

        })

    });

    loadBudgets();

}catch(error){

    console.log(error);

}
```

}

async function loadBudgets(){

```
try{

    const response = await fetch(

        `/budgets/${userId}`

    );

    const data = await response.json();

    const list = document
        .getElementById("budgetsList");

    if(!list){

        return;

    }

    list.innerHTML = "";

    data.forEach(item => {

        list.innerHTML += `

        <div class="premium-item">

            <div>
                📦 ${item.category}
            </div>

            <div>
                ${item.amount} ₽
            </div>

        </div>

        `;

    });

}catch(error){

    console.log(error);

}
```

}

// =====================================================
// SUBSCRIPTIONS
// =====================================================

async function saveSubscription(){

```
const title = document
    .getElementById("subscriptionTitle")
    .value;

const amount = parseFloat(

    document
        .getElementById("subscriptionAmount")
        .value

);

if(!amount || amount <= 0){

    return;

}

try{

    await fetch("/save_subscription", {

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            user_id:userId,

            title:title,

            amount:amount

        })

    });

    loadSubscriptions();

}catch(error){

    console.log(error);

}
```

}

async function loadSubscriptions(){

```
try{

    const response = await fetch(

        `/subscriptions/${userId}`

    );

    const data = await response.json();

    const list = document
        .getElementById("subscriptionsList");

    if(!list){

        return;

    }

    list.innerHTML = "";

    data.forEach(item => {

        list.innerHTML += `

        <div class="premium-item">

            <div>
                🔁 ${item.title}
            </div>

            <div>
                ${item.amount} ₽
            </div>

        </div>

        `;

    });

}catch(error){

    console.log(error);

}
```

}

// =====================================================
// AI
// =====================================================

async function loadAI(){

```
try{

    const response = await fetch(

        `/ai_analytics/${userId}`

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
```

}

// =====================================================
// INIT
// =====================================================

loadTransactions();

loadStats();

loadBudgets();

loadSubscriptions();

loadAI();
