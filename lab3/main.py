import sys
from pathlib import Path

from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


CONNECTION_NAME = "lab3_sqlite_connection"


class QueryDialog(QDialog):
    """Модальное окно для выполнения произвольного SQL-запроса."""

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.model = QSqlQueryModel(self)

        self.setWindowTitle("Произвольный SQL-запрос")
        self.resize(760, 500)

        self.editor = QPlainTextEdit("SELECT * FROM sqlite_master;")
        self.editor.setPlaceholderText("Введите SQL-запрос")
        self.editor.setTabChangesFocus(True)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        self.message = QLabel()
        self.message.setWordWrap(True)

        buttons = QDialogButtonBox()
        execute_button = buttons.addButton("Выполнить", QDialogButtonBox.AcceptRole)
        close_button = buttons.addButton(QDialogButtonBox.Close)
        execute_button.clicked.connect(self.execute_query)
        close_button.clicked.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("SQL-запрос:"))
        layout.addWidget(self.editor)
        layout.addWidget(self.message)
        layout.addWidget(self.table, stretch=1)
        layout.addWidget(buttons)

    def execute_query(self):
        query = self.editor.toPlainText().strip()
        if not query:
            self.message.setText("Введите запрос.")
            return

        self.model.setQuery(query, self.database)
        error = self.model.lastError()
        if error.isValid():
            self.message.setText(f"Ошибка: {error.text()}")
            self.message.setStyleSheet("color: #b00020;")
            return

        self.message.setText(
            f"Запрос выполнен. Строк в результате: {self.model.rowCount()}."
        )
        self.message.setStyleSheet("color: #237a3b;")
        self.table.resizeColumnsToContents()


class DatabaseViewer(QMainWindow):
    """Просмотрщик структуры SQLite-базы данных."""

    MASTER_COLUMNS = ("type", "name", "tbl_name", "rootpage", "sql")

    def __init__(self):
        super().__init__()
        self.database = None

        self.setWindowTitle("Лабораторная работа №3 — SQLite")
        self.resize(960, 650)

        self._create_menu()
        self._create_interface()
        self._set_connected(False)
        self.statusBar().showMessage("База данных не подключена")

    def _create_menu(self):
        database_menu = self.menuBar().addMenu("База данных")

        self.connect_action = QAction("Set connection…", self)
        self.connect_action.setStatusTip("Выбрать файл SQLite и открыть соединение")
        self.connect_action.triggered.connect(self.set_connection)
        database_menu.addAction(self.connect_action)

        self.close_action = QAction("Close connection", self)
        self.close_action.setStatusTip("Закрыть соединение и очистить результаты")
        self.close_action.triggered.connect(self.close_connection)
        database_menu.addAction(self.close_action)

        database_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        database_menu.addAction(exit_action)

        query_menu = self.menuBar().addMenu("Запрос")
        self.custom_query_action = QAction("Выполнить SQL…", self)
        self.custom_query_action.triggered.connect(self.open_query_dialog)
        query_menu.addAction(self.custom_query_action)

    def _create_interface(self):
        self.names_button = QPushButton("Имена объектов (Tab 2)")
        self.names_button.clicked.connect(
            lambda: self.run_query(
                "SELECT name FROM sqlite_master ORDER BY name", 1
            )
        )

        self.column_combo = QComboBox()
        self.column_combo.addItem("Выберите колонку…", None)
        for column in self.MASTER_COLUMNS:
            self.column_combo.addItem(column, column)
        self.column_combo.currentIndexChanged.connect(self.show_selected_column)

        self.tables_button = QPushButton("Таблицы (Tab 4)")
        self.tables_button.clicked.connect(
            lambda: self.run_query(
                "SELECT name, rootpage, sql FROM sqlite_master "
                "WHERE type = 'table' ORDER BY name",
                3,
            )
        )

        self.other_objects_button = QPushButton("Индексы и представления (Tab 5)")
        self.other_objects_button.clicked.connect(
            lambda: self.run_query(
                "SELECT type, name, tbl_name, sql FROM sqlite_master "
                "WHERE type IN ('index', 'view', 'trigger') ORDER BY type, name",
                4,
            )
        )

        controls = QGridLayout()
        controls.setHorizontalSpacing(18)
        controls.setVerticalSpacing(12)
        controls.addWidget(self.names_button, 0, 0)
        controls.addWidget(QLabel("Колонка sqlite_master:"), 0, 1)
        controls.addWidget(self.column_combo, 0, 2)
        controls.addWidget(self.tables_button, 1, 0)
        controls.addWidget(self.other_objects_button, 1, 2)
        controls.setColumnStretch(1, 1)

        self.tabs = QTabWidget()
        self.tables = []
        tab_names = (
            "Tab 1 — sqlite_master",
            "Tab 2 — имена",
            "Tab 3 — колонка",
            "Tab 4 — таблицы",
            "Tab 5 — другие объекты",
        )
        for name in tab_names:
            table = QTableView()
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.setSelectionBehavior(QTableView.SelectRows)
            self.tables.append(table)
            self.tabs.addTab(table, name)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)
        layout.addLayout(controls)
        layout.addWidget(self.tabs, stretch=1)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _set_connected(self, connected):
        self.close_action.setEnabled(connected)
        self.custom_query_action.setEnabled(connected)
        self.names_button.setEnabled(connected)
        self.column_combo.setEnabled(connected)
        self.tables_button.setEnabled(connected)
        self.other_objects_button.setEnabled(connected)

    def set_connection(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите базу данных SQLite",
            str(Path.home()),
            "SQLite database (*.db *.sqlite *.sqlite3);;Все файлы (*)",
        )
        if not file_name:
            return

        self.close_connection()
        self.database = QSqlDatabase.addDatabase("QSQLITE", CONNECTION_NAME)
        self.database.setDatabaseName(file_name)

        if not self.database.open():
            error_text = self.database.lastError().text()
            self._remove_database()
            QMessageBox.critical(
                self, "Ошибка подключения", f"Не удалось открыть базу данных:\n{error_text}"
            )
            return

        self._set_connected(True)
        self.statusBar().showMessage(f"Подключено: {file_name}")
        self.run_query("SELECT * FROM sqlite_master", 0)

    def run_query(self, query, tab_index):
        if self.database is None or not self.database.isOpen():
            QMessageBox.warning(self, "Нет подключения", "Сначала подключите базу данных.")
            return

        model = QSqlQueryModel(self)
        model.setQuery(query, self.database)
        error = model.lastError()
        if error.isValid():
            model.deleteLater()
            QMessageBox.critical(self, "Ошибка SQL", error.text())
            return

        old_model = self.tables[tab_index].model()
        self.tables[tab_index].setModel(model)
        self.tables[tab_index].resizeColumnsToContents()
        if old_model is not None:
            old_model.deleteLater()

        self.tabs.setCurrentIndex(tab_index)
        self.statusBar().showMessage(
            f"Запрос выполнен: {model.rowCount()} строк", 5000
        )

    def show_selected_column(self, index):
        column = self.column_combo.itemData(index)
        if column is None:
            return
        # Имя берётся только из заранее заданного списка MASTER_COLUMNS.
        self.run_query(
            f'SELECT "{column}" FROM sqlite_master ORDER BY "{column}"', 2
        )

    def open_query_dialog(self):
        if self.database is not None and self.database.isOpen():
            QueryDialog(self.database, self).exec_()

    def clear_results(self):
        for table in self.tables:
            model = table.model()
            table.setModel(None)
            if model is not None:
                model.clear()
                model.deleteLater()
        self.column_combo.setCurrentIndex(0)

    def _remove_database(self):
        if self.database is not None:
            if self.database.isOpen():
                self.database.close()
            self.database = None
        if QSqlDatabase.contains(CONNECTION_NAME):
            QSqlDatabase.removeDatabase(CONNECTION_NAME)

    def close_connection(self):
        self.clear_results()
        self._remove_database()
        self._set_connected(False)
        self.statusBar().showMessage("База данных не подключена")

    def closeEvent(self, event):
        self.close_connection()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
