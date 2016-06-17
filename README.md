# wiki_test

Setup:
    -run the following commands in psql shell:
        create role wiki login password '123';
        create database wiki owner wiki;
        create database wiki_test owner wiki;

Running tests:
    -from project directory run:
        python3 -m unittest discover

Running application:
    -from project directory run:
        python3 server.py
    The service listens port 8888
