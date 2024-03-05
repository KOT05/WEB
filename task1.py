import os
import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

SCREEN_SIZE = [600, 450]


class YandexMapWidget(QWidget):
    def __init__(self):
        super().__init__()

        # начальные настройки
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.move(600, 250)

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        # задаем координаты, масштаб и слой карты
        self.coords = [37.4821434, 55.6629601]
        self.size = 0.005
        self.layer = "map"

        self.get_image(self.coords, self.size, self.layer)

    def get_image(self, coords, size, layer):
        # создание запроса
        map_params = {"ll": f"{coords[0]},{coords[1]}",
                      "spn": f"{size},{size}",
                      "l": layer}

        response = requests.get("http://static-maps.yandex.ru/1.x/", params=map_params)

        # запись полученное изображение в файл для дальгейшей работы
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        # вывод изображения
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YandexMapWidget()
    ex.show()
    sys.exit(app.exec())
