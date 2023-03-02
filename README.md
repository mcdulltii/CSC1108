# CSC1108 Project

## Requirements (Python3)

- googlemaps
- Flask
- flask_cors
- python-dotenv

## Setup

> Install python3 dependencies

```shell
> pip3 install -r requirements.txt
```

> Add .env file

```shell
> echo 'API_KEY=<GMAP_API_KEY>' > .env
```

## Setup (Docker)

> Run `run.sh` to build Dockerfile and run docker image

```shell
> ./run.sh
```

> Alternatively, build the Dockerfile and run the docker image as below

```shell
> docker build -t route_planner .
> docker run -p 80:80 -it --rm --name route_planner route_planner
```

## Usage

```shell
❯ python3 app.py -h
usage: app.py [-h] [-f FILE] [-i HOST] [-p PORT]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Bus routes information
  -i HOST, --host HOST  Hostname
  -p PORT, --port PORT  Port number
```

```shell
> python3 app.py -f ./routes_scraper/routes.txt -i 0.0.0.0 -p 80
```
