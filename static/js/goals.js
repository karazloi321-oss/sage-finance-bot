// =====================================================
// GOALS
// =====================================================

async function loadGoals(){

    try{

        const response = await fetch(

            `/goals/${userId}`

        );

        const goals = await response.json();

        const container = document
            .getElementById("goalsList");

        if(!container){
            return;
        }

        container.innerHTML = "";

        if(goals.length === 0){

            container.innerHTML = `

            <div class="history-sub">

                Целей пока нет

            </div>

            `;

            return;

        }

        goals.forEach(goal => {

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

            percent = percent.toFixed(1);

            container.innerHTML += `

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

                    <button
                    class="delete-btn"
                    onclick="deleteGoal(${goal.id})"
                    >

                        ✕

                    </button>

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

                    <div class="goal-percent">

                        ${percent}%

                    </div>

                    <button
                    class="goal-add-btn"
                    onclick="addMoneyGoal(${goal.id})"
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
                .getElementById(
                    "goalTarget"
                )
                .value

        );

        if(
            !title ||
            !target
        ){

            alert(
                "Заполните поля"
            );

            return;

        }

        await fetch(

            "/save_goal",

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    user_id:userId,

                    title:title,

                    target:target

                })

            }

        );

        document.getElementById(
            "goalTitle"
        ).value = "";

        document.getElementById(
            "goalTarget"
        ).value = "";

        loadGoals();

    }catch(error){

        console.log(
            "SAVE GOAL ERROR",
            error
        );

    }

}

// =====================================================
// ADD MONEY
// =====================================================

async function addMoneyGoal(goalId){

    try{

        const amount = prompt(
            "Сумма пополнения"
        );

        if(!amount){
            return;
        }

        await fetch(

            "/add_goal_money",

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    goal_id:goalId,

                    amount:parseFloat(amount)

                })

            }

        );

        loadGoals();

    }catch(error){

        console.log(
            "ADD GOAL MONEY ERROR",
            error
        );

    }

}

// =====================================================
// DELETE GOAL
// =====================================================

async function deleteGoal(goalId){

    try{

        await fetch(

            `/delete_goal/${goalId}`,

            {
                method:"DELETE"
            }

        );

        loadGoals();

    }catch(error){

        console.log(
            "DELETE GOAL ERROR",
            error
        );

    }

}
