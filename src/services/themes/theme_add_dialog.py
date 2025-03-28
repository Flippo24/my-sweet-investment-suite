from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QDialogButtonBox

class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Theme")
        self.setModal(True)

        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.author_input = QLineEdit()
        self.project_url_input = QLineEdit()
        self.theme_url_input = QLineEdit()
        self.file_path_input = QLineEdit()

        file_button = QPushButton("Browse")
        file_button.clicked.connect(self.browse_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(file_button)

        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Author:", self.author_input)
        self.form_layout.addRow("Project URL:", self.project_url_input)
        self.form_layout.addRow("Theme URL:", self.theme_url_input)
        self.form_layout.addRow("Local File:", file_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Theme JSON File", "", "JSON Files (*.json)")
        if file_path:
            self.file_path_input.setText(file_path)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "author": self.author_input.text(),
            "project_url": self.project_url_input.text(),
            "theme_url": self.theme_url_input.text(),
            "file_path": self.file_path_input.text()
        }
