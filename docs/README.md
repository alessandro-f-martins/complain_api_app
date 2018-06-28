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

   - `src/app_vars.cfg`:
     ```bash
     line 1: # . ../../venv/bin/activate --> change it to point to the 'activate' script of your virtual environment 
     ```
   - `src/runApp.sh`:
     ```bash
     line 2: export APP_DIR=/usr/src/app --> change it to point to your app_dir
     ```
   - `src/http/nginx.conf`:
     ```bash
     line 2: pid /usr/src/app/http/nginx.pid; --> change it to point to your app_dir
     line 41: access_log /usr/src/app/http/access.log; --> change it to point to your app_dir
     line 42: error_log  /usr/src/app/http/error.log --> change it to point to your app_dir
     ```
   - `src/db/init/mongod.conf`:
     ```bash
     line 3:    path: "/usr/src/app/db/log/mongod.log" --> change it to point to your app_dir
     line 9:    dbPath: "/usr/src/app/db/data" --> change it to point to your app_dir
     ```

5. Go to the `src/` directory and run the application with `sudo`:
   ```bash
   $ cd src
   $ sudo ./runApp.sh
   ```
6. To deactivate the application, run `closeApp.sh` with `sudo`:
   ```bash
   $ sudo ./closeApp.sh
   ```

### Testing

There are some examples of testing data in the `app_dir/tests`directory. They can be run using the `testscript.sh` curl-based Bash script:  
```bash
$ ./testscript.sh
```
During development, [Postman][postman_link] was used for ease of operation. Please feel free to analyze the `tests/entrynn.txt` test data files to produce test data of your own.



## About the application  

### The API Routing and Data Engine

The Complaint API application is based upon *Flask* and *Flask-RESTful* frameworks to provide all the underpinnings of request routing, HTTP method association, argument parsing and REST object manipulation. For more details, please refer to [Flask-RESTful website][flask-restful_link].

[Flask-PyMongo][flask-pymongo_link] was also used for providing connectivity to the MongoDB database.

### The *complain* module

asdasdasd

### REST functionalities

asdasdsadasd

### Working with Geolocation and Distance Range queries

sadasdsad

### Querying with the GET method

asdasdasdsad

### Dockerized version

asdasdasdasdasd



## Under work

There are still some functionalities we wish to improve further:

- Decouple the main routing and HTTP servicing engine from the database engine in two separate, more loosely coupled microservices. This can improve overall system scalability. 




[docker_link]:http://hub.docker.com/afmartins/xxx
[github_link]:https://github.com/alessandro-f-martins/complaint_api_app
[postman_link]:https://www.getpostman.com/apps
[flask-restful_link]:https://flask-restful.readthedocs.io/en/latest/
[flask-pymongo_link]:http://flask-pymongo.readthedocs.io/en/latest/