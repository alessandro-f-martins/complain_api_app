# Complaint API Application

Author: Alessandro F. Martins

Version: 0.1b 

## Introduction

This is an application for submission to Reclame Aqui, which consists on a simple Restful API application to manage complaints, which includes:

- Full CRUD capabilities: create, read, update and delete complaints
- Three search modes for the GET method: exact match, "*like*" match (using parts of the desired attribute value, case insensitive) and distance range search
- Exact and "*like*" searches can be combined 
- Google Maps- and MongoDB native-based geolocation capabilities
- JSON-based document format, MongoDB-based persistence
- Dockerfile for building containerized application. A link to an example container can be found [here][docker_link]



## Installation

### Prerequisites:

The following software was used in the elaboration of this application: 

- Python 3.6 (the application was built and tested with Python 3.6.5)
- pip 10.0.1
- virtualenv 16.0.0
- MongoDB 3.4.1
- Nginx 1.14.0

### Installation steps:

1. Clone this repository to a working directory (let's say, _app_dir_):  

  ```bash
  $ mkdir app_dir
  $ cd app_dir
  $ git clone https://github.com/alessandro-f-martins/complaint_api_app .
  ```

2. Create a Python virtual environment for this project (please refer to any related tutorials on the Internet. There is a number of ways to organize virtual environments, which depend on system organization, please feel free to choose the one which is best for you).

3. Install the needed Python packages using the provided `requirements.txt`:

   ```bash
   $ pip install -r requirements.txt
   ```

4. Modify the following configuration files. They contain references to the docker internal directory structure (`/usr/src/app` for the main application directory), and should be changed for running in your environment:

   - `app_vars.cfg`:
     ```bash
     line 1: # . ../../venv/bin/activate # --> change it to point to the 'activate' script of your virtual environment 
     ```
   - `runApp.sh`:
     ```bash
     line 2: export APP_DIR=/usr/src/app # --> change it to point to your app_dir
     ```
   - `http/nginx.conf`:
     ```bash
     line 2: pid /usr/src/app/http/nginx.pid; # --> change it to point to your app_dir
     line 41: access_log /usr/src/app/http/access.log; # --> change it to point to your app_dir
     line 42: error_log  /usr/src/app/http/error.log # --> change it to point to your app_dir
     ```
   - `db/init/mongod.conf`:
     ```bash
     line 3:    path: "/usr/src/app/db/log/mongod.log" # --> change it to point to your app_dir
     line 9:    dbPath: "/usr/src/app/db/data" # --> change it to point to your app_dir
     ```

5. Go to the *api_dir* directory and run the application with `sudo`:
   ```bash
   $ cd app_dir
   $ sudo ./runApp.sh &
   ```
   Once running, the server listens on HTTP port 80.

6. To deactivate the application, run `closeApp.sh` with `sudo`:
   ```bash
   $ sudo ./closeApp.sh
   ```

### Testing

There are some examples of testing data in the `app_dir/tests` directory. They can be run using the `testscript.sh` curl-based Bash script:  
```bash
$ ./testscript.sh
```
During development, [Postman][postman_link] was used for ease of operation. Please feel free to analyze the `tests/entrynn.txt` test data files to produce test data of your own.



## About the application  

### The API Routing and Data Engine

The Complaint API application is based upon *Flask* and *Flask-RESTful* frameworks to provide all the underpinnings of request routing, HTTP method association, argument parsing and REST object manipulation. For more details, please refer to [Flask-RESTful website][flask-restful_link].

[Flask-PyMongo][flask-pymongo_link] was also used for providing connectivity to the MongoDB database.

### The *Complaint* Document format

The *complaint* JSON document has the following format:
```json
{
    "complain_id" : <int>,
	"title" : <string>,
	"description" : <string>,
    "locale" : {
		"address" : <string>,
		"complement" : <string>,
		"vicinity" : <string>,
		"zip" : <string>,
		"city" : <string>,
		"state" : <string>,
		"country" : <string>,
		"geo_location" : {
			"type" : "Point",
			"coordinates" : [
				<float>,
				<float>
			]
		}
	},
	"company" : <string>,
}
```
Two things to mention about the `locale.geo_location` attribute:
- Its type is *GeoJSON*, a format used for encoding a variety of geographic data structures. For more information, please refer to [GeoJSON.org][geojson_link].
- The document shown above is how it is stored in the MongoDB database. It is omitted in any REST operations, as they are produced and stored for geolocation purposes only (see *Working with Geolocation and Distance Range queries*).

### The *complain* module and REST functionalities

The *complain* module, under the *resources* package, contains the definitions of the `Complain` and `ComplainList` classes. The first one contains methods for handling URIs which are related to a single complaint object, and therefore have the *id* of this object as its last part:
   ```bash
   $ curl http://myserver/complain/5   # HTTP GET: Retrieves complaint object whose id is 5

   $ curl -X DELETE http://myserver/complain/9   # HTTP DELETE: Removes complaint object whose id is 9

   $ curl -d 'complain={"company":"Umbrella%20Corp."}' -X PATCH \ http://localhost/complain/5 # HTTP PATCH: Modifies the company attribute of complaint object whose id is 5

   $ curl -d "@new_entry.txt" -X PUT http://localhost/complain/3  # HTTP PUT: Replaces the whole content of complaint object whose id is 3 by the complain document contained in file "new_entry.txt" (see below)
   ```
The second class (`ComplainList`) contains methods for handling URIs which don't relate to a specific object, either potentially bringing a complete list of complaint documents in the database, a list that match a query string, or creating a new object with a system-assigned *id*:

   ```bash
   $ curl -d "@new_entry.txt" -X POST http://localhost/complain  # HTTP POST: Replaces the whole content the company attribute of complaint object whose id is 3 by the complain document contained in file "new_entry.txt" (see below)

   $ curl http://localhost/complain?title=Complain%201 # HTTP GET: Retrieving complaints whose 'title' attribute matches "Complain 1" exactly (whole text, case sensitive)

   $ curl http://localhost/complain?city_like=Paulo # HTTP GET: Retrieves complaints made in a city which contains "Paulo" in its name (case insensitive)
   ```
For reference, here is a content for a *new_entry.txt* file, as used by the *PUT* and *POST* examples above:

   ```json
   complain={
     "title" : "Complaint 4",
     "description" : "I am the fourth complaint",
     "locale" : {
       "address": "Av. Paulista, 1500",
       "complement": "3rd floor, room 345",
       "vicinity": "Bela Vista",
       "zip": "01310-100",
       "city": "São Paulo",
       "state": "SP",
       "country": "Brazil"
     },
     "company" : "Damage Inc."
   }
   ```



Of course, these are `curl`-based examples of usage, and the user should call the API methods according to the REST conventions of the client language or application.

### Querying with the GET method

asdasdasdsad

### Working with Geolocation and Distance Range queries

sadasdsad



### Dockerized version



```bash
$ docker run -p80:80 afmartins/complain_api_app
```



## Under work

There are still some functionalities we wish to improve further:

- Include attributes such *created_at: <timestamp>* and *complainer_name: <string>*
- Currently, the dockerized application provided as example keeps everything inside its own container, including its database files, as it is meant for testing. In a production environment, Docker Volumes should be used, so data may be persisted and multiple containerized instances of the application may persist and have access to the data.



----



[geojson_link]:http://geojson.org/
[docker_link]:http://hub.docker.com/afmartins/xxx
[github_link]:https://github.com/alessandro-f-martins/complaint_api_app
[postman_link]:https://www.getpostman.com/apps
[flask-restful_link]:https://flask-restful.readthedocs.io/en/latest/
[flask-pymongo_link]:http://flask-pymongo.readthedocs.io/en/latest/

[flas]: 