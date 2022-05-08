import sys, requests
from io import BytesIO
from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QDialog, QVBoxLayout, QDateTimeEdit, QDialogButtonBox, \
    QTextEdit, QLineEdit, QLabel
import yandex_map_helper 


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('interface.ui', self)
        self.zoom = 12
        self.last_coords = '30.315635 59.938951'
        self.zoomButton.clicked.connect(self.get_zoom)
        self.coordsButton.clicked.connect(self.get_coords)
        self.get_map()

    def get_zoom(self):
        zoom, ok = ZoomDialog.get_zoom(self.zoom)
        self.zoom = zoom
        self.get_map()

    def get_coords(self):
        coords, ok = CoordsDialog.get_coordinates(self.last_coords)
        if ok:
            self.coordinates.setText(coords)
            self.get_map()

    def get_map(self):
        #print(self.verticalSlider.value())

        try:
            toponym_longitude, toponym_lattitude = self.coordinates.text().split(" ")
        except:
            self.coordinates.setText(" ".join(self.last_coords))
            toponym_longitude, toponym_lattitude = self.last_coords
            self.errorlabel.setText('Координаты должны быть разделены пробелом')
            
        map_params = yandex_map_helper.set_map_params(toponym_longitude, toponym_lattitude, self.zoom)
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        
        try:
            result = Image.open(BytesIO(response.content))
            result.save('res.png')
            self.errorlabel.setText('')
            
            self.picture.setPixmap(QPixmap('res.png'))  
            self.last_coords = self.coordinates.text().split(" ")
        except:
            self.coordinates.setText(" ".join(self.last_coords))
            self.errorlabel.setText('Какие-то стремные координаты')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Up:
            print("up")
        elif e.key() == Qt.Key_Down:
            print("down")
        elif e.key() == Qt.Key_Left:
            print("left")
        elif e.key() == Qt.Key_Right:
            print("right")

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
