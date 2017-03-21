# rpi-auxdisplay
A server-client application to use RPi with a screen as a auxiliary display

### Server
GUI which runs on Auxiliary Display (Raspberry Pi).

issue `python3.4 server/server.py` command from shell to run client

### Client
Application which runs on main machine (laptop, desktop, anything other than your auxiliary display) and pushes data to server on auxiliary display.

issue `python3.4 client/client.py` command from shell to run client

## Requirements
Python 3.4 or newer should be ebough to run both server and client with the dependecies given below. (Python3.4 is preinstalled on raspbian as of the date of 2017-02-19)

### Dependencies
* python3.4
* netifaces: https://pypi.python.org/pypi/netifaces
* zeroconf: https://pypi.python.org/pypi/zeroconf
* feedparser: https://pypi.python.org/pypi/feedparser

### References
* E-Mail Icon from https://commons.wikimedia.org/wiki/File:Email_Shiny_Icon.svg

## Trivia
* Developement envrionement is Asus K53SV Laptop with `Linux archlinux-k53sv 4.10.4-1-ARCH #1 SMP PREEMPT Sat Mar 18 19:39:18 CET 2017 x86_64 GNU/Linux` and a Raspberry Pi 3 Type B with official 7" touchscreen and `Linux raspberrypi 4.4.38-v7+ #938 SMP Thu Dec 15 15:22:21 GMT 2016 armv7l GNU/Linux`
