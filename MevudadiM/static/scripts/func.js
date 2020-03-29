// create the photo


// set hide function when clicking on screen
document.getElementById("help").onclick = function(){
    setTimeout(function (){
        document.getElementById("haveChosen").style.display = "none";
    }, 600); 
    document.getElementById("haveChosen").style.opacity = 0;
};

document.getElementById("help2").onclick = function(){
    setTimeout(function (){
        document.getElementById("login").style.display = "none";
    }, 500); 
    document.getElementById("login").style.opacity = 0;
    document.getElementById("help2").style.display = "none";
};

// set chosen onclick for all photos
var cards = document.getElementsByClassName('card');
for(var i = 0; i < cards.length; i++) {

    var card = cards[i];

    card.style.animation = "cardEntrece 1500ms ease-out "+(i+1)*150+"ms 1 normal forwards running";
    console.log(card.style.animationDelay);
    

    card.onclick = function() {
        var card = event.srcElement;
        var card_image = card.style.backgroundImage;
        var card_image = card_image.substr(5, card_image.length-7);
        document.getElementById("chosenImage").src = card_image;
        var myStr = card_image.split(".");
        myStr.pop();
        myStr = myStr.join();
        myStr = myStr.replace("/static/memes/", "")
        document.getElementById("imageTitle").innerText = myStr;
        document.getElementById("haveChosen").style.display = "block";
        setTimeout(function (){
            setTimeout(document.getElementById("haveChosen").style.opacity = 1, 1000);
        }, 100); 
}
}

function inViewPort(dom){
    var h1 = document.getElementById("test")
    var bounding = h1.getBoundingClientRect();
    if (
        bounding.top >= 0 &&
        bounding.left >= 0 &&
        bounding.right <= (window.innerWidth || document.documentElement.clientWidth) &&
        bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight)
    ) {
        console.log('In the viewport!');
    } else {
        console.log('Not in the viewport... whomp whomp');
    }
}

function toggleLogin(){
    if (document.getElementById("login").style.display == "block"){
        document.getElementById("help2").style.display = "none";
        setTimeout(function (){
            document.getElementById("login").style.display = "none"
        }, 500); 
        document.getElementById("login").style.opacity = 0
    }else{
        setTimeout(function (){
        document.getElementById("login").style.opacity = 1
        }, 50); 
        document.getElementById("login").style.display = "block";
        document.getElementById("help2").style.display = "block";
    }
}