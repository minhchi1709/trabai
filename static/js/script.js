          
function change_index(x) {
    x.src = "../static/images/enterhover.jpg";
}
function out_index(x) {
    x.src = "../static/images/enter.jpg";
} 

function change_test(x) {
    x.src = "../static/images/continue2.jpg";
}
function out_test(x) {
    x.src = "../static/images/continue1.jpg";
} 

function change_back(x) {
    x.src = "../static/images/back2.jpg";
}
function out_back(x) {
    x.src = "../static/images/back1.jpg";
}

function change_del(x) {
    x.src = "../static/images/del2.jpg";
}
function out_del(x) {
    x.src = "../static/images/del1.jpg";
}

function change_add(x) {
    x.src = "../static/images/add2.jpg";
}
function out_add(x) {
    x.src = "../static/images/add1.jpg";
}

function change_finish(x) {
    x.src = "../static/images/finish2.jpg";
}
function out_finish(x) {
    x.src = "../static/images/finish1.jpg";
}

const button2 = document.getElementById('button2');
const vocabs = document.getElementById('div1').value;
function showAnswers(){
    for (let i = 0 ; i < vocabs.length ; i++) {
        let result = document.getElementById(vocabs[i]['eng']);
        result.classList.remove('hide');
    }
}