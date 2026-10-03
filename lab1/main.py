import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Окно с кнопкой и картинкой"""

    INITIAL_TEXT = ""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Лабораторная работа №1")
        self.resize(650, 500)

        self.label = QLabel(self.INITIAL_TEXT)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px;")

        self.button = QPushButton("Тыкни на меня")
        self.button.setStyleSheet("font-size: 18px; padding: 10px;")

        self.back_button = QPushButton("Хочу назад")
        self.back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.back_button.hide()

        # Сигнал нажатия кнопки соединён со слотом show_picture
        self.button.clicked.connect(self.show_picture)
        self.back_button.clicked.connect(self.show_start_screen)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.addWidget(self.label, stretch=1)
        layout.addWidget(self.button)
        layout.addWidget(self.back_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_picture(self):
        """Заменяет текст надписи изображением picture.jpg"""
        image_path = Path(__file__).resolve().parent / "picture.jpg"
        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():
            self.label.setText(f"Не удалось загрузить изображение:\n{image_path}")
            return

        pixmap = pixmap.scaled(
            560,
            380,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label.clear()
        self.label.setPixmap(pixmap)
        self.button.hide()
        self.back_button.show()

    def show_start_screen(self):
        """Возвращает надпись и исходную кнопку"""
        self.label.clear()
        self.label.setText(self.INITIAL_TEXT)
        self.back_button.hide()
        self.button.show()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
