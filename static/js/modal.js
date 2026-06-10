// =====================================================
// MODAL
// =====================================================

function openModal(){

    try{

        const modal = document.getElementById(
            "modal"
        );

        if(!modal){
            return;
        }

        modal.classList.add("show");

        document.body.classList.add(
            "modal-open"
        );

    }catch(error){

        console.log(
            "MODAL OPEN ERROR",
            error
        );

    }

}

// =====================================================
// CLOSE MODAL
// =====================================================

function closeModal(){

    try{

        const modal = document.getElementById(
            "modal"
        );

        if(!modal){
            return;
        }

        modal.classList.remove("show");

        document.body.classList.remove(
            "modal-open"
        );

    }catch(error){

        console.log(
            "MODAL CLOSE ERROR",
            error
        );

    }

}

// =====================================================
// OUTSIDE CLICK
// =====================================================

function outsideModalClose(event){

    try{

        const modal = document.getElementById(
            "modal"
        );

        if(event.target === modal){

            closeModal();

        }

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// ESC CLOSE
// =====================================================

document.addEventListener(

    "keydown",

    (event) => {

        if(event.key === "Escape"){

            closeModal();

            closeSidebar();

        }

    }

);

// =====================================================
// SWIPE DOWN CLOSE
// =====================================================

let startY = 0;

document.addEventListener(

    "touchstart",

    (event) => {

        startY = event.touches[0].clientY;

    },

    { passive:true }

);

document.addEventListener(

    "touchmove",

    (event) => {

        const modal = document.getElementById(
            "modal"
        );

        if(
            !modal ||
            !modal.classList.contains("show")
        ){
            return;
        }

        const currentY =
            event.touches[0].clientY;

        const diff = currentY - startY;

        if(diff > 140){

            closeModal();

        }

    },

    { passive:true }

);
