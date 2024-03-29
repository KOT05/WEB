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

        self.mark_coords = []
        # Записываем количество нажатий клавиш стрелок по осям (влево и вправо, вверх и вниз соответственно)
        self.inputs_counts = [0, 0]

        # задаем координаты, масштаб и слой карты

        self.coords = [37.4821434, 55.6629601]
        self.size = 0.005

        self.layer_switch_button = QPushButton(self, text='Сменить вид карты')
        self.layer_switch_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.layer_switch_button.setGeometry(50, 50, 150, 30)
        self.layer_switch_button.clicked.connect(self.switch_layer)

        self.find_field = QLineEdit(self)
        self.find_field.setGeometry(50, 10, 420, 30)
        # self.find_field.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.find_button = QPushButton(self, text='Искать')
        self.find_button.setGeometry(480, 10, 70, 30)
        self.find_button.clicked.connect(self.find_adress)
        self.find_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.layers = ["map", "sat", "skl"]
        self.layer_i = 0

        self.get_image(self.coords, self.size, self.layers[self.layer_i])

    def find_adress(self):
        map_params = {
            "geocode": self.find_field.text().lower(),
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "format": "json"
        }

        response = requests.get("https://geocode-maps.yandex.ru/1.x", params=map_params)
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            print('Ошибка поиска')
        else:
            lon, lat = found_places[0]['GeoObject']['Point']['pos'].split(" ")
            self.coords = [float(lon), float(lat)]
            self.mark_coords = self.coords.copy()
            self.inputs_counts = [0, 0]
            self.get_image(self.coords, self.size, self.layers[self.layer_i], True)
        self.find_field.clearFocus()

    def switch_layer(self):
        mark_exists = False
        if any(self.mark_coords):
            mark_exists = True

        self.layer_i += 1
        self.layer_i %= 3
        self.get_image(self.coords, self.size, self.layers[self.layer_i], mark_exists)

    def get_image(self, coords, size, layer, is_with_mark=False):
        # создание запроса
        map_params = {
            "ll": f"{coords[0]},{coords[1]}",
            "spn": f"{size},{size}",
            "l": layer
        }
        if is_with_mark and not any(self.inputs_counts):
            map_params['pt'] = f"{coords[0]},{coords[1]}"

        response = requests.get("http://static-maps.yandex.ru/1.x/", params=map_params)

        # запись полученное изображение в файл для дальгейшей работы
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        # вывод изображения
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

        # При закрытии формы подчищаем за собой
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        mark_exists = False
        if any(self.mark_coords):
            mark_exists = True

        if event.key() == Qt.Key_PageUp:
            self.size += self.size / 2
        if event.key() == Qt.Key_PageDown:
            self.size -= self.size / 2
            if self.size < 0.00001:
                self.size = 0.00001

        if event.key() == Qt.Key_Down:
            self.coords[1] -= self.size * 2
            self.inputs_counts[1] -= 1
        if event.key() == Qt.Key_Up:
            self.coords[1] += self.size * 2
            self.inputs_counts[1] += 1
        if event.key() == Qt.Key_Right:
            self.coords[0] += self.size * 2
            self.inputs_counts[0] += 1
        if event.key() == Qt.Key_Left:
            self.coords[0] -= self.size * 2
            self.inputs_counts[0] -= 1

        self.get_image(self.coords, self.size, self.layers[self.layer_i], mark_exists)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YandexMapWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
