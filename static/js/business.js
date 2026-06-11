async function loadBusinessAnalytics(){

    const response =
        await fetch(

            `/business_summary/${userId}`

        );

    const data =
        await response.json();

    document.getElementById(
        "businessIncome"
    ).innerHTML =
        `${data.income} ₽`;

    document.getElementById(
        "businessExpense"
    ).innerHTML =
        `${data.expense} ₽`;

    document.getElementById(
        "businessProfit"
    ).innerHTML =
        `${data.profit} ₽`;

    document.getElementById(
        "businessMargin"
    ).innerHTML =
        `${data.margin}%`;

}
