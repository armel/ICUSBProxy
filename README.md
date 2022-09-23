# ICUSBProxy
![licence](https://img.shields.io/github/license/armel/ICUSBProxy)
![language](https://img.shields.io/github/languages/top/armel/ICUSBProxy)
![size](https://img.shields.io/github/repo-size/armel/ICUSBProxy)
![version](https://img.shields.io/github/v/release/armel/ICUSBProxy)
![activity](https://img.shields.io/github/commit-activity/y/armel/ICUSBProxy)

The Icom IC-7300 or IC-9700 transceivers do not have Bluetooth or WiFi support.

This project allows to set up an HTTP _proxy_ allowing to talk wirelessly, from an M5Stack (or other equipment), with an Icom transceiver like IC-7300 or IC-9700 and sending CI-V commands.

> I don't own the IC-9700, so I haven't tested it. But it seems to work well.

This project was made to work with my [ICMultiMeter](https://github.com/armel/ICMultiMeter) and [ICSMeter](https://github.com/armel/ICSMeter) on M5Stack.

# Technical architecture

ICUSBProxy only need Python3.

## Connexion

__M5Stack__ <--- (_WiFi Connection_) ---> __PC with ICUSBProxy__ <--- (_USB Connection_) ---> __Icom Transceiver__.

As a PC, I'm using a simple Raspberry Pi under Raspbian. But it could work with another PC and another operating system. 

## GET Request data format

`civ = {CI-V bytes field command},{baud},{tty}` 

Examples,

```
civ = fe,fe,a4,e0,00,56,34,12,07,00,fd,115200,/dev/ttyUSB0
civ = fe,fe,a4,e0,03,fd,115200,/dev/ttyACM0
```

# Installation

Check that you have Python3 on your PC. If not, install it.

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

Icom and the Icom logo are registered trademarks of Icom Incorporated (Japan) in Japan, the United States, the United Kingdom, Germany, France, Spain, Russia, Australia, New Zealand, and/or other countries.

# Donations

Special thanks to Rolf Schroeder DL8BAG, Brian Garber WB8AM, Matt B-Wilkinson M6VWM, Robert Agnew KD0TVP, Meinhard Frank Günther DL0CN, Johan Hansson SM0TSC, Tadeusz Pater VA7CPM, Frederic Ulmer F4ESO, Joshua Murray M0JMO, Mark Hammond N8MH, Angel Mateu Muzzio EA4GIG, Hiroshi Sasaki JL7KGW, Robert John Williams VK3IE, Mark Bumstead M0IAX, Félix Symann F1VEO, Patrick Ruhl DG2YRP, Michael Beck DH5DAX, Philippe Nicolas F4IQP, Timothy Nustad KD9KHZ, Martin Blanz DL9SAD, Edmund Thompson AE4TQ, Gregory Kiyoi KN6RUQ, Patrick Samson F6GWE and George Kokolakis SV3QUP for their donations. That’s so kind of them. Thanks so much 🙏🏻

If you find this project fun and useful then [offer me a beer](https://www.paypal.me/F4HWN) :) 

By the way, you can follow me on [Twitter](https://twitter.com/F4HWN) and post pictures of your installation with your M5Stack. It always makes me happy ;) 
