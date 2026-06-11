async function loadAI(){

    const response =
        await fetch(

            `/ai/${userId}`

        );

    const data =
        await response.json();

    const aiText =
        document.getElementById(
            "aiText"
        );

    if(aiText){

        aiText.innerHTML =
            data.text;

    }

}
