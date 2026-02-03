
def list_pick(lst, title='', msg='', select_mode='single', pre_select=False, allow_none=False):
    """Select items from a list using checkboxes or radio buttons.

    Args:
        lst: list of text items to select from
        title: title displayed at the top of the dialog
        msg: message displayed below the title
        select_mode: 'single' for radio buttons (one choice), 'multiple' for checkboxes (many choices)
        pre_select: if True, the first item starts selected; if False, nothing is selected
        allow_none: if False, user must pick at least one value or cancel; if True, OK with no selection returns ['']

    Returns:
        list of selected values, [''] if OK with no selections (allow_none=True), or None if cancelled
    """

    import sys
    from PySide6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout,
        QCheckBox, QRadioButton, QButtonGroup, QPushButton,
        QLabel, QScrollArea, QWidget, QMessageBox,
    )
    from PySide6.QtCore import Qt

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    class ListPickDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(title)
            self.setMinimumWidth(350)
            self.result_value = None
            self.is_multiple = select_mode == 'multiple'
            self.item_widgets = []
            self.radio_group = None

            main_layout = QVBoxLayout(self)

            # message label
            if msg:
                msg_label = QLabel(msg)
                msg_label.setStyleSheet("font-size: 14px;")
                main_layout.addWidget(msg_label)

            # mode status label
            if self.is_multiple:
                self.mode_status = QLabel("Multiple values allowed")
            else:
                self.mode_status = QLabel("Only a single value allowed")
            main_layout.addWidget(self.mode_status)

            # scroll area for list items
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            self.list_container = QWidget()
            self.list_layout = QVBoxLayout(self.list_container)
            scroll.setWidget(self.list_container)
            main_layout.addWidget(scroll)

            # action buttons
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("OK")
            cancel_btn = QPushButton("Cancel")
            ok_btn.clicked.connect(self.on_ok)
            cancel_btn.clicked.connect(self.on_cancel)
            btn_layout.addWidget(ok_btn)
            if allow_none:
                clear_btn = QPushButton("Clear All")
                clear_btn.clicked.connect(self.on_clear)
                btn_layout.addWidget(clear_btn)
            btn_layout.addWidget(cancel_btn)
            main_layout.addLayout(btn_layout)

            # build the list based on select_mode
            if self.is_multiple:
                self.build_checkbox_list()
            else:
                self.build_radio_list()

        def build_radio_list(self):
            self.clear_list()
            self.radio_group = QButtonGroup(self)
            for i, item in enumerate(lst):
                rb = QRadioButton(str(item))
                if pre_select and i == 0:
                    rb.setChecked(True)
                self.radio_group.addButton(rb)
                self.list_layout.addWidget(rb)
                self.item_widgets.append(rb)
            self.list_layout.addStretch()

        def build_checkbox_list(self, selected_indices=None):
            self.clear_list()
            self.radio_group = None
            if selected_indices is None:
                selected_indices = set()
            for i, item in enumerate(lst):
                cb = QCheckBox(str(item))
                if i in selected_indices:
                    cb.setChecked(True)
                elif pre_select and i == 0 and not selected_indices:
                    cb.setChecked(True)
                self.list_layout.addWidget(cb)
                self.item_widgets.append(cb)
            self.list_layout.addStretch()

        def clear_list(self):
            for w in self.item_widgets:
                self.list_layout.removeWidget(w)
                w.deleteLater()
            self.item_widgets.clear()
            # remove stretch if present
            while self.list_layout.count():
                item = self.list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        def on_ok(self):
            selected = [lst[i] for i in range(len(lst)) if self.item_widgets[i].isChecked()]
            if not selected and not allow_none:
                QMessageBox.warning(self, title, "Please select at least one value.")
                return
            self.result_value = selected if selected else ['']
            self.accept()

        def on_clear(self):
            if self.radio_group:
                self.radio_group.setExclusive(False)
            for w in self.item_widgets:
                w.setChecked(False)
            if self.radio_group:
                self.radio_group.setExclusive(True)

        def on_cancel(self):
            self.result_value = None
            self.reject()

    dialog = ListPickDialog()
    dialog.exec()
    return dialog.result_value


if __name__ == '__main__':

    ll = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']

    # return non list if signle mode
    selected = list_pick(ll, title='Pick Gift', msg='Choose the gift you want to seend to people',
                         select_mode='single', pre_select=False, )[0]
    print(f"{selected=}")


    selected = list_pick(ll, title='Pick Gift', msg='Choose the gift you want to seend to people',
                         select_mode='single', pre_select=False, allow_none=True)
    print(f"{selected=}")

    selected = list_pick(ll, title='Pick Gifts', msg='Choose the gifts you wish to buy',
                         select_mode='multiple', pre_select=True)
    print(f"{selected=}")

    selected = list_pick(ll, title='Pick Gifts', msg='Choose the gifts you wish to buy',
                         select_mode='multiple', pre_select=True, allow_none=True)
    print(f"{selected=}")
