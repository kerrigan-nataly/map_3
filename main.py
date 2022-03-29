import sys, requests
from io import BytesIO
from PIL import Image
from PyQt5.Qt import Qt
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider

import yandex_map_helper 


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('interface.ui', self)

        self.last_coords = "30.315635 59.938951"
        self.coordinates.setText(self.last_coords)

        self.verticalSlider.setTickInterval(17)
        self.verticalSlider.setMinimum(0)
        self.verticalSlider.setMaximum(17)
        self.verticalSlider.setSingleStep(1)
        self.verticalSlider.setTickPosition(QSlider.TicksBelow)

        self.verticalSlider.setValue(12)

        self.pushButton.clicked.connect(self.get_map)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.zoom(1)
        elif event.key() == Qt.Key_PageDown:
            self.zoom(-1)

    def get_map(self):
        #print(self.verticalSlider.value())
        try:
            toponym_longitude, toponym_lattitude = self.coordinates.text().split(" ")
        except:
            self.coordinates.setText(" ".join(self.last_coords))
            toponym_longitude, toponym_lattitude = self.last_coords
            self.errorlabel.setText('Координаты должны быть разделены пробелом')
            
        map_params = yandex_map_helper.set_map_params(toponym_longitude, toponym_lattitude, self.verticalSlider.value())
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
            
    def zoom(self, value):
        self.verticalSlider.setValue(self.verticalSlider.value() + value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
    ex.connection.close()
