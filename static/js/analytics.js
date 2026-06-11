let expenseChart = null;
let financeChart = null;

async function loadCharts(){

    try{

        const response = await fetch(
            `/transactions/${userId}`
        );

        const data =
            await response.json();

        let income = 0;
        let expense = 0;

        const categoriesData = {};

        data.forEach(item => {

            if(item.type === "income"){

                income += item.amount;

            }else{

                expense += item.amount;

                if(!categoriesData[item.category]){

                    categoriesData[
                        item.category
                    ] = 0;

                }

                categoriesData[
                    item.category
                ] += item.amount;

            }

        });

        createExpenseChart(
            categoriesData
        );

        createFinanceChart(
            income,
            expense
        );

    }catch(error){

        console.log(error);

    }

}

function createExpenseChart(
    categoriesData
){

    const canvas =
        document.getElementById(
            "expenseChart"
        );

    if(!canvas){
        return;
    }

    if(expenseChart){

        expenseChart.destroy();

    }

    expenseChart = new Chart(

        canvas,

        {

            type:"doughnut",

            data:{

                labels:Object.keys(
                    categoriesData
                ),

                datasets:[{

                    data:Object.values(
                        categoriesData
                    )

                }]

            }

        }

    );

}

function createFinanceChart(
    income,
    expense
){

    const canvas =
        document.getElementById(
            "financeChart"
        );

    if(!canvas){
        return;
    }

    if(financeChart){

        financeChart.destroy();

    }

    financeChart = new Chart(

        canvas,

        {

            type:"bar",

            data:{

                labels:[
                    "Доход",
                    "Расход"
                ],

                datasets:[{

                    data:[
                        income,
                        expense
                    ]

                }]

            }

        }

    );

}
