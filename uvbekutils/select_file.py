from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from pathlib import Path
from fnmatch import fnmatch
import sys


def select_file(title: str, start_dir: str, files_like: str, choices: list[str] = ["Select", "Cancel"], mode: str = "file", title2: str = "", show_hidden_button: bool = False, show_sort_button: bool = False) -> str | None:
    """
    Display a file/directory selection dialog.

    Args:
        title: Window title
        start_dir: Initial directory to display
        files_like: Wildcard pattern for filtering (e.g., "*.txt")
        choices: List of two button labels [select_label, cancel_label]
        mode: "file" (select files), "dir" (select directories), or "both"
        title2: Optional subtitle displayed below the window title
        show_hidden_button: Show checkbox to toggle hidden files (default False)
        show_sort_button: Show checkbox to toggle sort order (default False)

    Returns:
        Selected path as string, or None if cancelled
    """
    # Create application if needed
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    dialog = FileSelectDialog(title, start_dir, files_like, choices, mode, title2, show_hidden_button, show_sort_button)
    result = dialog.exec()

    if result == QDialog.Accepted:
        return dialog.selected_path
    return None


class FileSelectDialog(QDialog):
    def __init__(self, title: str, start_dir: str, files_like: str, choices: list[str], mode: str, title2: str = "", show_hidden_button: bool = False, show_sort_button: bool = False):
        super().__init__()
        self.current_dir = Path(start_dir).expanduser().resolve()
        self.files_like = files_like if files_like.strip() else "*"
        self.mode = mode
        self.title2 = title2
        self.selected_path = None
        self.item_paths = []
        self.show_hidden_button = show_hidden_button
        self.show_sort_button = show_sort_button

        self.setWindowTitle(title)
        self.setMinimumSize(750, 400)
        self.setup_ui(choices)
        self.populate_list()

    def setup_ui(self, choices: list[str]):
        layout = QVBoxLayout(self)

        # Optional subtitle
        if self.title2:
            title2_label = QLabel(self.title2)
            title2_label.setAlignment(Qt.AlignLeft)
            title2_label.setWordWrap(True)
            layout.addWidget(title2_label)

        # Current path label
        self.path_label = QLabel(str(self.current_dir))
        layout.addWidget(self.path_label)

        # Wildcard filter label
        filter_label = QLabel(f"Like: {self.files_like}")
        layout.addWidget(filter_label)

        # Sort alpha checkbox (default is sort by date modified)
        self.sort_alpha_cb = None
        if self.show_sort_button:
            self.sort_alpha_cb = QCheckBox("Sort alpha")
            self.sort_alpha_cb.setChecked(False)
            self.sort_alpha_cb.stateChanged.connect(self.on_sort_toggled)
            layout.addWidget(self.sort_alpha_cb)

        # Show hidden checkbox
        self.show_hidden_cb = None
        if self.show_hidden_button:
            self.show_hidden_cb = QCheckBox("Show hidden")
            self.show_hidden_cb.setChecked(False)
            self.show_hidden_cb.stateChanged.connect(self.on_hidden_toggled)
            layout.addWidget(self.show_hidden_cb)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_double_click)
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.select_btn = QPushButton(choices[0])
        self.select_btn.clicked.connect(self.on_select)
        self.select_btn.setEnabled(False)  # Disabled until valid selection
        button_layout.addWidget(self.select_btn)

        cancel_btn = QPushButton(choices[1])
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def on_sort_toggled(self, state):
        """Re-populate list when sort checkbox is toggled."""
        self.populate_list()

    def on_hidden_toggled(self, state):
        """Re-populate list when show hidden checkbox is toggled."""
        self.populate_list()

    def update_path_label(self):
        """Update path label with elided text and full path as tooltip."""
        prefix = "Current: "
        full_path = str(self.current_dir)
        self.path_label.setToolTip(full_path)

        # Calculate available width and elide text (accounting for prefix)
        metrics = QFontMetrics(self.path_label.font())
        prefix_width = metrics.horizontalAdvance(prefix)
        available_width = self.path_label.width() - prefix_width - 10  # Small margin
        elided = metrics.elidedText(full_path, Qt.ElideLeft, available_width)
        self.path_label.setText(prefix + elided)

    def resizeEvent(self, event):
        """Re-elide path when window is resized."""
        super().resizeEvent(event)
        self.update_path_label()

    def populate_list(self):
        self.list_widget.clear()
        self.item_paths.clear()
        self.select_btn.setEnabled(False)  # Reset button state

        self.update_path_label()

        # Add parent directory entry
        item = QListWidgetItem("[..] Parent Directory")
        self.list_widget.addItem(item)
        self.item_paths.append(("parent", str(self.current_dir.parent)))

        # Categorize entries
        dirs = []
        files = []
        show_hidden = self.show_hidden_cb.isChecked() if self.show_hidden_cb else False
        try:
            for entry in self.current_dir.iterdir():
                # Skip hidden files/dirs if checkbox unchecked
                if not show_hidden and entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    dirs.append(entry)
                elif self.mode != "dir":
                    files.append(entry)
        except PermissionError:
            return

        # Sort (alphabetically if checked, by date modified if unchecked)
        if self.sort_alpha_cb and self.sort_alpha_cb.isChecked():
            dirs.sort(key=lambda p: p.name.lower())
            files.sort(key=lambda p: p.name.lower())
        else:
            # Sort by modification time, newest first
            dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Add directories (always show all for navigation)
        for entry in dirs:
            if self.mode == "file":
                # In file mode, directories are for navigation only
                item = QListWidgetItem(f"[DIR] {entry.name}")
                self.list_widget.addItem(item)
                self.item_paths.append(("dir", str(entry)))
            elif fnmatch(entry.name.lower(), self.files_like.lower()):
                # Directory matches wildcard - selectable
                item = QListWidgetItem(f"[DIR] {entry.name}")
                self.list_widget.addItem(item)
                self.item_paths.append(("dir", str(entry)))
            else:
                # Directory doesn't match wildcard - navigation only
                item = QListWidgetItem(f"[dir] {entry.name}")
                self.list_widget.addItem(item)
                self.item_paths.append(("dir_nav", str(entry)))

        # Add files
        for entry in files:
            if fnmatch(entry.name.lower(), self.files_like.lower()):
                item = QListWidgetItem(f"     {entry.name}")
                self.list_widget.addItem(item)
                self.item_paths.append(("file", str(entry)))

    def on_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Enable/disable Select button based on whether current selection is valid."""
        if current is None:
            self.select_btn.setEnabled(False)
            return

        idx = self.list_widget.row(current)
        item_type, path = self.item_paths[idx]

        # Determine if this item is selectable
        is_selectable = False
        if item_type == "file":
            is_selectable = True
        elif item_type == "dir" and self.mode in ("dir", "both"):
            is_selectable = True

        self.select_btn.setEnabled(is_selectable)

    def on_double_click(self, item: QListWidgetItem):
        idx = self.list_widget.row(item)
        item_type, path = self.item_paths[idx]

        if item_type == "parent":
            self.current_dir = Path(path)
            self.populate_list()
        elif item_type in ("dir", "dir_nav"):
            # Both selectable and nav-only directories can be navigated into
            self.current_dir = Path(path)
            self.populate_list()
        elif item_type == "file":
            self.selected_path = path
            self.accept()

    def on_select(self):
        current_item = self.list_widget.currentItem()
        if current_item is None:
            self.selected_path = None
            self.reject()
            return

        idx = self.list_widget.row(current_item)
        item_type, path = self.item_paths[idx]

        if item_type == "parent":
            self.selected_path = None
        elif item_type == "dir":
            if self.mode in ("dir", "both"):
                self.selected_path = path
            else:
                self.selected_path = None
        elif item_type == "dir_nav":
            # Navigation-only directory - not selectable
            self.selected_path = None
        elif item_type == "file":
            self.selected_path = path

        if self.selected_path:
            self.accept()
        else:
            self.reject()


if __name__ == "__main__":
    selected = select_file(
        title="Select a Python File",
        start_dir="~/Downloads",
        files_like="*.csv",
        choices=["Select", "Cancel"],
        mode="file",  # file, dir or both
        title2="Select the latest user file that you can.  It should be the one you want that works just right.",
        show_hidden_button=False,
        show_sort_button=False
    )
    print(f"Selected: {selected}")

    selected = select_file(
        title="Select a Python File",
        start_dir="~/Downloads",
        files_like="*.csv",
        choices=["Select", "Cancel"],
        mode="file",  # file, dir or both
        title2="Select the latest user file that you can.  It should be the one you want that works just right.",
        show_hidden_button=True,
        show_sort_button=True
    )
    print(f"Selected: {selected}")
