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
                .getElementById("debtAmount")
                .value

        );

        const type = document
            .getElementById("debtType")
            .value;

        if(!person){

            alert(
                "Введите имя"
            );

            return;

        }

        if(!amount || amount <= 0){

            alert(
                "Введите сумму"
            );

            return;

        }

        await fetch("/save_debt", {

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

        });

        document
            .getElementById("debtPerson")
            .value = "";

        document
            .getElementById("debtAmount")
            .value = "";

        await loadDebts();

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

async function deleteDebt(id){

    try{

        await fetch(

            `/delete_debt/${id}`,

            {

                method:"DELETE",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    user_id:userId

                })

            }

        );

        await loadDebts();

    }catch(error){

        console.log(
            "DELETE DEBT ERROR",
            error
        );

    }

}

// =====================================================
// LOAD DEBTS
// =====================================================

async function loadDebts(){

    try{

        const response = await fetch(

            `/debts/${userId}`

        );

        const data = await response.json();

        const debtsList = document
            .getElementById("debtsList");

        if(!debtsList){
            return;
        }

        debtsList.innerHTML = "";

        if(data.length === 0){

            debtsList.innerHTML = `

            <div
            style="
            opacity:.7;
            padding:10px;
            "
            >

            Долгов пока нет

            </div>

            `;

            return;

        }

        data.forEach(item => {

            let color = "#79d279";

            let label = "💰 Мне должны";

            if(item.type === "i_debt"){

                color = "#ff7d7d";

                label = "📉 Я должен";

            }

            debtsList.innerHTML += `

            <div class="debt-card">

                <div class="debt-top">

                    <div>

                        <div class="history-title">

                            ${item.person}

                        </div>

                        <div class="history-sub">

                            ${label}

                        </div>

                    </div>

                    <button
                    class="delete-btn"
                    onclick="
                    deleteDebt(${item.id})
                    "
                    >

                        ✕

                    </button>

                </div>

                <div
                class="debt-amount"
                style="
                color:${color};
                "
                >

                    ${item.amount} ₽

                </div>

                <div
                class="history-sub"
                style="
                margin-top:10px;
                "
                >

                    ${item.created_at}

                </div>

            </div>

            `;

        });

    }catch(error){

        console.log(
            "LOAD DEBTS ERROR",
            error
        );

    }

}
