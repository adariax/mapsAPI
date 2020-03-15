from pprint import pprint

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.Qt import QPixmap, QImage, Qt

from ui_window import Ui_MainWindow

import requests
import sys

STATIC_API_URL = 'http://static-maps.yandex.ru/1.x/'
GEOCODER_API_URL = "http://geocode-maps.yandex.ru/1.x/"
GEOCODER_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
SEARCH_URL = "https://search-maps.yandex.ru/v1/"
SEARCH_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"


def point_to_str(p):
    """convert point to http format"""
    return "%.8f" % p[0] + "," + "%.8f" % p[1]


def lon_mod(lon):  # Return correctly longitude for coords
    if lon > 180:
        return lon - 360
    elif lon <= -180:
        return lon + 360
    else:
        return lon


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.static_api_params = {'l': 'map',
                                  'size': '450,450'}

        self._z = 17
        self._ll = 37.588392, 55.734036
        self.apply_cords()

        self._toponym = None  # Store toponym json if found

        # Connect layouts buttons
        self.rb_map.toggled.connect(self.change_layouts)
        self.rb_sat.toggled.connect(self.change_layouts)
        self.cb_trf.stateChanged.connect(self.change_layouts)
        self.cb_skl.stateChanged.connect(self.change_layouts)

        self.bt_search.clicked.connect(self.search_by_button)
        self.bt_clean.clicked.connect(self.clean_result)

        self.cb_pcd.stateChanged.connect(self.show_info)

        self.setMouseTracking(True)

    @property
    def ll(self):
        return self._ll

    @property
    def z(self):
        return self._z

    @property
    def toponym(self):
        return self._toponym

    def apply_cords(self):
        """Translate (z, ll) to (spn, ll)  and update image"""
        x, y = self.ll
        e = 0
        scale_e = e / (2 ** self.z)
        delta = (360 - e) / (2 ** self.z)
        lower_corner = [x - delta / 2, y - delta / 2]
        upper_corner = [x + delta / 2, y + delta / 2]

        # Check borders and move map if get out
        if lower_corner[0] <= -180:
            xd = lower_corner[0] + 180 - scale_e
            x -= xd
        elif upper_corner[0] >= 180:
            xd = upper_corner[0] - 180 + scale_e
            x -= xd

        if lower_corner[1] < -90:
            yd = lower_corner[1] + 90 - scale_e
            y -= yd
        elif upper_corner[1] > 90:
            yd = upper_corner[1] - 90 + scale_e
            y -= yd

        self.static_api_params["ll"] = point_to_str((x, y))
        self.static_api_params["spn"] = point_to_str((delta, delta))
        self.update_image()

    @ll.setter
    def ll(self, ll):
        # Change center of map
        if not (-180 <= ll[0] <= 180 and -90 <= ll[1] <= 90):
            return
        self._ll = ll
        self.apply_cords()

    @z.setter
    def z(self, z):
        # Change scale of map
        if not (3 <= z <= 20):
            return
        self._z = z
        self.apply_cords()

    @toponym.setter
    def toponym(self, toponym):
        if toponym:
            if 'geometry' in toponym:
                point_coords = ','.join(map(str, toponym["geometry"]["coordinates"]))
            elif 'Point' in toponym:
                point_coords = toponym["Point"]["pos"].replace(" ", ",")
            self.static_api_params['pt'] = f'{point_coords},org'
        self._toponym = toponym
        self.show_info()

    def update_image(self):
        print(f"z: {self.z}, ll: {self.ll}")
        pprint(self.static_api_params)

        # Get image from staticAPI
        response = requests.get(STATIC_API_URL, params=self.static_api_params)
        self.map_container.clear()
        if response is None:
            # Report an error
            self.map_container.setText("Connection Failed")
        else:
            # Set image
            img = QPixmap.fromImage(QImage.fromData(response.content))
            self.map_container.setPixmap(img)

    def move_map(self, dx, dy):
        x, y = self.ll
        move_delta = 360 / (2 ** self.z)
        x = (x + move_delta * 2 * dx) % 360
        if x > 180:
            x -= 360
        y = (y + move_delta * dy) % 180
        if y > 90:
            y -= 180
        self.ll = x, y

    def change_scale(self, d: int):
        # d - {1, -1}
        self.z += d

    def get_degrees(self, x, y):
        spn = list(map(lambda coord: float(coord), self.static_api_params['spn'].split(',')))
        # Get degrees in 1 pixel
        one_pixel_x, one_pixel_y = map(lambda coord: coord / 450, spn)
        lon = lon_mod((self.ll[0] - spn[0]) + x * one_pixel_x * 2)  # Get correctly longitude
        lat = (self.ll[1] + spn[1]) - y * one_pixel_y * 2
        return [lon, lat] if 0 <= x < 450 and 0 <= y < 450 else None

    def change_layouts(self):
        # Update layouts information from buttons
        layouts = ['map' if self.rb_map.isChecked() else 'sat']  # main layout
        if self.cb_trf.isChecked():  # Traffic jams
            layouts.append('trf')
        if self.cb_skl.isChecked():  # Toponyms name
            layouts.append('skl')

        self.static_api_params["l"] = ','.join(layouts)
        self.update_image()

    def get_json_from_search(self, search_params, url=SEARCH_URL):  # Get response and return json
        current_params = search_params
        current_params['results'], current_params['lang'] = 1, 'ru_RU'
        search_response = requests.get(url, params=current_params)
        return search_response.json() if search_response else None

    def found_toponym_coords(self, result_json):  # Processing search response
        try:
            if 'features' in result_json:  # Check if response by Search
                found_toponym = result_json["features"][0]  # Here can be IndexError
                # So it mean that toponym wasn't found --> Exception
                toponym_coordinates = found_toponym["geometry"]["coordinates"]
            elif 'response' in result_json:  # Check if response by Geocoder
                found_toponym = result_json["response"]["GeoObjectCollection"]["featureMember"] \
                    [0]["GeoObject"]
                toponym_coordinates = found_toponym["Point"]["pos"]
            else:
                return
        except (IndexError, TypeError, KeyError):
            return
        else:
           self.toponym = found_toponym
           return toponym_coordinates

    def search_by_button(self):
        self.clean_info()  # Delete  info about past toponym

        toponym_to_find = self.le_search.text()

        # Make search attributes
        search_params = {
            "apikey": SEARCH_KEY,
            "text": toponym_to_find
        }
        # Get coords of founded toponym and position the map on them
        coords = self.found_toponym_coords(self.get_json_from_search(search_params, SEARCH_URL))
        self.ll = coords if coords else self._ll

    def show_info(self):
        self.pt_info.clear()  # Delete  info about past toponym

        if self.toponym is None:  # If no toponym
            return

        info_to_show = []
        toponym = self.toponym['properties'] if 'properties' in self.toponym \
            else self.toponym['metaDataProperty']  # Get info by type of response
        if 'GeocoderMetaData' in toponym:  # Checking type of toponym: org. or geoobj.
            info_to_show.append(toponym['GeocoderMetaData']['text'])
        else:
            info_to_show.append(toponym['CompanyMetaData']['address'])

        if self.cb_pcd.isChecked():
            # Searching object's postal code
            geocoder_params = {
                "apikey": GEOCODER_API_KEY,
                "geocode": info_to_show[0],
                "format": "json"}
            json_response = self.get_json_from_search(geocoder_params, GEOCODER_API_URL)
            try:
                postal_code = json_response["response"]["GeoObjectCollection"]["featureMember"][0] \
                    ["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
            except (KeyError, TypeError):  # If toponym has not postal code
                postal_code = 'Not found'

            info_to_show.append(f'Индекс: {postal_code}')

        for string in info_to_show:  # Append toponym's info to pt_info (PlainTextEdit)
            self.pt_info.appendPlainText(string)

    def clean_result(self):
        self.clean_info()
        self.remove_point()
        self.update_image()  # For removing point

    def remove_point(self):  # Delete all info about points on map
        if 'pt' in self.static_api_params:
            del self.static_api_params['pt']

    def clean_info(self):  # Clean showed in pt_info (PlainTextEdit) address
        self.pt_info.clear()
        self.toponym = None

    def mousePressEvent(self, event):
        x, y = event.x() - 9, event.y() - 15
        coords = self.get_degrees(x, y)  # Get coords by click
        if coords:
            if event.button() == Qt.LeftButton:
                geocoder_params = {"apikey": GEOCODER_API_KEY,
                                   "geocode": ','.join(map(str, coords)),
                                   "format": "json"}
                self.found_toponym_coords(self.get_json_from_search(geocoder_params,
                                                                    GEOCODER_API_URL))
            elif event.button() == Qt.RightButton:
                pass
            self.update_image()  # Show point

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_PageUp:
            self.change_scale(1)
        elif a0.key() == Qt.Key_PageDown:
            self.change_scale(-1)
        elif a0.key() == Qt.Key_Up:
            self.move_map(0, 1)
        elif a0.key() == Qt.Key_Down:
            self.move_map(0, -1)
        elif a0.key() == Qt.Key_Left:
            self.move_map(-1, 0)
        elif a0.key() == Qt.Key_Right:
            self.move_map(1, 0)
        elif a0.key() == Qt.Key_Enter:
            self.map_container.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
