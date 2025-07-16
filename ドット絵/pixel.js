//ドット絵生成関数
function create(){
    //<canvas>を空にする
    reset();
    //<img>ノードの生成
    image = document.createElement("img");
    //入力されたファイルリストを取得
    input = document.querySelector("input[type='file']");
    //最初に選択されたファイルを取得
    file = input.files[0];
    //FileReader(ファイル読み取りツール)をインスタンス化
    reader = new FileReader();
    //ファイル内容の読み込み
    reader.readAsDataURL(file);
    //読み込み完了後、<img>のsrcに文字列化されたバイナリデータを指定
    reader.onload = function(e) {
        image.src = e.target.result;
    };
    //画像の読み込みが完了したらcanvasに描画
    image.onload = function() {
        canvas = document.querySelector("canvas");
        ctx = canvas.getContext("2d");

        //キャンバスサイズを画像サイズに合わせる
        canvas.width = image.width;
        canvas.height = image.height;

        //canvasに描画
        ctx.drawImage(image, 0, 0);

        //画像情報の取得（offsetX, offsetY, 幅、高さ）
        imageData = ctx.getImageData(0, 0, canvas.clientWidth, canvas.clientHeight);
  
        //imageData.dataに1pxごとのRGBAが含まれる
        data = imageData.data;

        //変換処理
        size = document.getElementById("number").value
        convert(parseInt(size));

        //画像情報からCanvasに書き戻す
        ctx.putImageData(imageData, 0, 0);
    };
}



//<canvas>リセット関数
function reset() {
    //<canvas>ノードの取得
    canvas=document.querySelector("canvas");
    //幅を設定し、<canvas>をリセット
    canvas.width=canvas.width;
}



//ドット絵変換関数
function convert(blockSize) {
    for (let y = 0; y < canvas.height; y += blockSize) {
        for (let x = 0; x < canvas.width; x += blockSize) {

            let rSum = 0, gSum = 0, bSum = 0, count = 0;

            // ブロック内の平均色を計算
            for (let dy = 0; dy < blockSize; dy++) {
                for (let dx = 0; dx < blockSize; dx++) {
                    let ny = y + dy;
                    let nx = x + dx;

                    if (ny < canvas.height && nx < canvas.width) {
                        let index = (ny * canvas.width + nx) * 4;
                        rSum += data[index];
                        gSum += data[index + 1];
                        bSum += data[index + 2];
                        count++;
                    }
                }
            }

            let rAvg = rSum / count;
            let gAvg = gSum / count;
            let bAvg = bSum / count;

            // ブロック内を平均色で塗りつぶす
            for (let dy = 0; dy < blockSize; dy++) {
                for (let dx = 0; dx < blockSize; dx++) {
                    let ny = y + dy;
                    let nx = x + dx;

                    if (ny < canvas.height && nx < canvas.width) {
                        let index = (ny * canvas.width + nx) * 4;
                        data[index] = rAvg;
                        data[index + 1] = gAvg;
                        data[index + 2] = bAvg;
                    }
                }
            }
        }
    }
}

