# wiki_test

## Setup

Run the following commands in *psql* shell:

`create role wiki login password '123';`
`create database wiki owner wiki;`
`create database wiki_test owner wiki;`


## Running tests
From project directory run:
`python3 -m unittest discover`

## Running application
From project directory run:
`python3 server.py`
The service listens port 8888

