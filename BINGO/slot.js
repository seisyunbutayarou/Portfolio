//<div>要素を取得
div=document.querySelector("div")

//カードのサイズの指定
function size_function(){
    size = document.querySelector('input').value;
    return size;
}

//値格納配列
numbers = [];

//<td>の値を生成
function createnumber(){
    size=size_function();
    //１ ～ (size*size*3)までの乱数を生成
    let randomNumber = Math.floor(Math.random() * (size*size*3)) + 1
    //乱数が配列に存在する場合、再生成
    if(numbers.includes(randomNumber)){
        createnumber();
    }else{
        //生成した乱数を配列に格納
        numbers.push(randomNumber);
        //生成した数を表示
        div.innerHTML += "<br>"+randomNumber;
    }
}
//乱数をリセット
function resetcard(){
    div.innerHTML = "" 
}