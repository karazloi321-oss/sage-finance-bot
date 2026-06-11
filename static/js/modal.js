function openModal(){

    document
        .getElementById("modal")
        .classList.add("show");

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
