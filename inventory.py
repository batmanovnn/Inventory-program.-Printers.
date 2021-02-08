from datetime import datetime, date, timedelta
import sys
from pprint import pprint

import simplejson as json

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMessageBox

import window


class App(QtWidgets.QMainWindow, window.Ui_mainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lineEdit_data_rem.hide()
        self.lineEdit_error.hide()  #
        self.lineEdit_phone.hide()  #
        self.radioButton_full.setChecked(True)
        self.start_table()  # loading initial table
        self.init_handlers()  # Initialization of Interface Elements
        self.printers = {}

    # Loading initial table
    def start_table(self):
        with open("data_file.json", "r") as read_file:
            load_printers = json.load(read_file)
            index = load_printers.keys()

        self.html_f(load_printers, index)

    # Initialization of Interface Elements
    def init_handlers(self):
        # Edit tables
        self.pushButton_append.clicked.connect(self.add_row)
        self.pushButton_remove.clicked.connect(self.del_row)
        # Data fields
        self.dateEdit_data_pay.setDate(QDate.currentDate())
        self.dateEdit_data_pay.dateChanged.connect(self.data_amort)
        self.spinBox_lifetime.valueChanged.connect(self.data_amort)
        # Type HTML-table
        self.radioButton_full.clicked.connect(self.set_text)
        self.radioButton_amort.clicked.connect(self.set_text)
        self.radioButton_state.clicked.connect(self.set_text)
        self.radioButton_hr.clicked.connect(self.set_text)
        # Interactive Search Fields
        self.comboBox.activated[int].connect(self.remont)
        self.comboBox_2.activated[int].connect(self.set_text)
        self.lineEdit_made.textChanged.connect(self.set_text)
        self.checkBox_made.clicked.connect(self.set_text)
        self.lineEdit_model.textChanged.connect(self.set_text)
        self.checkBox_model.clicked.connect(self.set_text)
        self.lineEdit_room.textChanged.connect(self.set_human)
    # def help_about_qt(self):
    #     QMessageBox.aboutQt(self, "about Qt")

    # Add a row in table
    def add_row(self):
        if self.radioButton_hr.isChecked():
            self.append_hr()
        else:
            self.append_printer()

    # Add a row in table
    def del_row(self):
        if self.radioButton_hr.isChecked():
            self.del_hr()
        else:
            self.del_printer()

    # automatic depreciation calculation
    def data_amort(self):
        data_amort = self.dateEdit_data_pay.date().addYears(int(self.spinBox_lifetime.text()))
        self.lineEdit_data_amort.setText(data_amort.toString("dd.MM.yyyy"))

    # Hide status fields "under repair"
    def remont(self, text):
        if self.comboBox.currentIndex() == 0 or self.comboBox.currentIndex() == 1:
            self.lineEdit_data_rem.hide()
            self.lineEdit_error.hide()
        else:
            self.lineEdit_data_rem.show()
            self.lineEdit_error.show()
        self.comboBox.activated[str].connect(self.set_text)

    # Displayed human
    def set_human(self):
        with open("data_h-r.json", "r") as hr_file:
            hr = json.load(hr_file)
        index = hr.keys()
        room = self.lineEdit_room.text()
        if room in index:
            self.lineEdit_human.setText(hr[room]['name'])

    # Updating the displayed table
    def set_text(self):
        if self.radioButton_hr.isChecked():
            self.lineEdit_phone.show()

            with open("data_h-r.json", "r") as hr_file:
                load_printers = json.load(hr_file)

            index_res = sorted(load_printers.keys())

        else:
            self.lineEdit_phone.hide()

            with open("data_file.json", "r") as read_file:
                load_printers = json.load(read_file)

            table_keys = sorted(load_printers.keys())
            index_type = []
            index_made = []
            index_model = []
            index_state = []

            for i in table_keys:
                if self.comboBox_2.currentIndex() == 0:
                    index_type.append(i)
                else:
                    tmp = load_printers[i]['type']
                    if tmp.find(self.comboBox_2.currentText()) != -1:
                        index_type.append(i)
                tmp = load_printers[i]['made']
                if self.checkBox_made.isChecked():
                    if tmp.find(self.lineEdit_made.text()) != -1:
                        index_made.append(i)
                else:
                    index_made.append(i)
                tmp = load_printers[i]['model']
                if self.checkBox_model.isChecked():
                    if tmp.find(self.lineEdit_model.text()) != -1:
                        index_model.append(i)
                else:
                    index_model.append(i)
                if self.comboBox.currentIndex() == 0:
                    index_state.append(i)
                else:
                    tmp = load_printers[i]['state']
                    if tmp.find(self.comboBox.currentText()) != -1:
                        index_state.append(i)

            index = [index_type] + [index_made] + [index_model] + [index_state]
            index_res = list(set.intersection(*map(set, index)))

        self.html_f(load_printers, index_res)

    # Adding a row to hr tables
    def append_hr(self):
        with open("data_h-r.json", "r") as read_file:
            hr = json.load(read_file)
        pprint(hr)

        index = sorted(hr.keys())
        if self.lineEdit_room in index:
            del hr[self.lineEdit_room.text()]

        if self.lineEdit_room.text() != "":
            hr.setdefault(self.lineEdit_room.text(),
                          {'name': self.lineEdit_human.text(),
                           'phone': self.lineEdit_phone.text()
                           }
                          )
        pprint(hr)
        with open("data_h-r.json", "w") as write_file:
            json.dump(hr, write_file)

        with open("data_h-r.json", "r") as read_file:
            hr = json.load(read_file)
        pprint(hr)

        self.set_text()

    # Adding a row to printers table
    def append_printer(self):
        self.textBrowser.clear()

        with open("data_file.json", "r") as read_file:
            printers = json.load(read_file)

        index = sorted(printers.keys())
        if self.lineEdit_ser_num.text() in index:
            del printers[self.lineEdit_ser_num.text()]

        if self.comboBox.currentIndex() == 0:
            self.comboBox.setCurrentIndex(1)
        if self.comboBox_2.currentIndex() == 0:
            self.comboBox_2.setCurrentIndex(1)
        if self.comboBox.currentIndex() != 2:
            self.lineEdit_data_rem.setText("")
            self.lineEdit_error.setText("")

        if self.lineEdit_ser_num.text() == "":
            printers.setdefault(self.lineEdit_ser_num.text(),
                                {'type': self.comboBox_2.currentText(),
                                 'made': self.lineEdit_made.text(),
                                 'model': self.lineEdit_model.text(),
                                 'data_pay': self.dateEdit_data_pay.text(),
                                 'lifetime': int(self.spinBox_lifetime.text()),
                                 'amort': self.lineEdit_data_amort.text(),
                                 'room': self.lineEdit_room.text(),
                                 'state': self.comboBox.currentText(),
                                 'data_rem': self.lineEdit_data_rem.text(),
                                 'error': self.lineEdit_error.text()
                                 }
                                )

        with open("data_file.json", "w") as write_file:
            json.dump(printers, write_file)

        self.set_text()

    # Removing a row from a printers table
    def del_printer(self):
        self.textBrowser.clear()

        with open("data_file.json", "r") as read_file:
            printers = json.load(read_file)

        index = printers.keys()
        if self.lineEdit_ser_num.text() in index:
            del printers[self.lineEdit_ser_num.text()]

        with open("data_file.json", "w") as write_file:
            json.dump(printers, write_file)

        self.set_text()

    # Removing a row from a hr table
    def del_hr(self):
        self.textBrowser.clear()

        with open("data_h-r.json", "r") as read_file:
            hr = json.load(read_file)

        index = hr.keys()
        if self.lineEdit_room.text() in index:
            del hr[self.lineEdit_room.text()]

        with open("data_h-r.json", "w") as write_file:
            json.dump(hr, write_file)

        self.set_text()

    # HTML table generation
    def html_f(self, table, index):
        with open("data_h-r.json", "r") as hr_file:
            hr = json.load(hr_file)

        # Generate a full table
        if self.radioButton_full.isChecked():
            with open('src/table_full.html') as f:
                table_top = f.read()
            table_full = f"{table_top}"

            index = [table.keys()] + [index]
            table_keys = list(set.intersection(*map(set, index)))

            table_keys = sorted(table_keys)

            for i in table_keys:
                room = str(table[i]['room'])
                gen = (
                    f"<tr>"
                    f"<td>{i}</td>"
                    f"<td>{table[i]['type']}</td>"
                    f"<td>{table[i]['made']}</td>"
                    f"<td>{table[i]['model']}</td>"
                    f"<td>{table[i]['data_pay']}</td>"
                    f"<td>{table[i]['lifetime']}</td>"
                    f"<td>{table[i]['amort']}</td>"
                    f"<td>{table[i]['room']}</td>"
                )
                if table[i]['room'] in hr.keys():
                    gen_h = f"<td>{hr[room]['name']}</td>"
                else:
                    gen_h = f"<td></td>"
                gen_2 = (
                    f"<td>{table[i]['state']}</td>"
                    f"<td>{table[i]['data_rem']}</td>"
                    f"<td>{table[i]['error']}</td>"
                    f"</tr>"
                )
                table_full = f"{table_full}{gen}{gen_h}{gen_2}"

        # Generate a table of amortization
        elif self.radioButton_amort.isChecked():
            print(f"amort-form")
            with open('src/table_amort.html') as f:
                table_top = f.read()
            table_full = f"{table_top}"

            index = [table.keys()] + [index]
            table_keys = list(set.intersection(*map(set, index)))

            table_keys = sorted(table_keys)

            for i in table_keys:
                gen_1 = (
                    f"<tr>"
                    f"<td>{i}</td>"
                    f"<td white-space = 'nowrap'>{table[i]['type']}</td>"
                    f"<td>{table[i]['made']}</td>"
                    f"<td>{table[i]['model']}</td>"
                    f"<td>{table[i]['data_pay']}</td>"
                    f"<td>{table[i]['lifetime']}</td>"
                )
                # Marker for field "amortization" (return gen_a)
                tmp = table[i]['amort']
                now = datetime.now()
                deadline = now + timedelta(30)
                if tmp == "":
                    gen_a = (
                        f"<td bgcolor='red'>{table[i]['amort']}</td>"
                    )
                else:
                    tmp = datetime.strptime(tmp, '%d.%m.%Y')
                    if tmp > deadline:
                        gen_a = (
                            f"<td>{table[i]['amort']}</td>"
                        )
                    else:
                        gen_a = (
                            f"<td bgcolor='red'>{table[i]['amort']}</td>"
                        )

                gen_2 = (
                    f"<td>{table[i]['state']}</td>"
                    f"</tr>"
                )
                table_full = f"{table_full}{gen_1}{gen_a}{gen_2}"

        # Generate a table of state
        elif self.radioButton_state.isChecked():
            with open('src/table_state.html') as f:
                table_top = f.read()
            table_full = f"{table_top}"

            index = [table.keys()] + [index]
            table_keys = list(set.intersection(*map(set, index)))

            table_keys = sorted(table_keys)

            for i in table_keys:
                gen = (
                    f"<tr>"
                    f"<td>{i}</td>"
                    f"<td>{table[i]['type']}</td>"
                    f"<td>{table[i]['made']}</td>"
                    f"<td>{table[i]['model']}</td>"
                    f"<td>{table[i]['room']}</td>"
                    f"<td>{table[i]['state']}</td>"
                    f"<td>{table[i]['data_rem']}</td>"
                    f"<td>{table[i]['error']}</td>"
                    f"</tr>"
                )
                table_full = f"{table_full}{gen}"

        # Generate a table of hr
        elif self.radioButton_hr.isChecked():
            with open('src/table_hr.html') as f:
                table_top = f.read()
            table_full = f"{table_top}"

            for i in index:
                gen = (
                    f"<tr>"
                    f"<td>{i}</td>"
                    f"<td>{hr[i]['name']}</td>"
                    f"<td>{hr[i]['phone']}</td>"
                )
                table_full = f"{table_full}{gen}"

        table_full = f"{table_full}</table></div></body></html>"

        self.textBrowser.setText(table_full)


def main():
    app = QtWidgets.QApplication(sys.argv)
    a = App()
    a.show()
    app.exec_()


if __name__ == '__main__':
    main()
