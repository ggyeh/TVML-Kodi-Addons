# TVML Kodi Addons
Working TVML server written in python(flask) and javascript serving original KODI addons!!
I've created a bridge from the kodi plugins to the server using the excellent [Kodi stubs](https://github.com/romanvm/Kodistubs)

##Screenshots
![alt tag](https://raw.githubusercontent.com/ggyeh/TVML-Kodi-Addons/master/images/screenshot1.png)
![alt tag](https://raw.githubusercontent.com/ggyeh/TVML-Kodi-Addons/master/images/screenshot2.png)
![alt tag](https://raw.githubusercontent.com/ggyeh/TVML-Kodi-Addons/master/images/screenshot3.png)
![alt tag](https://raw.githubusercontent.com/ggyeh/TVML-Kodi-Addons/master/images/screenshot4.png)
![alt tag](https://raw.githubusercontent.com/ggyeh/TVML-Kodi-Addons/master/images/screenshot5.png)

##How to use
1. You can use the pre-compiled executable (for windows 64bit, mac and linux)
2. This will run the server on port 5000. (You can run with -p switch to select different port)
3. Fire up a TVML client on the apple TV like: TVML Explorer (available in TVOS appstore)
4. Add your IP of the server
5. Have fun

##Kodi addons
Still not all of Kodi API is implemented so some might fail.

Most addons should work immediately (Simply add them via the interface)

###How it works
The main page of the app shows a grid view of all addons available.

You can install new addons from the 'Settings -> Addons' tab.

Once you select an addon, the server runs it with an empty string and returs the list back to the client.

Subsequent calls will run the plugin with the list item url


##What's working and what's not
The server is based on python flask and is relatively small scale.

The idea is to install the server (on your network) and access it locally (i.e. one user)

To create a large scale server serving multiple clients will probably require some work

Currently working are most dialogs, simple actions like addDirectory and setResolvedURL

executeBuiltin commands

Addon settings can be accessed by long press on the addon icon in the main view

Addon settings are saved locally (on client) so will persist even if server restarts

Addon data path (for saving local files) is currently on server so all clients will use the same files (might be a problem).

##What's next
A lot more work to be done:
- Implement more of kodi stubs to fit more addons
- Modify the server to be able to accept many multiple connections. Think about the possibility to have multiple central servers on the web so everyone can connect to them without having to install anything locally!!
- If your interested in coding (python/javascript), I'd love the help

##Building from source
To build from source, you need python 2.7, and the following python modules:
- flask
- gevent
- pyinstaller
- AdvancedHTMLParser
- requests
- psutil
- packaging
- httplib2


To run from source, simply run the app.py file located at the root dir of this repo.

To build an executable issue `pyinstaller app.spec` from an appropriate OS (i.e. running on windows will build windows EXE, etc.)

## License

Licensed under Apache License v2.0.
<br>
Copyright 2016
