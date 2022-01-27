
# GPS data reader

The repository presents the principles of working gps_data_reader python package, intended for route management in road transport companies. 

In project was used a slice of real data from gps device, therefore the sensitive data was changed.
Any similarities to real personal data are coincidental.

## Table of content

* [Repository content](#Repository-content)
* [GPS Data Reader Package](#GPS-Data-Reader-Package)
* [Tech Stack And Requirements](#Tech-Stack-And-Requirements)
* [How to use](#How-to-use)
* [Run with Docker](#Run-with-Docker)

## Repository content

- *gps_data_reader* (python package)
- *1_data_processing.ipynb* (raw data processing)
- *2_create_db_DBManager_class.ipynb*  (creating a database for xyz company with DBManager)
- *3_GpsDataReader_review.ipynb* (functionality presentation)
- *company_xyz.db* (company database)
- *gps_data.pickle* (processed data)
- *gps_raw_data.csv* (raw data)
## GPS Data Reader Package

Python package for organizing and reading GPS data.

The package is intended for collecting, processing and reading signals from GPS devices.

**gps_data_reader** allows to track and manage routes in international road transport of goods and passengers in accordance with *Regulation (EC) No 561/2006* and *Act of 16 April 2004 on working time of drivers (Text No. 879)* and its updates.

#### Main Features
-------------
    - creating and managing SQlite database for transport companies.
    - providing data for calculating drivers working time and delegations.
    - route information (driver, vehicle, trucks mileage, distance travelled).
    - vehicle route map visualization (including start, end and crossing borders points).
    - point-by-point route analysis with crucial information such as: datetime, vehicle position, mileage, speed etc.
    - speed and mileage diagrams allow to detect drivers infringements and manipulations on vehicle.
    
 #### Modules
-------------
    db_manager(DBManager): SQLite database manager.
    gps(GpsDataReader): transportation routes analysis and visualization.
    tests: unit testing samples(unittest framework)

For more information please read package documentation.
## Tech Stack And Requirements

WIN10, Python 3.8.12, SQLite 3.34.0, Jupyter Notebook 6.4.5

*Python Libraries:*
    
    os
    datetime
    collections
    unittest
    parameterized 0.8.1
    sqlite3 '2.6.0'
    numpy '1.20.1'
    pandas '1.3.4'
    folium '0.12.1.post1'
    plotly '5.4.0'



## How to use
In order to run the project:
- download and unpack gps_data_reader folder
- install requirements from section 'Tech Stack And Requirements'
- run with Jupyter Notebook or equivalent.

Caution! Github does not allow the display of maps. For a full review copy the notebook repository link and paste on page http://nbviewer.org/ 

or try below link:

http://nbviewer.org/github/Daniel-Prus/gps_data_reader/blob/main/3_GpsDataReader_review.ipynb


## Run with Docker
Make sure you have installed Docker application on your computer. For more information visit https://docs.docker.com/get-docker/ .

Link to the Docker image https://hub.docker.com/r/danielprus/gps_data_reader .




#### Image specification:

python:3.8-slim

     jupyterlab 3.2.8
     pandas 1.4.0
     numpy 1.22.1
     plotly 5.5.0
     parameterized 0.8.1
     folium 0.12.1.post1


#### Run with terminal:

    1. Docker pull command:

        docker pull danielprus/gps_data_reader

    2. Run container with mapped port :

        docker run --rm -d -t --name=gps -p 8888:8888  danielprus/gps_data_reader

    3. Execute container with bash:

        docker exec -ti gps bash

    4. Run jupter lab in container:

        jupyter lab --ip='0.0.0.0' --port=8888 --no-browser --allow-root

    5. Copy jupyter lab link and paste into your browser, or use localhost:8888.