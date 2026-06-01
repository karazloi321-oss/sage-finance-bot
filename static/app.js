let balance = 0

const balanceElement = 
    document.getElementById("balance")

function updateBalance() {

    balanceElement.innerText =
        balance + " р"
}

function addExpense(amount) {

    balance -= amount

    updateBalance()
}

function customExpense() {

    const input =
        document.getElementById("customAmount")

    const amount =
        Number(input.value)

    if (!amount) return

    balance -= amount

    input.value = ""

    updateBalance()
}

updateBalance()
