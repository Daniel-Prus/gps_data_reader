import unittest
import sqlite3
from parameterized import parameterized
from gps_data_reader.db_manager import DBManager
from test_data import *


class TestDBManager(unittest.TestCase):

    def setUp(self):
        # external connection
        connection = sqlite3.connect("test_company_db")
        cursor = connection.cursor()
        self.connection = connection

        # DBManager instance
        self.db = DBManager("test_company_db")
        self.db.create_table('gps')

    def tearDown(self):
        self.connection.close()
        self.db.drop_table('gps')
        self.db.close()

    def test_a_create_table(self):
        # arrange
        self.db.drop_table('gps')
        self.db.create_table('gps')
        cursor = self.connection.cursor()

        # act
        cursor.execute("""SELECT * FROM gps""")

        # assert
        expected = []

        self.assertEqual(list(cursor), expected)

    def test_b_drop_table_raise_operational_error(self):
        # arrange
        self.db.drop_table('gps')
        cursor = self.connection.cursor()

        # act & assert
        with self.assertRaises(sqlite3.OperationalError):
            cursor.execute("""SELECT * FROM gps""")

    def test_c_add_values(self):
        # arrange
        self.db.insert_values('gps', test_values)
        cursor = self.connection.cursor()

        # act
        cursor.execute('''SELECT * FROM gps''')

        # assert
        expected = expected_values
        self.assertEqual(list(cursor), expected)

    def test_d_insert_dataframe(self):
        # arrange
        self.db.insert_dataframe('gps', test_values_df)
        cursor = self.connection.cursor()

        # act
        cursor.execute('''SELECT * FROM gps''')

        # assert
        expected = expected_values
        self.assertEqual(list(cursor), expected)

    def test_e_check_unique_id(self):
        # arrange
        for a in range(3):
            self.db.insert_values('gps', test_values)
        cursor = self.connection.cursor()

        # act
        cursor.execute('''SELECT * FROM gps''')

        # assert
        expected = 15  # last id number from database
        self.assertEqual(list(cursor)[-1][0], expected)

    def test_f_gps_table_length(self):
        # arrange
        for a in range(10):
            self.db.insert_dataframe('gps', test_values_df)
        table_length = self.db.table_length('gps')
        cursor = self.connection.cursor()

        # act
        cursor.execute('''SELECT * FROM gps''')

        # assert
        expected = table_length
        self.assertEqual(len(list(cursor)), expected)

    def test_g1_gps_find_duplicates_1(self):
        # arrange
        self.db.insert_dataframe('gps', test_values_df)
        duplicates = self.db.find_duplicates('gps')
        cursor = self.connection.cursor()

        # act
        execute = cursor.execute('''select count FROM 
                                (SELECT * , COUNT(*) as count
                                FROM gps
                                GROUP BY dt, position, speed, longitude, latitude
                                HAVING count > 1)''')  # number of duplicates

        # assert

        expected = duplicates.iloc[0][-1]

        self.assertEqual(list(execute), expected)

    def test_g2_gps_find_duplicates_2(self):
        # arrange
        self.db.insert_dataframe('gps', test_values_df)
        duplicates = self.db.find_duplicates('gps')
        cursor = self.connection.cursor()

        # act
        execute = list(cursor.execute('''SELECT * , COUNT(*)
                                        FROM gps
                                        GROUP BY dt, position, speed, longitude, latitude
                                        HAVING COUNT(*) > 1'''))[0]
        # assert

        expected = tuple(duplicates.iloc[0])

        self.assertEqual(execute, expected)

    def test_h_drop_duplicates(self):
        # arrange
        self.db.insert_dataframe('gps', test_values_df)
        self.db.drop_duplicates('gps')
        cursor = self.connection.cursor()

        # act
        cursor.execute('''SELECT * FROM gps''')

        # assert
        expected = len(test_values_df.drop_duplicates())

        self.assertEqual(len(list(cursor)), expected)

    def test_i_get_column_names(self):
        # arrange and act
        col_names = self.db.get_column_names('gps')

        # assert
        expected = expected_column_names
        self.assertEqual(col_names, expected)


class TestDBManagerSearchingValues(unittest.TestCase):
    db = None

    @classmethod
    def setUpClass(cls):
        print(f"\nTests - searching values.\n")
        cls.db = DBManager('test_company_db')
        cls.db.create_table('gps')
        cls.db.insert_values('gps', test_values)

    def test_search_with_no_args(self):
        arrange = len(list(self.db.search_values('gps')))
        result = len(test_values)
        self.assertEqual(arrange, result)

    @parameterized.expand([
        ('vehicle', 'gps', 'PL55555', '', None, 2),
        ('driver', 'gps', '', 'John Smith', None, 2),
        ('date_between', 'gps', '', '', ['2020-09-03', '2020-09-08'], 1),
    ])
    def test_search_with_args(self, test_name, table, vehicle, driver, between, result):
        self.assertEqual(len(list(self.db.search_values(table, vehicle, driver, between))), result)

    @parameterized.expand([
        ('vehicle', 'gps', 'PL55', '', None, 2),
        ('driver', 'gps', '', 'mith', None, 2),
        ('date_between_1', 'gps', '', '', ['2020-09-03', ''], 5),
        ('date_between_2', 'gps', '', '', [None, '2020-12-05'], 1),
    ])
    def test_search_with_incomplete_args(self, test_name, table, vehicle, driver, between, result):
        self.assertEqual(len(list(self.db.search_values(table, vehicle, driver, between))), result)

    @parameterized.expand([
        ('vehicle_sent_int_must_be_str', 'gps', 33, '', None),
        ('vehicle_sent_dict_must_be_str', 'gps', {}, '', None),
        ('driver_sent_int_must_be_str', 'gps', '', 1, None),
        ('driver_sent_dict_must_be_str', 'gps', '', {1: 'add'}, None),
        ('date_between_sent_int_must_be_list', 'gps', '', '', 22),
        ('date_between_sent_dict_must_be_list', 'gps', '', '', {}),
    ])
    def test_search_raise_type_errors(self, test_name, table, vehicle, driver, between):
        self.assertRaises(TypeError, self.db.search_values(table, vehicle, driver, between))

    @parameterized.expand([
        ('three_element_list', 'gps', '', '', [1, 2, 3]),
        ('one_element_list', 'gps', '', '', [1]),

    ])
    def test_search_between_arg_raise_exceptions(self, test_name, table, vehicle, driver, between):
        search = self.db.search_values(table, vehicle, driver, between)
        self.assertRaises(Exception, search)

    @parameterized.expand([
        ('sent_list_with_int', 'gps', '', '', ['int', 56]),
        ('sent_list_with_dict', 'gps', '', '', [0.33, {}]),

    ])
    def test_search_between_arg_raise_typeerror(self, test_name, table, vehicle, driver, between):
        self.assertRaises(TypeError, self.db.search_values(table, vehicle, driver, between))


if __name__ == '__main__':
    unittest.main(verbosity=2)
