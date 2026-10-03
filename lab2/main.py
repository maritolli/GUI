import sys
import xml.etree.ElementTree as ET

from PyQt5.QtCore import QDate, QSignalBlocker, QTimer, QUrl, QUrlQuery
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWidgets import (
    QApplication,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CurrencyConverter(QMainWindow):
    """Конвертер валют, демонстрирующий сигналы и слоты Qt"""

    # Эти значения используются до первой успешной загрузки с сайта ЦБ РФ и в случае ошибок подключения к интернету
    DEFAULT_RUB_PER_USD = 70.00
    DEFAULT_RUB_PER_EUR = 90.00
    REQUEST_TIMEOUT_MS = 5_000

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Лабораторная работа №2 - конвертер валют")
        self.resize(500, 340)

        self.rub_per_usd = self.DEFAULT_RUB_PER_USD
        self.eur_per_usd = self.DEFAULT_RUB_PER_USD / self.DEFAULT_RUB_PER_EUR
        self.network = QNetworkAccessManager(self)

        description = QLabel(
            "Измените значение любой валюты и остальные поля "
            "пересчитаются автоматически."
        )
        description.setWordWrap(True)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setMaximumDate(QDate.currentDate())

        self.load_button = QPushButton("Загрузить курс")
        self.load_button.clicked.connect(self.load_rates)

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.load_button)

        self.rubles = self.create_money_field(" ₽")
        self.dollars = self.create_money_field(" $")
        self.euros = self.create_money_field(" €")

        form = QFormLayout()
        form.addRow("Рубли:", self.rubles)
        form.addRow("Доллары:", self.dollars)
        form.addRow("Евро:", self.euros)

        self.rates_label = QLabel()
        self.rates_label.setWordWrap(True)
        self.show_rates("учебный курс")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)
        layout.addWidget(description)
        layout.addLayout(date_layout)
        layout.addLayout(form)
        layout.addWidget(self.rates_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # valueChanged — сигналы, методы update_from_* — слоты.
        self.rubles.valueChanged.connect(self.update_from_rubles)
        self.dollars.valueChanged.connect(self.update_from_dollars)
        self.euros.valueChanged.connect(self.update_from_euros)

        self.dollars.setValue(1.00)

    def show_rates(self, source):
        """Показывает текущий курс и источник данных"""
        rub_per_eur = self.rub_per_usd / self.eur_per_usd
        self.rates_label.setText(
            f"{source.capitalize()}: 1 $ = {self.rub_per_usd:.4f} ₽; "
            f"1 € = {rub_per_eur:.4f} ₽."
        )

    def load_rates(self):
        """Асинхронно запрашивает официальные курсы на выбранную дату"""
        requested_date = self.date_edit.date()
        url = QUrl("https://www.cbr.ru/scripts/XML_daily.asp")
        query = QUrlQuery()
        query.addQueryItem("date_req", requested_date.toString("dd/MM/yyyy"))
        url.setQuery(query)

        self.load_button.setEnabled(False)
        self.rates_label.setText("Загрузка курса с сайта ЦБ РФ…")

        reply = self.network.get(QNetworkRequest(url))
        reply.setProperty("requested_date", requested_date.toString("dd.MM.yyyy"))
        reply.finished.connect(lambda: self.handle_rates_reply(reply))

        timeout = QTimer(reply)
        timeout.setSingleShot(True)
        timeout.timeout.connect(reply.abort)
        timeout.start(self.REQUEST_TIMEOUT_MS)

    def use_default_rates(self, message):
        """Восстанавливает базовые курсы после ошибки загрузки"""
        self.rub_per_usd = self.DEFAULT_RUB_PER_USD
        self.eur_per_usd = self.DEFAULT_RUB_PER_USD / self.DEFAULT_RUB_PER_EUR
        self.rates_label.setText(
            f"{message} Используется базовый курс: "
            f"1 $ = {self.DEFAULT_RUB_PER_USD:.2f} ₽; "
            f"1 € = {self.DEFAULT_RUB_PER_EUR:.2f} ₽."
        )
        self.update_from_dollars(self.dollars.value())

    def handle_rates_reply(self, reply):
        """Обрабатывает XML-ответ Банка России"""
        self.load_button.setEnabled(True)

        if reply.error() != QNetworkReply.NoError:
            if reply.error() == QNetworkReply.OperationCanceledError:
                error_message = "Не удалось загрузить курс: превышено время ожидания."
            else:
                error_message = f"Не удалось загрузить курс: {reply.errorString()}."
            self.use_default_rates(error_message)
            reply.deleteLater()
            return

        try:
            root = ET.fromstring(bytes(reply.readAll()))
            rates = {}
            for valute in root.findall("Valute"):
                code = valute.findtext("CharCode")
                nominal = int(valute.findtext("Nominal"))
                value = float(valute.findtext("Value").replace(",", "."))
                rates[code] = value / nominal

            rub_per_usd = rates["USD"]
            rub_per_eur = rates["EUR"]
        except (ET.ParseError, AttributeError, KeyError, TypeError, ValueError):
            self.use_default_rates(
                "ЦБ РФ вернул данные в неожиданном формате"
            )
            reply.deleteLater()
            return

        self.rub_per_usd = rub_per_usd
        self.eur_per_usd = rub_per_usd / rub_per_eur

        actual_date = root.attrib.get("Date", reply.property("requested_date"))
        self.show_rates(f"курс ЦБ РФ на {actual_date}")
        self.update_from_dollars(self.dollars.value())
        reply.deleteLater()

    @staticmethod
    def create_money_field(suffix):
        field = QDoubleSpinBox()
        field.setRange(0.00, 1_000_000_000.00)
        field.setDecimals(2)
        field.setSingleStep(1.00)
        field.setSuffix(suffix)
        field.setGroupSeparatorShown(True)
        return field

    def set_values(self, rubles, dollars, euros):
        """Обновляет поля, не вызывая их сигналы повторно"""
        blockers = (
            QSignalBlocker(self.rubles),
            QSignalBlocker(self.dollars),
            QSignalBlocker(self.euros),
        )
        self.rubles.setValue(rubles)
        self.dollars.setValue(dollars)
        self.euros.setValue(euros)
        del blockers

    def update_from_rubles(self, rubles):
        dollars = rubles / self.rub_per_usd
        euros = dollars * self.eur_per_usd
        self.set_values(rubles, dollars, euros)

    def update_from_dollars(self, dollars):
        rubles = dollars * self.rub_per_usd
        euros = dollars * self.eur_per_usd
        self.set_values(rubles, dollars, euros)

    def update_from_euros(self, euros):
        dollars = euros / self.eur_per_usd
        rubles = dollars * self.rub_per_usd
        self.set_values(rubles, dollars, euros)


def main():
    app = QApplication(sys.argv)
    window = CurrencyConverter()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
