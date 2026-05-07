"""A PySide6-based module that mimics pyautogui dialog functions.

This module provides lightweight replacements for pyautogui's dialog
functions (``alert`` and ``confirm``) using PySide6/Qt widgets. Dialogs
are displayed as always-on-top windows with word-wrapped messages.

Functions:
    alert: Display an alert dialog with an Ok button.
    alert_with_file_link: Display an alert dialog with an Ok button and a clickable file link.
    confirm: Display a confirmation dialog with custom buttons.
    confirm_with_file_link: Display a confirmation dialog with custom buttons and a clickable file link.

Example::

    from uvbekutils.pyautobek import alert, confirm

    alert("Operation complete.", "Status")
    choice = confirm("Save changes?", "Confirm", ["Yes", "No"])
"""

import subprocess
import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
)

from PySide6.QtCore import Qt


def _get_app():
    """Get existing QApplication or create one if needed."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def alert(msg, title="Alert"):
    """Display an alert dialog with a message and an Ok button.

    Creates a modal, always-on-top Qt dialog containing the message
    and a single Ok button. The dialog blocks until the user clicks Ok.

    Args:
        msg (str): The message to display in the dialog.
        title (str): The title of the dialog window. Defaults to "Alert".

    Example::

        alert("File saved successfully.", "Status")
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


def alert_with_file_link(msg, filepath, title="Alert"):
    """Display an alert dialog with a message, a clickable file link, and an Ok button.

    Like ``alert()``, but adds a clickable hyperlink below the message that
    opens ``filepath`` in its default application (e.g. Preview for PDF).

    Args:
        msg (str): The message to display in the dialog.
        filepath (str | Path): Path to a file; displayed as a clickable link.
        title (str): The title of the dialog window. Defaults to "Alert".

    Example::

        alert_with_file_link("Errors found.", "/output/error.pdf", "Error")
    """
    app = _get_app()

    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

    layout = QVBoxLayout()

    label = QLabel(msg)
    label.setWordWrap(True)
    layout.addWidget(label)

    link_label = QLabel(f'<a href="{filepath}">{filepath}</a>')
    link_label.setOpenExternalLinks(False)
    link_label.linkActivated.connect(lambda url: subprocess.run(['open', url]))
    layout.addWidget(link_label)

    button_layout = QHBoxLayout()
    button_layout.addStretch()

    ok_button = QPushButton("Ok")
    ok_button.clicked.connect(dialog.accept)
    button_layout.addWidget(ok_button)

    button_layout.addStretch()
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec()


def confirm_with_file_link(msg, filepath, title="Confirm", buttons=None, close_on_link_click=False):
    """Display a confirmation dialog with a message, a clickable file link, and custom buttons.

    Like ``confirm()``, but adds a clickable hyperlink below the message that
    opens ``filepath`` in its default application.

    Args:
        msg (str): The message to display in the dialog.
        filepath (str | Path): Path to a file; displayed as a clickable link.
        title (str): The title of the dialog window. Defaults to "Confirm".
        buttons (list[str] | None): Button labels. Defaults to ["Ok", "Cancel"].
        close_on_link_click (bool): When True, clicking the link both opens
            the file/URL **and** closes the dialog. Use this for end-user
            scripts where the dialog is just a launcher and would otherwise
            be left buried behind the opened browser/app. Defaults to False
            (preserves existing behavior — popup stays open after click).

    Returns:
        str: The lowercase text of the clicked button. If
        ``close_on_link_click=True`` and the user dismissed the dialog by
        clicking the link, returns ``""``.

    Example::

        choice = confirm_with_file_link("Errors found. Upload anyway?", "/output/error.pdf",
                                        "Confirm Upload", ["Yes", "No"])
        if choice == "yes":
            upload()
    """
    if buttons is None:
        buttons = ["Ok", "Cancel"]

    app = _get_app()

    dialog = QDialog()
    dialog.setWindowTitle(title)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

    result = [None]

    layout = QVBoxLayout()

    label = QLabel(msg)
    label.setWordWrap(True)
    layout.addWidget(label)

    link_label = QLabel(f'<a href="{filepath}">{filepath}</a>')
    link_label.setOpenExternalLinks(False)
    if close_on_link_click:
        link_label.linkActivated.connect(
            lambda url: (subprocess.run(['open', url]), dialog.accept())
        )
    else:
        link_label.linkActivated.connect(lambda url: subprocess.run(['open', url]))
    layout.addWidget(link_label)

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

    return result[0].lower() if result[0] is not None else ""


def confirm(msg, title="Confirm", buttons=None):
    """Display a confirmation dialog with custom buttons.

    Creates a modal, always-on-top Qt dialog containing the message
    and a row of buttons. The dialog blocks until the user clicks one
    of the buttons.

    Args:
        msg (str): The message to display in the dialog.
        title (str): The title of the dialog window. Defaults to "Confirm".
        buttons (list[str] | None): A list of strings for button labels.
            Defaults to ``["Ok", "Cancel"]`` if not provided.

    Returns:
        str: The lowercase text of the clicked button.

    Example::

        choice = confirm("Save changes?", "Confirm", ["Yes", "No"])
        if choice == "yes":
            save()
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
    label.setContentsMargins(4, 4, 4, 4)

    scroll = QScrollArea()
    scroll.setWidget(label)
    scroll.setWidgetResizable(True)
    scroll.setMinimumWidth(500)
    scroll.setMaximumHeight(700)
    layout.addWidget(scroll)

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
