// =====================================================
// APP START
// =====================================================

document.addEventListener(

    "DOMContentLoaded",

    async () => {

        try{

            // =========================================
            // TELEGRAM UI
            // =========================================

            if(window.Telegram?.WebApp){

                Telegram.WebApp.ready();

                Telegram.WebApp.expand();

                Telegram.WebApp.disableVerticalSwipes();

                Telegram.WebApp.setHeaderColor(
                    "#0f1722"
                );

                Telegram.WebApp.setBackgroundColor(
                    "#0f1722"
                );

            }

            // =========================================
            // CATEGORIES
            // =========================================

            if(window.updateCategories){

                updateCategories();

            }

            // =========================================
            // RESTORE SECTION
            // =========================================

            if(window.restoreActiveSection){

                restoreActiveSection();

            }

            // =========================================
            // LOAD API DATA
            // =========================================

            if(window.loadAllData){

                await loadAllData();

            }

            // =========================================
            // LOAD INVENTORY
            // =========================================

            if(window.loadInventory){

                loadInventory();

            }

            // =========================================
            // FIX ACTIVE NAVBAR
            // =========================================

            syncNavbarState();

            // =========================================
            // AUTO CLOSE SIDEBAR
            // =========================================

            initOutsideClick();

            // =========================================
            // ONLINE STATUS
            // =========================================

            initConnectionListener();

            console.log(
                "SAGE FINANCE V23 STARTED"
            );

        }catch(error){

            console.log(
                "APP INIT ERROR",
                error
            );

        }

    }

);

// =====================================================
// NAVBAR STATE
// =====================================================

function syncNavbarState(){

    try{

        const activeSection =
            localStorage.getItem(
                "active_section"
            );

        if(!activeSection){
            return;
        }

        document
            .querySelectorAll(".nav-item")
            .forEach(item => {

                item.classList.remove(
                    "active"
                );

                const onclick =
                    item.getAttribute(
                        "onclick"
                    );

                if(
                    onclick &&
                    onclick.includes(
                        activeSection
                    )
                ){

                    item.classList.add(
                        "active"
                    );

                }

            });

    }catch(error){

        console.log(
            "NAVBAR ERROR",
            error
        );

    }

}

// =====================================================
// OUTSIDE CLICK
// =====================================================

function initOutsideClick(){

    document.addEventListener(

        "click",

        (event) => {

            const sidebar =
                document.getElementById(
                    "sidebar"
                );

            const menuBtn =
                document.querySelector(
                    ".menu-btn"
                );

            if(
                !sidebar ||
                !sidebar.classList.contains(
                    "open"
                )
            ){
                return;
            }

            if(
                !sidebar.contains(
                    event.target
                ) &&
                !menuBtn.contains(
                    event.target
                )
            ){

                closeSidebar();

            }

        }

    );

}

// =====================================================
// CONNECTION STATUS
// =====================================================

function initConnectionListener(){

    window.addEventListener(

        "offline",

        () => {

            alert(
                "Нет подключения к интернету"
            );

        }

    );

    window.addEventListener(

        "online",

        () => {

            console.log(
                "ONLINE"
            );

        }

    );

}

// =====================================================
// PREVENT IOS ZOOM
// =====================================================

document.addEventListener(

    "gesturestart",

    function(event){

        event.preventDefault();

    }

);

// =====================================================
// FAST CLICK FIX
// =====================================================

document.addEventListener(

    "touchstart",

    () => {},

    {

        passive:true

    }

);

// =====================================================
// GLOBAL ERROR CATCH
// =====================================================

window.onerror = function(

    message,
    source,
    line,
    column,
    error

){

    console.log(

        "GLOBAL ERROR:",

        message,

        source,

        line

    );

};

// =====================================================
// SAFE AREA FIX
// =====================================================

function updateSafeArea(){

    try{

        const navbar =
            document.querySelector(
                ".navbar"
            );

        if(!navbar){
            return;
        }

        navbar.style.paddingBottom =

            `calc(
                16px +
                env(safe-area-inset-bottom)
            )`;

    }catch(error){

        console.log(error);

    }

}

updateSafeArea();
