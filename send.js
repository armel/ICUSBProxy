var SerialPort = require("serialport");
var port = "/dev/USB2";
var commande = {0xFE, 0xFE, 0xA4, 0xE0, 0x15, 0x15, 0xFD};

var serialPort = new SerialPort(port, {
  baudRate: 9600
});

serialPort.write(hex(commande), function(err) {
  if (err) {
    return console.log("Error on write: ", err.message);
  }
  console.log("Message sent successfully");
});

function hex(str) {
  var arr = [];
  for (var i = 0, l = str.length; i < l; i ++) {
          var ascii = str.charCodeAt(i);
          arr.push(ascii);
  }
  return new Buffer(arr);
}