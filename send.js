var SerialPort = require('serialport').SerialPort;

var buffer = new Buffer(7);
buffer[0] = 0xFE;
buffer[1] = 0xFE;
buffer[2] = 0xA4;
buffer[3] = 0xE0;
buffer[4] = 0x15;
buffer[5] = 0x15;
buffer[6] = 0xFD;

var port = "/dev/ttyUSB2";


var com = new SerialPort({
    path: port,
    baudRate: 115200,
    databits: 8,
    parity: 'none'
}, false);

com.open(function (error) {
    if (error) {
        console.log('Error while opening the port ' + error);
    } else {
        console.log('CST port open');
        com.write(buffer, function (err, result) {
            if (err) {
                console.log('Error while sending message : ' + err);
            }
            if (result) {
                console.log('Response received after sending message : ' + result);
            }    
        });
    }              
});