Bukopie
=======

An internet radio with a web interface, using MPlayer as the media backend.
It uses [Python](http://www.python.org/) and [Tornado](http://www.tornadoweb.org/)
to run as a local web service on your computer. (Python 3 not yet tested)


Requirements
============

Bukopie requires the following modules and programs to function:

* tornado
* sockjs-tornado
* simplejson
* mplayer


Installation
============

* Install these Python modules using the following command via [pip](http://pypi.python.org/pypi/pip):

    `sudo pip install tornado sockjs-tornado simplejson`

* Install MPlayer if you don't have it installed:

    * Mac OS X (via MacPorts)
       * `sudo port install mplayer`
    * Debian
       * `sudo apt-get install mplayer`
    * Win32
       * Download the latest MPlayer binary from [this link](http://code.google.com/p/mplayer-for-windows/downloads/list)
       * Place the binaries inside the Bukopie/app directory


Running Bukopie
===============

Bukopie runs as a web service on port 8081 by default. You may run it from the command line or as a daemon.


As stand-alone
--------------

Run `run.sh` or the following command: 

    python app/main.py
  
As daemon mode (For Debian-based systems)
-----------------------------------------

* Open `initd.sh` using a text-editor
* Edit the `DAEMON_PATH` variable and point it to the Bukopie directory
* Copy `initd.sh` file to your initd directory:
  * `sudo cp initd.sh /etc/init.d/bukopie`
  * `chmod +x /etc/init.d/bukopie`
* Run bukopie as a service:
  * `sudo service bukopie start`
* Open the following URL from your web browser:
  * `http://localhost:8081`
* Enjoy!
