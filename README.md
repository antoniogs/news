News
====

This is an exercise about how to read news from News API (https://newsapi.org/), store and show using python3 and Django.

Requirements
============
* Python3 (not tested in python2).

Installation
============

* Download the project code.
* Install the required libraries.
    Included in the requirements.txt file (pip install -r requirements.txt)
* Configure your Django server (see https://docs.djangoproject.com/en/1.11/howto/deployment/ for help),
    or run locally (using python manage.py runserver).
* Configure the database.
    By default, this project uses an SQLite database, but if you are going to use another database system,
    modify the database section of the settings.py file with your database data.
* Populate the database with the required tables, executing the next command in the same folder than the manage.py file:
    python manage.py migrate

Configuration
=============
* Add your News API key to settings.py, as the NEWSAPI_KEY value.


Usage
=====
* /articles
    Get a list of articles from News API.
    The first time, the app look for articles between the current time and one hour before.
    Return, in JSON format, if the app connected to News API and how many new articles were loaded.
* /json_articles
    Get, in JSON format, the 100 most recent articles.
* /newslist
    Show a html view containing the 20 most recent articles.