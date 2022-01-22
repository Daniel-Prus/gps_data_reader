import pandas as pd

# test values without 'id' (two duplicates)
test_values = (('2021-11-11 01:43:00', 'PL55555', 'John Smith', 'Chernobyl 1234', 'UKR', 88.1212, 500533.0, 1, 0,
                11.490252, 52.179932),
               ('2021-11-11 05:50:00', 'PL55555', 'John Smith', 'Chernobyl 1234', 'UKR', 20, 500533.0, 0, 0, 11.490252,
                52.179932),
               ('2021-08-05 12:50:00', 'GB06666', 'Jan Kowalski', 'Warszawa, Mokotów 1234', 'PL', 50, 121121.0, 1, 1,
                5.881000, 12.124566),
               ('2021-08-05 12:50:00', 'GB06666', 'Jan Kowalski', 'Warszawa, Mokotów 1234', 'PL', 50, 121121.0, 1, 1,
                5.881000, 12.124566),
               ('2020-09-05 19:23:00', 'BI122', 'Elon Musk', 'Gdańsk 8', 'PL', 0, 521121.0, 1, 1, 7.450903, 52.306171))

# expected values with added unique id by sqlite
expected_values = [(1, '2021-11-11 01:43:00', 'PL55555', 'John Smith', 'Chernobyl 1234', 'UKR', 88.1212, 500533.0, 1, 0,
                    11.490252, 52.179932),
                   (2, '2021-11-11 05:50:00', 'PL55555', 'John Smith', 'Chernobyl 1234', 'UKR', 20, 500533.0, 0, 0,
                    11.490252, 52.179932),
                   (3, '2021-08-05 12:50:00', 'GB06666', 'Jan Kowalski', 'Warszawa, Mokotów 1234', 'PL', 50,
                    121121.0, 1, 1, 5.881000, 12.124566),
                   (4, '2021-08-05 12:50:00', 'GB06666', 'Jan Kowalski', 'Warszawa, Mokotów 1234', 'PL', 50,
                    121121.0, 1, 1, 5.881000, 12.124566),
                   (5, '2020-09-05 19:23:00', 'BI122', 'Elon Musk', 'Gdańsk 8', 'PL', 0, 521121.0, 1, 1, 7.450903,
                    52.306171)]

# 'gps' table columns names (without id)
test_column_names = ['dt', 'vehicle', 'driver', 'position', 'country', 'speed', 'mileage', 'ignition_status',
                     'engine_status', 'longitude', 'latitude']

expected_column_names = ['id', 'dt', 'vehicle', 'driver', 'position', 'country', 'speed', 'mileage', 'ignition_status',
                         'engine_status', 'longitude', 'latitude']

# test pandas dataframes
test_values_df = pd.DataFrame(test_values, columns=test_column_names)
excepted_values_df = pd.DataFrame(expected_values, columns=expected_column_names)
