var SerialPort = require('serialport').SerialPort;

var buffer = new Buffer(11);
buffer[0] = 0xFE;
buffer[1] = 0xFE;
buffer[2] = 0xA4;
buffer[3] = 0xE0;
buffer[4] = 0x00;
buffer[5] = 0x56;
buffer[6] = 0x34;
buffer[7] = 0x12;
buffer[8] = 0x07;
buffer[9] = 0x00;
buffer[10] = 0xFD;

var port = "/dev/ttyUSB2";


var com = new SerialPort({
    path: port,
    baudRate: 9600,
    databits: 7,
    parity: 'yes'
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