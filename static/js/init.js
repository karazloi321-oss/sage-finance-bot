document.addEventListener(

    "DOMContentLoaded",

    () => {

        try{

            updateCategories();

            loadTransactions?.();

            loadStats?.();

            loadAI?.();

            loadCharts?.();

            loadGoals?.();

            loadDebts?.();

            loadBusinessAnalytics?.();

        }catch(error){

            console.log(
                "INIT ERROR",
                error
            );

        }

    }

);
