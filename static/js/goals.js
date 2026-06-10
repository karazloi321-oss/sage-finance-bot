// =====================================================
// SAVE GOAL
// =====================================================

async function saveGoal(){

    try{

        const title = document
            .getElementById("goalTitle")
            .value
            .trim();

        const target = parseFloat(

            document
                .getElementById("goalTarget")
                .value

        );

        if(!title){

            alert(
                "Введите название цели"
            );

            return;

        }

        if(!target || target <= 0){

            alert(
                "Введите сумму цели"
            );

            return;

        }

        await fetch("/save_goal", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                user_id:userId,

                title:title,

                target:target

            })

        });

        document
            .getElementById("goalTitle")
            .value = "";

        document
            .getElementById("goalTarget")
            .value = "";

        await loadGoals();

    }catch(error){

        console.log(
            "SAVE GOAL ERROR",
            error
        );

    }

}

// =====================================================
// ADD MONEY TO GOAL
// =====================================================

async function addToGoal(id){

    try{

        const amount = prompt(
            "Сколько добавить?"
        );

        if(!amount){
            return;
        }

        await fetch(

            `/add_goal_money/${id}`,

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    amount:amount

                })

            }

        );

        await loadGoals();

    }catch(error){

        console.log(
            "ADD GOAL MONEY ERROR",
            error
        );

    }

}

// =====================================================
// LOAD GOALS
// =====================================================

async function loadGoals(){

    try{

        const response = await fetch(

            `/goals/${userId}`

        );

        const data = await response.json();

        const goalsList = document
            .getElementById("goalsList");

        if(!goalsList){
            return;
        }

        goalsList.innerHTML = "";

        if(data.length === 0){

            goalsList.innerHTML = `

            <div
            style="
            opacity:.7;
            padding:10px;
            "
            >

            Пока нет целей

            </div>

            `;

            return;

        }

        data.forEach(goal => {

            let percent = 0;

            if(goal.target > 0){

                percent = Math.min(

                    100,

                    (
                        goal.saved /
                        goal.target
                    ) * 100

                );

            }

            goalsList.innerHTML += `

            <div class="goal-card">

                <div class="goal-top">

                    <div>

                        <div class="goal-title">

                            ${goal.title}

                        </div>

                        <div class="goal-sub">

                            ${goal.saved} ₽
                            из
                            ${goal.target} ₽

                        </div>

                    </div>

                    <div class="goal-percent">

                        ${percent.toFixed(0)}%

                    </div>

                </div>

                <div class="goal-progress">

                    <div
                    class="goal-progress-fill"
                    style="
                    width:${percent}%;
                    "
                    ></div>

                </div>

                <div class="goal-footer">

                    <button
                    class="goal-add-btn"
                    onclick="
                    addToGoal(${goal.id})
                    "
                    >

                        + Пополнить

                    </button>

                </div>

            </div>

            `;

        });

    }catch(error){

        console.log(
            "LOAD GOALS ERROR",
            error
        );

    }

}
