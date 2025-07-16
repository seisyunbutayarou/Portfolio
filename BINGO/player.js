//カードのサイズの指定
function size_function(){
    size = document.querySelector('input').value;
    return size;
}

//BINGOカード
const card=document.getElementById('card');

//カードの生成
function createcard(){
    //値格納配列
    numbers = [];
    size=size_function();
    //カードのリセット
    resetcard();
    for(i=0;i<size;i++){
        //<tr>の生成
        row=document.createElement("tr")
        for(j=0;j<size;j++){
            //<td>の生成
            col=document.createElement("td")
            //<td>に値を設定
            col.textContent=createnumber()
            //カードの真ん中をBINGOにする
            if (i === Math.floor(size / 2) && j === Math.floor(size / 2)) {
                col.textContent = "●";
            }
            //<tr>に<td>を追加
            row.append(col)
        }
        //<table>に<tr>を追加
        card.append(row)
    }
    document.querySelectorAll('td').forEach(td => {
    td.addEventListener('click', change_color);
    });
    
}
//カードのリセット
function resetcard(){
    card.innerHTML = "" 
}


//<td>の値を生成
function createnumber(){
    size=size_function();
    //１ ～ (size*size*3)までの乱数を生成
    let randomNumber = Math.floor(Math.random() * (size*size*3)) + 1
    //乱数が配列に存在する場合、再生成
    if(numbers.includes(randomNumber)){
        return createnumber();
    }else{
        //生成した乱数を配列に格納
        numbers.push(randomNumber);
    }
    return randomNumber
}

function change_color(ev) {
    if(ev.target.style.background === 'black'){
        ev.target.style.background = '';
    }else{
        ev.target.style.background = 'black';
    }
}

