import sys, requests
from io import BytesIO
from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QDialogButtonBox, \
    QLineEdit, QComboBox
from PyQt5.QtCore import *

import yandex_map_helper


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.zoom = 0.2
        self.place = ''
        self.place_point = ''
        self.map_type = 'map'
        self.last_coordinates = '30.315635 59.938951'
        self.initUI()

    def initUI(self):
        uic.loadUi('interface.ui', self)
        self.zoomButton.clicked.connect(self.get_zoom)
        self.coordsButton.clicked.connect(self.get_coords)
        self.mapTypeButton.clicked.connect(self.map_type_select)
        self.searchButton.clicked.connect(self.searchPlace)
        self.resetButton.clicked.connect(self.resetPlace)
        self.placeLineEdit.installEventFilter(self)
        self.get_map()

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.releaseKeyboard()
            self.placeLineEdit.setFocusPolicy(Qt.StrongFocus)
            self.placeLineEdit.setReadOnly(False)
            return True
        return False

    def resetPlace(self):
        self.placeLineEdit.setText('')
        self.place = ''
        self.place_point = ''
        self.get_map()

    def searchPlace(self):
        place = self.placeLineEdit.text()
        map_params = {
            "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
            "geocode": place,
            "results": '1',
            "lang": "ru_RU",
            "format": "json"
        }
        map_api_server = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(map_api_server, params=map_params)
        json_response = response.json()
        data = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        coordinates = data['Point']['pos']
        self.place = data['name']
        self.place_point = coordinates
        self.coordinates.setText(coordinates)

        self.placeLineEdit.setReadOnly(True)
        self.placeLineEdit.setFocusPolicy(Qt.NoFocus)
        self.grabKeyboard()
        self.get_map()

    def get_zoom(self):
        self.releaseKeyboard()
        zoom, ok = ZoomDialog.get_zoom(self.zoom)
        self.zoom = zoom
        self.get_map()

    def get_coords(self):
        self.releaseKeyboard()
        coordinates, ok = CoordsDialog.get_coordinates(self.last_coordinates)
        if ok:
            self.coordinates.setText(coordinates)
            self.get_map()

    def map_type_select(self):
        self.releaseKeyboard()
        map_type, ok = MapTypeDialog.get_type(self.map_type)
        if ok:
            self.map_type = map_type
            self.get_map()

    def get_map(self):
        try:
            toponym_longitude, toponym_latitude = self.coordinates.text().split(" ")
        except:
            self.coordinates.setText(" ".join(self.last_coordinates))
            toponym_longitude, toponym_latitude = self.last_coordinates
            self.errorlabel.setText('Координаты должны быть разделены пробелом')

        # map_params = {
        #     "ll": ",".join([toponym_longitude, toponym_latitude]),
        #     "spn": f'{float(self.zoom)},{float(self.zoom)}',
        #     "size": '431,431',
        #     "l": 'map'
        # }

        bblb = ','.join([
            str(float(toponym_longitude) + float(self.zoom)),
            str(float(toponym_latitude) - float(self.zoom))
        ])
        bbrt = ','.join([
            str(float(toponym_longitude) - float(self.zoom)),
            str(float(toponym_latitude) + float(self.zoom))
        ])
        map_params = {
            "bbox": f'{bblb}~{bbrt}',
            "size": '450,450',
            "l": self.map_type
        }
        if len(self.place) > 0:
            long, lat = self.place_point.split(" ")
            map_params['pt'] = f'{long},{lat},pm2rdm'
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        
        try:
            result = Image.open(BytesIO(response.content))
            result.save('res.png')
            self.errorlabel.setText('')
            
            self.picture.setPixmap(QPixmap('res.png'))  
            self.last_coordinates = self.coordinates.text().split(" ")
        except:
            self.coordinates.setText(" ".join(self.last_coordinates))
            self.errorlabel.setText('Какие-то стремные координаты')

    def keyPressEvent(self, e):
        mult = 3
        toponym_longitude, toponym_latitude = self.coordinates.text().split(" ")
        if e.key() == Qt.Key_Up:
            toponym_latitude = str(float(toponym_latitude) + float(self.zoom) * mult)
        elif e.key() == Qt.Key_Down:
            toponym_latitude = str(float(toponym_latitude) - float(self.zoom) * mult)
        elif e.key() == Qt.Key_Right:
            toponym_longitude = str(float(toponym_longitude) + float(self.zoom) * mult * 2)
        elif e.key() == Qt.Key_Left:
            toponym_longitude = str(float(toponym_longitude) - float(self.zoom) * mult * 2)

        self.coordinates.setText(' '.join([toponym_longitude, toponym_latitude]))
        self.get_map()


class CoordsDialog(QDialog):
    def __init__(self, last_coords, parent=None):
        super(CoordsDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        # nice widget for editing the date
        self.coords_field = QLineEdit(self)
        self.coords_field.setText(" ".join(last_coords))
        layout.addWidget(self.coords_field)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_coordinates(last_coords, parent=None):
        dialog = CoordsDialog(last_coords=last_coords, parent=parent)
        result = dialog.exec_()
        coords = dialog.coords_field.text()
        return (coords, result == QDialog.Accepted)


class MapTypeDialog(QDialog):
    def __init__(self, current_type, parent=None):
        super(MapTypeDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        self.map_type = QComboBox(self)
        self.map_type.addItem("map")
        self.map_type.addItem("sat")
        self.map_type.addItem("sat,skl")
        layout.addWidget(self.map_type)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_type(current_type, parent=None):
        dialog = MapTypeDialog(current_type=current_type, parent=parent)
        result = dialog.exec_()
        map_type = dialog.map_type.currentText()
        return (map_type, result == QDialog.Accepted)


class ZoomDialog(QDialog):
    def __init__(self, last_zoom, parent=None):
        super(ZoomDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        # nice widget for editing the date
        self.zoom_field = QLineEdit(self)
        self.zoom_field.setText(str(last_zoom))
        layout.addWidget(self.zoom_field)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def get_zoom(last_zoom, parent=None):
        dialog = ZoomDialog(last_zoom=last_zoom, parent=parent)
        result = dialog.exec_()
        zoom = dialog.zoom_field.text()
        return (zoom, QDialog.Accepted)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
    ex.connection.close()
