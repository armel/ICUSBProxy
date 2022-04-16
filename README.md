# ICUSBProxy
![licence](https://img.shields.io/github/license/armel/ICUSBProxy)
![language](https://img.shields.io/github/languages/top/armel/ICUSBProxy)
![size](https://img.shields.io/github/repo-size/armel/ICUSBProxy)
![version](https://img.shields.io/github/v/release/armel/ICUSBProxy)
![activity](https://img.shields.io/github/commit-activity/y/armel/ICUSBProxy)

The Icom IC7300 or IC9700 transceivers do not have Bluetooth or WiFi support.

This project allows to set up an HTTP _proxy_ allowing to talk wirelessly, from an M5Stack (or other equipment), with an Icom transceiver like IC7300 or IC9700 and sending CI-V commands.

> I don't own the 9700, so I haven't tested it.

This project was made to work with my ICMultiMeter on M5Stack.

# Technical architecture

__M5Stack__ <--- (_WiFi Connection_) ---> __PC with ICUSBProxy__ <--- (_USB Connection_) ---> __Icom Transceiver__.

As a PC, I'm using a simple Raspberry Pi under Raspbian. But it could work with another PC and another operating system. 

You only need Python3.

# Installation

Check that you have Python3 on your PC and if not install it.

Then, still on your PC or Mac, clone the ICUSBProxy project via the command :

`git clone https://github.com/armel/ICUSBProxy.git`

You can also download a [zip archive](https://github.com/armel/ICUSBProxy/releases) of the project, if you prefer, and unzip it.

# Usage

Plug your Transceiver via the USB cable (USB type A to USB type B) to your PC. It's time to start the Python3 script :

`./ICUSBProxy.py`

By default, the HTTP port is 1234, but you can change it. For example, if you want to change it for 2345 :

`./ICUSBProxy.py 2345`

And if you want to run this process even after logging out from the shell/terminal, here is the command (under Linux) :

`nohup ./ICUSBProxy.py 2345 &`

# Credits
 
Many thanks to [mdonkers](https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7).


# Donations

Special thanks to Matt B-Wilkinson, Rolf Schroeder, Brian Garber, Robert Agnew and Meinhard Frank Günther for their donations. That’s so kind of them. Thanks so much 🙏🏻

If you find this project fun and useful then [offer me a beer](https://www.paypal.me/F4HWN) :) 

By the way, you can follow me on [Twitter](https://twitter.com/F4HWN) and post pictures of your installation with your M5Stack. It always makes me happy ;) 