from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.Qt import QPixmap, QImage, Qt

from ui_window import Ui_MainWindow

import requests
import sys

STATIC_API_URL = 'http://static-maps.yandex.ru/1.x/'


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.static_api_params = {'ll': '37.588392,55.734036',
                                  'z': 13,
                                  'l': 'map',
                                  'size': '450,450'}

        # Connect layouts buttons
        self.rb_map.toggled.connect(self.change_layouts)
        self.rb_sat.toggled.connect(self.change_layouts)
        self.cb_trf.stateChanged.connect(self.change_layouts)
        self.cb_skl.stateChanged.connect(self.change_layouts)

        self.bt_search.clicked.connect(self.search_by_button)

        self.update_image()

    def update_image(self):
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
        x, y = map(float, self.static_api_params["ll"].split(','))
        move_delta = 180 / (2 ** self.static_api_params["z"])
        x = (x + move_delta * 2 * dx) % 360
        if x > 180:
            x -= 360
        y = (y + move_delta * dy) % 180
        if y > 90:
            y -= 180
        self.static_api_params["ll"] = '%f,%f' % (x, y)
        self.update_image()

    def change_scale(self, d: int):
        # d - {1, -1}
        z = self.static_api_params["z"]
        z += d
        if not (0 <= z <= 17):
            return
        self.static_api_params["z"] = z
        self.update_image()

    def change_layouts(self):
        # Update layouts information from buttons
        layouts = ['map' if self.rb_map.isChecked() else 'sat']  # main layout
        if self.cb_trf.isChecked():  # Traffic jams
            layouts.append('trf')
        if self.cb_skl.isChecked():  # Toponyms name
            layouts.append('skl')

        self.static_api_params["l"] = ','.join(layouts)
        self.update_image()

    def search_by_button(self):
        toponym_to_find = self.le_search.text()

        # Make search by organization and geocoder

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        search_api_server = "https://search-maps.yandex.ru/v1/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        search_params = {
            "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
            "text": toponym_to_find,
            "lang": 'ru_RU'}

        geocoder_response = requests.get(geocoder_api_server, params=geocoder_params)
        search_response = requests.get(search_api_server, params=search_params)

        if not geocoder_response:
            return

        geocoder_response_json = geocoder_response.json()
        search_response_json = search_response.json()

        # Get list of toponyms for checking finding toponyms
        geocoder_toponyms = geocoder_response_json["response"]["GeoObjectCollection"] \
            ["featureMember"]
        # Check if the Search by Org. couldn't found
        if search_response_json['properties']['ResponseMetaData']['SearchRequest']['results']:
            toponym_coordinates = ','.join(map(str, search_response_json['features'][0] \
                                               ["geometry"]["coordinates"]))
        elif len(geocoder_toponyms):
            toponym_coordinates = geocoder_toponyms[0]["GeoObject"] \
                ["Point"]["pos"].replace(' ', ',')
        else:
            return  # Exit if the toponym weren't found

        self.static_api_params['ll'] = toponym_coordinates  # Update coords of founded toponym
        self.static_api_params['pt'] = f'{toponym_coordinates},org'  # Make a point on the map

        self.update_image()

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
