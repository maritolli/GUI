import base64
import binascii
import sys
from pathlib import Path

from PyQt5.QtCore import QObject, QIODevice, QSaveFile, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Interface(QObject):
    """Связывает QML-холст с таймером и файловой системой."""

    saveRequested = pyqtSignal()
    statusChanged = pyqtSignal(str, arguments=["message"])

    AUTOSAVE_INTERVAL_MS = 5_000
    HISTORY_SIZE = 2

    def __init__(self, autosave_directory):
        super().__init__()
        self.autosave_directory = Path(autosave_directory)
        self._dirty = False

        self.timer = QTimer(self)
        self.timer.setInterval(self.AUTOSAVE_INTERVAL_MS)
        self.timer.timeout.connect(self.request_save)
        self.timer.start()

    @pyqtSlot()
    def markDirty(self):
        """Отмечает, что после последнего сохранения холст изменился."""
        if not self._dirty:
            self._dirty = True
            self.statusChanged.emit("Есть несохранённые изменения")

    @pyqtSlot()
    def request_save(self):
        """Просит QML передать изображение только при наличии изменений."""
        if self._dirty:
            self.saveRequested.emit()

    @pyqtSlot()
    def saveNow(self):
        """Принудительно сохраняет холст по нажатию кнопки."""
        self.statusChanged.emit("Сохранение…")
        self.saveRequested.emit()

    def _next_file(self):
        """Возвращает свободный файл или самый старый файл истории."""
        files = [
            self.autosave_directory / f"canvas_{number}.png"
            for number in range(1, self.HISTORY_SIZE + 1)
        ]
        for file_path in files:
            if not file_path.exists():
                return file_path
        return min(files, key=lambda file_path: file_path.stat().st_mtime_ns)

    @pyqtSlot(str)
    def saveCanvas(self, data_url):
        """Декодирует PNG из QML и записывает его в историю автосохранений."""
        try:
            header, encoded_data = data_url.split(",", 1)
            if header != "data:image/png;base64":
                raise ValueError("получены данные неизвестного формата")

            image_data = base64.b64decode(encoded_data, validate=True)
            if not image_data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("данные не являются PNG-изображением")

            self.autosave_directory.mkdir(parents=True, exist_ok=True)
            file_path = self._next_file()

            output = QSaveFile(str(file_path))
            if not output.open(QIODevice.WriteOnly):
                raise OSError(output.errorString())
            if output.write(image_data) != len(image_data):
                output.cancelWriting()
                raise OSError(output.errorString())
            if not output.commit():
                raise OSError(output.errorString())

        except (ValueError, binascii.Error, OSError) as error:
            self.statusChanged.emit(f"Ошибка автосохранения: {error}")
            return

        self._dirty = False
        self.statusChanged.emit(f"Сохранено: autosave/{file_path.name}")


def main():
    application = QGuiApplication(sys.argv)
    lab_directory = Path(__file__).resolve().parent

    interface = Interface(lab_directory / "autosave")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)
    engine.load(QUrl.fromLocalFile(str(lab_directory / "mainWindow.qml")))

    if not engine.rootObjects():
        print("Ошибка: не удалось загрузить QML-файл.")
        return -1

    # Если окно закрывают до очередного срабатывания таймера,
    # последнее изменение всё равно будет сохранено.
    application.aboutToQuit.connect(interface.request_save)
    return application.exec_()


if __name__ == "__main__":
    sys.exit(main())
