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

## Usage examples
List of pages:
`curl 127.0.0.1:8888/pages`
Add new page:
`curl 127.0.0.1:8888/page -d '{"text":"1v1","title":"p1"}' -H 'Content-Type: application/json'`
Return page current version content:
`curl 127.0.0.1:8888/page/1`
or
`curl 127.0.0.1:8888/page_by_title/p1`
Return page version:
`curl 127.0.0.1:8888/page/1/version/1`
Add new page version:
`curl 127.0.0.1:8888/page/1/version -d '{"text":"1v2","title":"p1"}' -H 'Content-Type: application/json'`
Page versions:
`curl 127.0.0.1:8888/page/1/version`
Page current version number:
`curl 127.0.0.1:8888/page/1/current_version`
Change page current version:
`curl 127.0.0.1:8888/page/1/current_version -d '{"version":2}' -H 'Content-Type: application/json'`

