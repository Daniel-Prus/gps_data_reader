import sqlite3
import numpy as np
import pandas as pd
from datetime import date
import os
from gps_data_reader.utils.validation import search_values_args_validation

np.set_printoptions(precision=6, suppress=True, edgeitems=10, linewidth=100000,
                    formatter=dict(float=lambda x: f'{x:.2f}'))


class DBManager:
    """Class creates and allows to manage SQLite databases for gps signal data.

    'Attributes'
        ------------
            database (str): name/path of database. If not exists creates new database.

    """

    def __init__(self, database):
        self.database = database
        self.__connect = sqlite3.connect(database, timeout=100)
        self.__connect.isolation_level = None
        self.__cursor = self.__connect.cursor()

    def __del__(self):
        self.__connect.close()

    def __repr__(self):
        return f'Database ({self.database})'

    def info(self):
        """Get specifications of database tables."""
        try:
            newline_indent = '\n   '

            result = self.__cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            table_names = sorted(list(zip(*result))[0])

            print(f"\t{(len(self.database) + 14) * '='}\n",
                  f"\t  Database: {self.database}\n",
                  f"\t{(len(self.database) + 14) * '='}\n")

            print("tables:" + newline_indent + newline_indent.join(table_names))
            print((len(self.database) + 14) * '=')

            for table_name in table_names:
                result = self.__cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall()
                col_names = [description[0] for description in self.__cursor.description]
                table_df = pd.DataFrame(result, columns=col_names)
                table_df = table_df.set_index(table_df.columns[1])
                rows_num = self.__cursor.execute("SELECT COUNT(*) FROM %s" % table_name).fetchone()

                print(("\n%s table (%s rows):" % (table_name, rows_num[0]))
                      + newline_indent)
                print(table_df)
                print(50 * '=')

        except IndexError:
            print(f'Database - {self.database} is empty. ')

    def commit(self):
        self.__cursor.execute("commit")
        self.__cursor.execute("begin")

    def rollback(self):
        self.__cursor.execute("rollback")

    def begin_transaction(self):
        self.__cursor.execute("begin")

    def close(self):
        self.__connect.close()

    def create_table(self, table: str):
        """Creates empty gps table with columns:
            "id", "dt", "vehicle", "driver", "position", "country",
            "speed", "mileage", "ignition_status", "engine_status",
            "longitude", "latitude".

            Parameters
            ----------
                table (str): table name.
        """
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS {}
                            (
                                "id" INTEGER NOT NULL,
                                "dt" TIMESTAMP NOT NULL,
                                "vehicle" TEXT,
                                "driver" TEXT,
                                "position" TEXT,
                                "country" TEXT,
                                "speed" INTEGER,
                                "mileage" REAL,
                                "ignition_status" INTEGER,
                                "engine_status" INTEGER,
                                "longitude" REAL,
                                "latitude" REAL,
                                PRIMARY KEY("id")
                            )'''.format(table))

    def insert_dataframe(self, table, df, if_exists='append'):
        """Insert values as pandas dataframe."""
        df.to_sql(name=table, con=self.__connect, index=False, if_exists=if_exists)

    def insert_values(self, table, values: list):
        self.__cursor.executemany("INSERT INTO {} values (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(table), values)
        print(f'{len(values)} rows added.')

    def search_values(self, table, vehicle='', driver='', between=None):
        """Search values by filter arguments.

        'Parameters'
        ------------
            table (str): table name - 'gps'.
            vehicle (str, optional): registration number of the vehicle.
            driver (str, optional): driver name/surname.
            date_range(list of str, optional): start/end date of route. Format - ["yyyy-mm-dd", "yyyy-mm-dd"].
                                                Default - None.

        'Yields'
        ----------
            generator object
        """
        search_values_args_validation(vehicle, driver, between)

        if bool(between) is False:
            between = ['2000-01-01', date.today().strftime("%Y-%m-%d")]
        if bool(between[0]) is False:
            between[0] = '2000-01-01'
        if bool(between[1]) is False:
            between[1] = date.today().strftime("%Y-%m-%d")

        self.__cursor.execute('''SELECT * FROM {}
                            where "vehicle" LIKE (?)
                            AND "driver" LIKE (?)
                            AND "dt" BETWEEN (?) AND (?)'''.format(table),
                              ("%" + vehicle + "%", "%" + driver + "%", between[0], between[1]))

        items = self.__cursor.fetchall()

        for row in items:
            yield row

    def find_duplicates(self, table):

        self.__cursor.execute('''SELECT *, COUNT(*) from {}
                           group by dt, position, speed, longitude, latitude'''.format(table))

        items = self.__cursor.fetchall()
        col_names = [description[0] for description in self.__cursor.description]
        duplicated = pd.DataFrame(items, columns=col_names)
        duplicated.set_index(duplicated.columns[1])
        duplicated = duplicated[duplicated[duplicated.columns[-1]] > 1].sort_values(duplicated.columns[-1],
                                                                                    ascending=False)

        return duplicated

    def drop_duplicates(self, table):

        duplicated = DBManager.find_duplicates(self, table)

        duplicates_num = sum(duplicated[duplicated.columns[-1]] - 1)

        self.__cursor.execute('''DELETE FROM {}
                            WHERE id NOT IN
                            (SELECT MIN(id) id FROM {}
                            GROUP BY dt, position, speed, longitude, latitude)'''.format(table, table))

        print(f'Duplicates dropped - {duplicates_num} rows.')

    def drop_table(self, table):
        self.__cursor.execute("DROP TABLE IF EXISTS {}".format(table))

    def table_length(self, table):
        self.__cursor.execute("SELECT COUNT(*) FROM {}".format(table))
        length = self.__cursor.fetchone()[0]
        return length

    def total_changes(self):
        print(self.__connect.total_changes)

    def get_column_names(self, table):
        self.__cursor.execute("SELECT * from {}".format(table))
        col_names = [description[0] for description in self.__cursor.description]
        return col_names

    @staticmethod
    def delete_database(database):
        os.remove(database)
        print(f'{str(database)} deleted succesfully.')

    @staticmethod
    def generator_converter(generator):
        """Convert generator to numpy array."""
        numpy = np.array([a for a in generator])
        return numpy
