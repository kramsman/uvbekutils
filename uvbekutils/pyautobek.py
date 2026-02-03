"""
pyautobek - A PySide6-based module that mimics pyautogui dialog functions.
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from PySide6.QtCore import Qt


def _get_app():
    """Get existing QApplication or create one if needed."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def alert(msg, title="Alert"):
    """
    Display an alert dialog with a message and an Ok button.

    Parameters:
        msg (str): The message to display in the dialog.
        title (str): The title of the dialog window.
    """
    app = _get_app()

    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

    layout = QVBoxLayout()

    label = QLabel(msg)
    label.setWordWrap(True)
    layout.addWidget(label)

    button_layout = QHBoxLayout()
    button_layout.addStretch()

    ok_button = QPushButton("Ok")
    ok_button.clicked.connect(dialog.accept)
    button_layout.addWidget(ok_button)

    button_layout.addStretch()
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec()


def confirm(msg, title="Confirm", buttons=None):
    """
    Display a confirmation dialog with custom buttons.

    Parameters:
        msg (str): The message to display in the dialog.
        title (str): The title of the dialog window.
        buttons (list): A list of strings for button labels.
                       Defaults to ["Ok", "Cancel"] if not provided.

    Returns:
        str: The text of the clicked button.
    """
    if buttons is None:
        buttons = ["Ok", "Cancel"]

    app = _get_app()

    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

    result = [None]  # Use list to allow modification in nested function

    layout = QVBoxLayout()

    label = QLabel(msg)
    label.setWordWrap(True)
    layout.addWidget(label)

    button_layout = QHBoxLayout()
    button_layout.addStretch()

    def make_handler(button_text):
        def handler():
            result[0] = button_text
            dialog.accept()
        return handler

    for button_text in buttons:
        btn = QPushButton(button_text)
        btn.clicked.connect(make_handler(button_text))
        button_layout.addWidget(btn)

    button_layout.addStretch()
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec()

    return result[0].lower()


if __name__ == "__main__":
    # Test the functions
    alert("This is a test alert message.", "Test Alert")

    choice = confirm("Do you want to proceed?", "Confirm Action", ["Yes", "No", "Maybe"])
    print(f"You clicked: {choice}")
