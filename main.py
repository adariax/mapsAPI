from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.Qt import QPixmap, QImage

from ui_window import Ui_MainWindow

import requests
import sys

STATIC_API_URL = 'http://static-maps.yandex.ru/1.x/'


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.static_api_params = {'ll': '37.589434,55.734088',
                                  'z': '15',
                                  'l': 'map',
                                  'size': '450,450'}
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
