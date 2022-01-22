# package level doc-string
__doc__ = """
gps_data_reader - Python package for organizing and reading GPS data.
===============================================================================

The package is intended for collecting, processing and reading signals from GPS devices.

**gps_data_reader** allows to track and manage routes in international road transport of goods and passengers.

Main Features
-------------
    - creating and managing SQlite database.
    - providing data for calculating drivers working time and delegations.
    - route information (driver, vehicle, trucks mileage, distance travelled).
    - vehicle route map visualization (including start, end and crossing borders points)
    - speed and mileage diagrams allow to detect drivers infringements and manipulations on vehicle.
    
 Modules
-------------
    db_manager(DBManager): SQLite database manager.
    gps(GpsDataReader): transportation routes analysis and visualization.

Created by Daniel Pruszyński
"""