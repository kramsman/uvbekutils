
def list_pick(lst, title='', msg='', pre_select=False):
    """Select items from a list using checkboxes or radio buttons.

    Args:
        lst: list of text items to select from
        title: title displayed at the top of the dialog
        msg: message displayed below the title
        pre_select: if True, the first item starts selected; if False, nothing is selected

    Returns:
        list of selected values, or None if cancelled
    """

    import sys
    from PySide6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout,
        QCheckBox, QRadioButton, QButtonGroup, QPushButton,
        QLabel, QScrollArea, QWidget,
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
            self.is_multiple = False
            self.item_widgets = []
            self.radio_group = None

            main_layout = QVBoxLayout(self)

            # message label
            if msg:
                msg_label = QLabel(msg)
                msg_label.setStyleSheet("font-size: 14px;")
                main_layout.addWidget(msg_label)

            # mode toggle
            self.mode_toggle = QCheckBox("Toggle to allow multiple values ")
            self.mode_toggle.setChecked(False)
            self.mode_toggle.toggled.connect(self.on_mode_toggled)
            main_layout.addWidget(self.mode_toggle)

            # mode status label
            self.mode_status = QLabel("- Currently only a single value allowed")
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
            btn_layout.addWidget(cancel_btn)
            main_layout.addLayout(btn_layout)

            # build the list in single (radio) mode
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

        def get_selected_indices(self):
            selected = set()
            for i, w in enumerate(self.item_widgets):
                if w.isChecked():
                    selected.add(i)
            return selected

        def on_mode_toggled(self, checked):
            selected = self.get_selected_indices()
            self.is_multiple = checked
            if checked:
                self.mode_toggle.setText("Toggle to allow only a single value ")
                self.mode_status.setText("- Currently multiple values allowed")
                self.build_checkbox_list(selected)
            else:
                self.mode_toggle.setText("Toggle to allow multiple values ")
                self.mode_status.setText("- Currently only a single value allowed")
                # keep only first selected when switching to single
                first_selected = min(selected) if selected else None
                self.build_radio_list()
                if first_selected is not None:
                    self.item_widgets[first_selected].setChecked(True)

        def on_ok(self):
            selected = [lst[i] for i in range(len(lst)) if self.item_widgets[i].isChecked()]
            self.result_value = selected
            self.accept()

        def on_cancel(self):
            self.result_value = None
            self.reject()

    dialog = ListPickDialog()
    dialog.exec()
    return dialog.result_value


if __name__ == '__main__':

    ll = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
    selected = list_pick(ll, title='Pick Items', msg='Choose your items', pre_select=False)
    print(f"{selected=}")
    selected = list_pick(ll, title='Pick Items', msg='Pre-Selected Example', pre_select=True)
    print(f"{selected=}")
