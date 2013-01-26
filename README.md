bukopie
=======

An internet radio with a web interface


Requirements
============

Bukopie requires the following Python modules to function:

* tornado
* sockjs-tornado
* simplejson


Install these modules using the following command via pip:

    sudo pip install tornado sockjs-tornado simplejson


Running Bukopie
===============

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
