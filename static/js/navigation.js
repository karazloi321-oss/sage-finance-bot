function openSidebar(){

    document
        .getElementById("sidebar")
        .classList.add("open");

    document
        .getElementById("overlay")
        .classList.add("show");

}

function closeSidebar(){

    document
        .getElementById("sidebar")
        .classList.remove("open");

    document
        .getElementById("overlay")
        .classList.remove("show");

}

function openSection(id, element=null){

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove(
                "active-section"
            );

        });

    const current = document
        .getElementById(id);

    if(current){

        current.classList.add(
            "active-section"
        );

    }

    document
        .querySelectorAll(".nav-item")
        .forEach(item => {

            item.classList.remove(
                "active"
            );

        });

    if(element){

        element.classList.add(
            "active"
        );

    }

    closeSidebar();

}
