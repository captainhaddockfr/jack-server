# Jack 

Jack is Spotify queue collaborate project. The goal is to allow a user to give access, in a secure way to his Spotify queue.

## Installation 

### Prerequisites 
* Docker and Docker-compose

### Quickstart 
* Create a `.env.dev` file with : 
```
DEBUG=1
SECRET_KEY=foo
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=hello_django_dev
SQL_USER=hello_django
SQL_PASSWORD=hello_django
SQL_HOST=db
SQL_PORT=5432
```
* Run container : 
```
docker-compose up -d 
```
* Open browser on [http://localhost:8000](http://localhost:8000)

## How it works 
### Get Spotify Access Token :
* Download [https://github.com/spotify/web-api-auth-examples](Spotify test projet)
* Install dependencies `npm i`
* In `authorization_code` subfolder, run project : `node app.js`
* Open browser on [http://localhost:8888](http://localhost:8888) and connect with your Spotify Account
* Find your Access Token
