var SerialPort = require("serialport");
var port = "/dev/USB2";
var commande = "FEFEA4E01515FD";

var serialPort = new SerialPort(port, {
  baudRate: 9600
});

serialPort.write(Buffer.from(commande, "hex"), function(err) {
  if (err) {
    return console.log("Error on write: ", err.message);
  }
  console.log("Message sent successfully");
});