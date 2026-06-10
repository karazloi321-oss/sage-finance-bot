// =====================================================
// CHARTS
// =====================================================

let financeChart = null;

// =====================================================
// LOAD CHARTS
// =====================================================

async function loadCharts(){

    try{

        const response = await fetch(

            `/transactions/${userId}`

        );

        const data = await response.json();

        let income = 0;
        let expense = 0;

        const expenseCategories = {};

        data.forEach(item => {

            if(item.type === "income"){

                income += item.amount;

            }else{

                expense += item.amount;

                if(
                    !expenseCategories[
                        item.category
                    ]
                ){

                    expenseCategories[
                        item.category
                    ] = 0;

                }

                expenseCategories[
                    item.category
                ] += item.amount;

            }

        });

        createFinanceChart(
            income,
            expense
        );

    }catch(error){

        console.log(
            "CHART ERROR",
            error
        );

    }

}

// =====================================================
// FINANCE CHART
// =====================================================

function createFinanceChart(
    income,
    expense
){

    try{

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

                        borderRadius:18,

                        borderSkipped:false

                    }]

                },

                options:{

                    responsive:true,

                    maintainAspectRatio:false,

                    plugins:{

                        legend:{
                            display:false
                        }

                    },

                    scales:{

                        y:{

                            ticks:{
                                color:"#cdd9e5"
                            },

                            grid:{
                                color:"#243247"
                            }

                        },

                        x:{

                            ticks:{
                                color:"#cdd9e5"
                            },

                            grid:{
                                display:false
                            }

                        }

                    }

                }

            }

        );

    }catch(error){

        console.log(
            "CREATE CHART ERROR",
            error
        );

    }

}
