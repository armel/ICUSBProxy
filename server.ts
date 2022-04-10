var express = require('express');
var app = require('express')();
var http = require('http').Server(app);
var port = process.env.port || 1337
var io = require('socket.io')(http);
var SerialPort = require('serialport').SerialPort;
var serial = new SerialPort('COM1', {
    baudrate: 19200
});

var civCommandTmp: string = "";

app.use(express.static(__dirname + '/public'));

app.get('/', function (req, res) {
    res.sendfile('index.html');
});

http.listen(3000, function () {
    console.log('listen 3000 port');
});

serial.on('open', function () {
    console.log('open');
});

serial.on('data', function (data) {
    //io.emit('recvmsg', data.toString());
    var buff = new Buffer(data, 'utf8'); //no sure about this
    var hexDump = buff.toString('hex')

    civCommandTmp = civCommandTmp + hexDump;
    var fdPosition = civCommandTmp.indexOf('fd');
    if (fdPosition != -1) {
        var civCommand: string = civCommandTmp.substring(0, fdPosition + 2);

        //civCommandTmp = civCommandTmp.substr(fdPosition);
        civCommandTmp = ""; // I know it's bad method.
        console.log(civCommand);
        //WatchArray(SeparateByTwoCharactor(civCommand));
        CivCommandDetect(SeparateByTwoCharactor(civCommand));
        io.emit('rcvmsg', civCommand);
    }
});

io.on('connection', function (socket) {
    socket.on('sendmsg', function (msg) {
        var txBuff = hexStringToByteArray(msg);
        serial.write(txBuff, function (err, results) {
        });
    });

    socket.on('setfreq', function (msg) {
        var freqStr: string = ("000000000" + msg).slice(-10);
        var freqStrArray = new Array();
        freqStrArray = SeparateByTwoCharactor(freqStr);
        freqStrArray.reverse();
        freqStr = freqStrArray.join("");

        freqStr = "fefe58e005" + freqStr + "fd"
        
        if (waitAck == false) {//このコードあまり意味ないみたいだから、とりあえず出す。
            waitAck == true;
        }
        console.log("TX:" + freqStr);
        var txBuff = hexStringToByteArray(freqStr);
        serial.write(txBuff, function (err, results) {
        });

    });
    //modeBtnが押されたときの動作
    socket.on('modeBtn', function (msg) {
        modeNum++;
        if (modeNum == 7) { modeNum = 0 };
        var modeStr: string = '0' + String(modeNum);
        var sendStr = "fefe58e006" + modeStr + "fd"

            if (waitAck == false) {//このコードあまり意味ないみたいだから、とりあえず出す。
            waitAck == true;
        }
        console.log("TX:" + sendStr);
        var txBuff = hexStringToByteArray(sendStr);
        serial.write(txBuff, function (err, results) {
        });

    });

});


/**************************************************************
* 2015/03/03
* バイトの文字列をバイト配列にする。
***************************************************************/
function hexStringToByteArray(str) {
    var len = str.length;
    var buff = new Buffer(len / 2);
    var i:number;
    for (i = 0; i < len; i += 2) {
        buff[i / 2] = parseInt(str.substr(i, 2), 16);
    }
    return buff;

}

/**************************************************************
* 2015/03/03
* 2文字ずつ区切って配列に入れる。
***************************************************************/
function SeparateByTwoCharactor(str: string) {
    var commandArray = new Array();
    var i: number;
    var oneByteStr: string;
    for (i = 0; i < str.length; i += 2) {
        oneByteStr = str.substr(i, 2);
        commandArray.push(oneByteStr);

    }
    return commandArray;
}

/**************************************************************
* 2015/03/03
* バイト配列の中身を確認する。
***************************************************************/
function WatchArray(ary) {
    for (var i = 0; i < ary.length; ++i) {
        console.log(ary[i] + "-");
    }

}

var myAddress: string = "00";
var freqHzStr: string;
var freqHz, freqMhz: number;
var modeArray = ["LSB", "USB", "AM", "CW", "RTTY", "FM", "WFM"];
var minFreq: number = 30000;        //30kHz
var maxFreq: number = 2000000000;   //2GHz
var waitAck: boolean = false;
var modeNum: number = 1;

/**************************************************************
* 2015/03/03
* CIVコマンドを解析して表示。
***************************************************************/
function CivCommandDetect(ary) {

    //if (ary[2] == myAddress) {//自局宛だったら（折り返しコマンドの無視）

        switch (ary[4]) {
            case "00":
            case "05":
            case "03":

                //Frequency
                freqHzStr = ary[9] + ary[8] + ary[7] + ary[6] + ary[5];
                console.log(freqHzStr);

                var freqNum: number;
                freqNum = Number(freqHzStr);
                //各種チェック
                if (ary[10] = 'fd' && isNaN(freqNum) == false && freqNum > minFreq && freqNum < maxFreq) {
                    //こっちもHz単位で送る
                    io.emit('freq', String(Number(freqHzStr)));
                }
                break;

            case "01":
            case "04":
            case "06":
                //band
                modeNum = Number(ary[5]);   //modeNumをglobalにした。
                var modeStr :string = modeArray[modeNum];    
                io.emit('mode', modeStr);
                break;

            case "fb":
                console.log("ack");
                waitAck = false;
                break;
            case "fa":
                console.log("nack");
                waitAck = false;
                break;


            default:
                console.log("unknown command");
                break;
        }
    //}
}