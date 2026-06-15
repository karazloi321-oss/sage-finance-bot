function openModal(){

    document
        .getElementById("modal")
        .classList.add("show");

    if(
        typeof loadProductsToSelect
        === "function"
    ){
        loadProductsToSelect();
    }

}

function closeModal(){

    document
        .getElementById("modal")
        .classList.remove("show");

}

function outsideModalClose(event){

    const modal = document
        .getElementById("modal");

    if(event.target === modal){

        closeModal();

    }

}
