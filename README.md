# StundenzettelCreator

[![Build Status](https://travis-ci.org/DerGut/StundenzettelCreator.svg?branch=master)](https://travis-ci.org/DerGut/StundenzettelCreator) [![codecov](https://codecov.io/gh/DerGut/StundenzettelCreator/branch/master/graph/badge.svg)](https://codecov.io/gh/DerGut/StundenzettelCreator)

A web interface for the [timesheet generator](https://github.com/pfaion/timesheet_generator) by Patrick Faion.

Visit [the web site](http://www.stundenzettel-creator.xyz) to have your Stundenzettel be automatically created.

## Installation
In order to install StundenzettelCreator locally simply follow the steps below.
- Clone the repository
- run `pip install -r requirements.txt` to install all the project dependencies
- run `python manage.py collectstatic` in order to get static files like *.css, *.js served by django
- and finally, run `python manage.py runserver` to get started
