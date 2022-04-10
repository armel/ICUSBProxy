var SerialPort = require('serialport').SerialPort;
var port = "/dev/ttyUSB2";
var commande = "FEFEA4E01515FD";
const path = require('path'); 

var serialPort = new SerialPort(port, {
  baudRate: 9600
});

serialPort.write(Buffer.from(commande, "hex"), function(err) {
  if (err) {
    return console.log("Error on write: ", err.message);
  }
  console.log("Message sent successfully");
});