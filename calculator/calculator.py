from PySide6 import QtWidgets, QtGui


class CalculatorWidget(QtWidgets.QWidget):
    """calculator windows"""

    def __init__(self) -> None:
        """bulid function"""

        super().__init__() 

        self.output = QtWidgets.QTextEdit()
        self.input = QtWidgets.QLineEdit()
        self.input.returnPressed.connect(self.calculate)

        calculate_button = QtWidgets.QPushButton("calculate")
        calculate_button.clicked.connect(self.calculate)
        calculate_button.setIcon(QtGui.QIcon("/home/ocean/vnpy/calculator/calculate.ico"))

        clear_button = QtWidgets.QPushButton("clean")
        clear_button.clicked.connect(self.input.clear)
        clear_button.setIcon(QtGui.QIcon("/home/ocean/vnpy/calculator/clean.ico"))

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.output)
        vbox.addWidget(self.input)
        vbox.addWidget(calculate_button)
        vbox.addWidget(clear_button)
        self.setLayout(vbox)

    def calculate(self) -> None:
        """begin calculate"""
        text: str = self.input.text()

        try:
            result = eval(text)
            self.output.append(f"{text} = {result}")
        except Exception:
            self.output.append(f"{text} expression error")


if __name__ == "__main__":
    qapp = QtWidgets.QApplication([])

    widget = CalculatorWidget()
    widget.show()

    qapp.exec()