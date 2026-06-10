// =====================================================
// NAVIGATION
// =====================================================

function openSection(id, element=null){

    try{

        // REMOVE ACTIVE SECTION

        document
            .querySelectorAll(".section")
            .forEach(section => {

                section.classList.remove(
                    "active-section"
                );

            });

        // OPEN CURRENT SECTION

        const current = document
            .getElementById(id);

        if(current){

            current.classList.add(
                "active-section"
            );

        }

        // REMOVE ACTIVE NAV

        document
            .querySelectorAll(".nav-item")
            .forEach(item => {

                item.classList.remove(
                    "active"
                );

            });

        // SET ACTIVE NAV

        if(element){

            element.classList.add(
                "active"
            );

        }

        // SAVE ACTIVE SECTION

        localStorage.setItem(
            "active_section",
            id
        );

        closeSidebar();

        window.scrollTo({

            top:0,

            behavior:"smooth"

        });

    }catch(error){

        console.log(
            "NAVIGATION ERROR",
            error
        );

    }

}

// =====================================================
// SIDEBAR
// =====================================================

function openSidebar(){

    try{

        document
            .getElementById("sidebar")
            .classList.add("open");

        document
            .getElementById("overlay")
            .classList.add("show");

    }catch(error){

        console.log(error);

    }

}

function closeSidebar(){

    try{

        document
            .getElementById("sidebar")
            .classList.remove("open");

        document
            .getElementById("overlay")
            .classList.remove("show");

    }catch(error){

        console.log(error);

    }

}

// =====================================================
// RESTORE ACTIVE SECTION
// =====================================================

function restoreActiveSection(){

    try{

        const saved = localStorage.getItem(
            "active_section"
        );

        if(!saved){
            return;
        }

        document
            .querySelectorAll(".section")
            .forEach(section => {

                section.classList.remove(
                    "active-section"
                );

            });

        const current = document
            .getElementById(saved);

        if(current){

            current.classList.add(
                "active-section"
            );

        }

    }catch(error){

        console.log(error);

    }

}
