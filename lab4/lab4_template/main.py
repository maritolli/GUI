import sys
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Interface(QObject):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':

    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    interface = Interface()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    # Загружаем QML
    engine.load("mainWindow.qml")

    # Проверка успешной загрузки QML
    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    sys.exit(app.exec())
