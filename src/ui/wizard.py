from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton

class ProjectWizard(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create New Project")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Add your wizard controls here...

        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.finish_wizard)
        layout.addWidget(self.finish_btn)

        self.setLayout(layout)

    def finish_wizard(self):
        # Placeholder for now.
        print("Project created successfully!")
        self.close()
