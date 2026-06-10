// =====================================================
// DEBTS
// =====================================================

async function loadDebts(){

    try{

        const response = await fetch(

            `/debts/${userId}`

        );

        const debts = await response.json();

        const container = document
            .getElementById("debtsList");

        if(!container){
            return;
        }

        container.innerHTML = "";

        if(debts.length === 0){

            container.innerHTML = `

            <div class="history-sub">

                Долгов пока нет

            </div>

            `;

            return;

        }

        let giveTotal = 0;
        let takeTotal = 0;

        debts.forEach(debt => {

            let color = "#79d279";
            let text = "Мне должны";

            if(debt.type === "i_debt"){

                color = "#ff7d7d";
                text = "Я должен";

                takeTotal += debt.amount;

            }else{

                giveTotal += debt.amount;

            }

            container.innerHTML += `

            <div class="debt-card">

                <div class="debt-top">

                    <div>

                        <div class="goal-title">

                            ${debt.person}

                        </div>

                        <div
                        class="goal-sub"
                        style="
                        color:${color};
                        "
                        >

                            ${text}

                        </div>

                    </div>

                    <button
                    class="delete-btn"
                    onclick="deleteDebt(${debt.id})"
                    >

                        ✕

                    </button>

                </div>

                <div class="debt-amount">

                    ${debt.amount} ₽

                </div>

                <div class="history-sub">

                    ${debt.created_at}

                </div>

            </div>

            `;

        });

        container.innerHTML += `

        <div class="cards-row">

            <div class="small-card">

                <div class="small-title">

                    💰 Мне должны

                </div>

                <div
                class="small-value"
                style="color:#79d279;"
                >

                    ${giveTotal} ₽

                </div>

            </div>

            <div class="small-card">

                <div class="small-title">

                    📉 Я должен

                </div>

                <div
                class="small-value"
                style="color:#ff7d7d;"
                >

                    ${takeTotal} ₽

                </div>

            </div>

        </div>

        `;

    }catch(error){

        console.log(
            "LOAD DEBTS ERROR",
            error
        );

    }

}

// =====================================================
// SAVE DEBT
// =====================================================

async function saveDebt(){

    try{

        const person = document
            .getElementById("debtPerson")
            .value
            .trim();

        const amount = parseFloat(

            document
                .getElementById(
                    "debtAmount"
                )
                .value

        );

        const type = document
            .getElementById("debtType")
            .value;

        if(
            !person ||
            !amount
        ){

            alert(
                "Заполните поля"
            );

            return;

        }

        await fetch(

            "/save_debt",

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    user_id:userId,

                    person:person,

                    amount:amount,

                    type:type

                })

            }

        );

        document.getElementById(
            "debtPerson"
        ).value = "";

        document.getElementById(
            "debtAmount"
        ).value = "";

        loadDebts();

    }catch(error){

        console.log(
            "SAVE DEBT ERROR",
            error
        );

    }

}

// =====================================================
// DELETE DEBT
// =====================================================

async function deleteDebt(debtId){

    try{

        await fetch(

            `/delete_debt/${debtId}`,

            {
                method:"DELETE"
            }

        );

        loadDebts();

    }catch(error){

        console.log(
            "DELETE DEBT ERROR",
            error
        );

    }

}
