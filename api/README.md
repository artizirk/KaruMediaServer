# API Karu Media

This is a api writen in python for Karu Media storage server

# How to set it up?
First you need Python 3.4 or newer and latest uwsgi installed in your system

For Debian you have to install those pacakges

    sudo apt-get install python3 python3-pip python3-venv uwsgi uwsgi-plugin-python3 python3-uwsgidecorators

And then you can just run those commands

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

And you can run it like so

    uwsgi --ini uwsgi.ini:dev
