from gps_data_reader.db_manager import DBManager
import folium
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class GpsDataReader:
    """GpsDataReader search and analyzes transportation routes according to provided guidelines.

        'Attributes'
        ------------
            company (str): transporation company name/database or path.
            vehicle (str, optional): registration number of the vehicle.
            driver (str, optional): driver name/surname.
            date_range(list of str, optional): start/end date of route. Format - ["yyyy-mm-dd", "yyyy-mm-dd"].
                                               Default - None.
    """

    def __init__(self, company, vehicle='', driver='', date_range=None):
        self._company = company
        self.__database = DBManager(database=company + ".db")
        self._gps_data = GpsDataReader.__gps_data_setter(self, vehicle=vehicle, driver=driver, date_range=date_range)

    def __repr__(self):
        return f"{type(self).__name__} - ({self.company})"

    def __gps_data_setter(self, vehicle, driver, date_range):
        if any((vehicle, driver, date_range)):
            data_gen = self.__database.search_values(table='gps', vehicle=vehicle, driver=driver, between=date_range)
            data = self.__database.generator_converter(data_gen)
            col_names = self.__database.get_column_names('gps')

            gps_data = dict()
            for index, col in enumerate(col_names):
                gps_data[col] = data[:, index]
            return gps_data

        else:
            print('No data selected.')

    def __is_data_selected(self):
        if self._gps_data is None:
            raise Exception('No data selected.')

    def __set_boundries(self):

        country_np = self._gps_data['country']
        aux_list = ['start']  # add start point

        for index, country in enumerate(country_np):
            index += 1
            try:
                if country_np[index] != country_np[index - 1]:
                    aux_list.append('entry')
                elif country_np[index] != country_np[index + 1]:
                    aux_list.append('exit')
                else:
                    aux_list.append(np.NaN)
            except IndexError:
                break

        aux_list.append('end')  # add end point
        return aux_list

    def __get_coordinates(self):
        coordinates = ((x, y) for x, y in zip(self._gps_data['latitude'], self._gps_data['longitude']))
        return coordinates

    def __get_start_end_coordinates(self):
        coordinates = list(self.__get_coordinates())
        start, end = (coordinates[0][0], coordinates[0][1]), (coordinates[-1][0], coordinates[-1][1])
        return start, end

    def __get_start_end_data(self):
        start_end_data = {i: [self._gps_data[i][0], self._gps_data[i][-1]] for i in self._gps_data.keys()}
        return start_end_data

    def __add_start_end_points_to_map(self, route_map):
        coordinates = list(self.__get_coordinates())

        # coords for start end points
        start, end = self.__get_start_end_coordinates()

        # start/end points data
        start_end_data = pd.DataFrame(self.__get_start_end_data())
        first_iloc = start_end_data.iloc[0]
        last_iloc = start_end_data.iloc[-1]

        # string block to display after click POPUP
        start_popup = folium.Popup(
            f"START POINT<br>dt: {first_iloc['dt']}<br>vehicle: {first_iloc['vehicle']}<br>"
            f"driver: {first_iloc['driver']}<br>position: {first_iloc['position']}<br>"
            f"country: {first_iloc['country']}<br>speed: {first_iloc['speed']}<br>"
            f"mileage: {first_iloc['mileage']}",
            max_width=900)

        end_popup = popup = folium.Popup(
            f"END POINT<br>dt: {last_iloc['dt']}<br>vehicle: {last_iloc['vehicle']}<br>"
            f"driver: {last_iloc['driver']}<br>position: {last_iloc['position']}<br>"
            f"country: {last_iloc['country']}<br>speed: {last_iloc['speed']}<br>"
            f"mileage: {last_iloc['mileage']}",
            max_width=900)

        # string block to display TOOLTIP
        start_tooltip = f" {first_iloc['dt']};\n {first_iloc['vehicle']}; {first_iloc['position']}," \
                        f"{first_iloc['country']}"
        end_tooltip = f"{last_iloc['dt']};\n {last_iloc['vehicle']}; {last_iloc['position']}; {last_iloc['country']}"

        # add points to the map
        # start point
        folium.Marker(start, icon=folium.Icon(color='black', icon='play', prefix='fa', max_width=900),
                      popup=start_popup, tooltip=start_tooltip).add_to(route_map)
        # end point
        folium.Marker(end, icon=folium.Icon(color='black', icon='flag-checkered', prefix='fa'), popup=end_popup,
                      tooltip=end_tooltip).add_to(route_map)

    def __add_crossing_borders_to_map(self, route_map):

        cross_df = self.crossing_borders()
        index_filter = cross_df.index

        # crossing borders coords
        coordinates = list(self.__get_coordinates())
        cross_coordinates = [coordinates[i] for i in index_filter]

        # border crossing points
        for i in range(1, len(cross_df) - 1):  # range skip start and end points

            # popup and toolip string blocks
            from_condition = cross_df.iloc[i - 1]['country'] if i % 2 == 0 else cross_df.iloc[i]['country']
            to_condition = cross_df.iloc[i]['country'] if i % 2 == 0 else cross_df.iloc[i + 1]['country']

            i_popup = folium.Popup(f"dt: {cross_df.iloc[i]['dt']}<br>vehicle: {cross_df.iloc[i]['vehicle']}<br>"
                                   f"driver: {cross_df.iloc[i]['driver']}<br>position: {cross_df.iloc[i]['position']}"
                                   f"<br>country: {cross_df.iloc[i]['country']}<br>"
                                   f"Occurence: From {from_condition} To {to_condition}",
                                   max_width=900)

            i_tooltip = f"{cross_df.iloc[i]['dt']};\n {cross_df.iloc[i]['vehicle']}; " \
                        f"{cross_df.iloc[i]['position']}, {cross_df.iloc[i]['country']}"

            # entry points
            if i % 2 == 0:
                folium.Marker(cross_coordinates[i],
                              icon=folium.Icon(color='green', icon='sign-in', prefix='fa', max_width=900),
                              popup=i_popup, tooltip=i_tooltip).add_to(route_map)
            # exit points
            else:
                folium.Marker(cross_coordinates[i],
                              icon=folium.Icon(color='red', icon='sign-out', prefix='fa', max_width=900),
                              popup=i_popup, tooltip=i_tooltip).add_to(route_map)

    def __get_df_for_diagrams(self):
        gps_data = self._gps_data.copy()
        df = pd.DataFrame(data={'dt': gps_data['dt'],
                                'speed': gps_data['speed'],
                                'mileage': gps_data['mileage'],
                                })
        # convert types
        df = df.astype(dtype={'speed': 'float64', 'mileage': 'float64'})
        df['dt'] = pd.to_datetime(df['dt'], dayfirst=True)
        df['date'] = df['dt'].dt.date

        # fill Nan
        df['speed'].fillna(0, inplace=True)
        df['mileage'].fillna(method='ffill', inplace=True)
        return df

    @property
    def gps_data(self):
        """Get gps_data atrribute."""
        return self._gps_data

    @property
    def company(self):
        """Get company atrribute."""
        return self._company

    def data_filter(self, vehicle="", driver="", date_range=None):
        """Select data to display.

            Parameters
            ----------
                vehicle (str): register number of the vehicle.
                driver (str): name of the driver.
                data_range (list): start/end date. Format - ["yyyy-mm-dd", "yyyy-mm-dd"]

            Sets the gps_data attribute.
        """
        del self._gps_data
        self._gps_data = GpsDataReader.__gps_data_setter(self, vehicle, driver, date_range)
        print(f"{len(self._gps_data['id'])} rows selected.")

    def route_info(self):
        """ Extracts summary information about the route from selected data.

            Returns
            ----------
            pandas.DataFrame
        """
        self.__is_data_selected()
        gps_data = self._gps_data.copy()

        vehicle = np.unique(gps_data['vehicle']).tolist()
        driver = np.unique(gps_data['driver']).tolist()
        start_end_date = gps_data['dt'].min(), gps_data['dt'].max()
        start_end_country = [gps_data['country'][0], gps_data['country'][len(gps_data['country']) - 1]]

        mileage = pd.Series(gps_data['mileage'])
        start_end_mileage = mileage.min(), mileage.max()

        distance = mileage.max() - mileage.min()

        route_info = pd.DataFrame(data={self._company: [vehicle, driver, start_end_date, start_end_country,
                                                        start_end_mileage, distance]},
                                  index=['vehicle', 'driver', 'start/end date', 'start/end country',
                                         'start/end mileage', 'distance(km)'])
        return route_info

    def crossing_borders(self):
        """ Selects points and detailed information about border crossing.

            Returns
            ----------
            pandas.DataFrame
        """
        aux_list = self.__set_boundries()
        gps_df = pd.DataFrame(data={'dt': self._gps_data['dt'],
                                    'vehicle': self._gps_data['vehicle'],
                                    'driver': self._gps_data['driver'],
                                    'position': self._gps_data['position'],
                                    'country': self._gps_data['country']})
        gps_df['borders'] = aux_list
        crossing_borders_df = gps_df[~gps_df['borders'].isnull()]
        return crossing_borders_df

    def route_map(self, crossing_broders=False):
        """ Displays gps trace signal map with start/end points.

            Parameters
            ----------
            crossing_borders (bool): True - to add crossing borders points.

            Returns
            ----------
            folium.Map: route path map.
        """
        gps = pd.DataFrame(self._gps_data.copy())
        gps.drop('id', axis=1, inplace=True)

        coordinates = list(self.__get_coordinates())

        # start location point
        start_location = (coordinates[0][0], coordinates[0][1])

        route_map = folium.Map(location=start_location, zoom_start=6)

        i = 0
        for coords in coordinates:
            popup = folium.Popup(
                f"dt: {gps.iloc[i]['dt']}<br>vehicle: {gps.iloc[i]['vehicle']}<br>"
                f"driver: {gps.iloc[i]['driver']}<br>position: {gps.iloc[i]['position']}<br>"
                f"country: {gps.iloc[i]['country']}<br>speed: {gps.iloc[i]['speed']}<br>"
                f"mileage: {gps.iloc[i]['mileage']}",
                max_width=900)
            folium.CircleMarker(location=coords,
                                popup=popup,
                                tooltip=f"{gps.iloc[i]['dt']};\n {gps.iloc[i]['vehicle']}; "
                                        f"{gps.iloc[i]['position']}, {gps.iloc[i]['country']}",
                                radius=2, weight=4,
                                color='#6495ED',
                                bubblingMouseEvents=False, ).add_to(route_map)
            i += 1

        self.__add_start_end_points_to_map(route_map=route_map)

        if crossing_broders:
            self.__add_crossing_borders_to_map(route_map)

        return route_map

    def crossing_borders_map(self):
        """ Displays map with crossing borders points.

            Returns
            ----------
            folium.Map
        """
        coordinates = list(self.__get_coordinates())
        start_location = self.__get_start_end_coordinates()[0]

        route_map = folium.Map(location=start_location, zoom_start=6)
        self.__add_start_end_points_to_map(route_map)
        self.__add_crossing_borders_to_map(route_map)
        return route_map

    def distance_diagram(self):
        """ Displays travelled distance per day in kilometers.

            Returns
            ----------
            plotly.graph_object: plotly figure.
        """
        distance_df = self.__get_df_for_diagrams()

        def km_per_point(df):
            aux_list = []
            for i in range(0, len(df['mileage'])):
                if i == len(df['mileage']) - 1:
                    aux_list.append(df['mileage'].max() - df['mileage'].iloc[i])
                else:
                    aux_list.append(df['mileage'].iloc[i + 1] - df['mileage'].iloc[i])
            return aux_list

        # distance - per point, cumsum, grouped by day
        km_per_point_list = km_per_point(distance_df)
        distance_df['km'] = km_per_point_list
        distance_df['km_cumsum'] = distance_df['km'].cumsum()
        date_grouped = distance_df.groupby('date')['km'].sum()

        # prepare plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=date_grouped.index, y=date_grouped, name='km/day'))

        fig.add_trace(go.Scatter(x=distance_df['dt'], y=distance_df['km_cumsum'], name='km'), secondary_y=True)

        fig.update_layout(title_text='KM diagram', width=1000,
                          xaxis=dict(
                              tickmode='linear'))

        fig.update_yaxes(title_text="km", secondary_y=False)
        fig.update_yaxes(title_text="km cumsum", secondary_y=True)

        print(fig.show())

    def speed_diagram(self):
        """ Displays vehicle speed trace and daily average speed.

            Returns
            ----------
            plotly.graph_object: plotly figure.
        """
        speed_df = self.__get_df_for_diagrams()

        fig = go.Figure(layout=go.Layout(yaxis=dict(range=[0, 100])))

        fig.add_trace(go.Scatter(x=speed_df['dt'], y=speed_df['speed'], name='speed (km/h)'))

        fig.add_trace(go.Scatter(x=speed_df.groupby('date').agg('mean')['speed'].index,
                                 y=speed_df.groupby('date').agg('mean')['speed'],
                                 name='day mean'))

        fig.update_layout(title_text='Speed diagram', width=1000, yaxis_title='km/h',
                          xaxis=dict(
                              tickmode='linear'))
        fig.show()
