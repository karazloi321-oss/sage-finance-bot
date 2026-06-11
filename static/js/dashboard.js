async function loadStats(){

    try{

        const response = await fetch(
            `/balance/${userId}`
        );

        const data =
            await response.json();

        const incomeStat =
            document.getElementById(
                "incomeStat"
            );

        const expenseStat =
            document.getElementById(
                "expenseStat"
            );

        const totalBalance =
            document.getElementById(
                "totalBalance"
            );

        if(incomeStat){

            incomeStat.innerHTML =
                `${data.income} ₽`;

        }

        if(expenseStat){

            expenseStat.innerHTML =
                `${data.expense} ₽`;

        }

        if(totalBalance){

            totalBalance.innerHTML =
                `${data.total} ₽`;

        }

    }catch(error){

        console.log(error);

    }

}
