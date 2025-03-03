from PyQt5.QtWidgets import (QWidget, QGridLayout, QTreeView, QFileSystemModel,
                             QLabel, QComboBox, QPushButton)
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QFont

from directory_utils.directory_handler import (is_not_directory, count_dcm_files, count_nii_files,
                                               getting_parent_directory)
from scans_visualization.scan_visualization import ScansViewer


class ScansExplorer(QWidget):
    def __init__(self, dataset_directory="./datasets"):
        super().__init__()  # noqa
        self.datasets_directory = dataset_directory
        self.files_directory = ''
        self.files_format = ''

        self.layout = QGridLayout()
        self.model = QFileSystemModel() # noqa
        self.tree_view = QTreeView()  # noqa
        self.info_label = QLabel()
        self.request_file_label = QLabel('Choose a folder')
        self.request_modality_label = QLabel('Choose sectional orientation')
        self.modality_combobox = QComboBox()    # noqa
        self.show_scans_button = QPushButton()

        self.setup_file_system_model()
        self.setup_tree_view()
        self.setup_modality_combobox()
        self.setup_show_scans_button()
        self.setup_layout()
        self.setup_window()

    def setup_file_system_model(self):
        self.model.setRootPath(self.datasets_directory)

    def setup_tree_view(self):
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.datasets_directory))
        self.tree_view.clicked.connect(self.folder_selected)  # noqa

    def folder_selected(self, index: QModelIndex):
        self.files_directory = self.model.filePath(index)
        if is_not_directory(self.files_directory):
            self.files_directory = getting_parent_directory(self.files_directory)
        self.update_label_info()

    def update_label_info(self):
        dicom_files_count = count_dcm_files(self.files_directory)
        nifti_files_count = count_nii_files(self.files_directory)

        if self.there_are_files(dicom_files_count):
            info = f"📂 {self.files_directory}\n📸 {dicom_files_count} DICOM files"
            self.files_format = 'dcm'
            self.update_show_scans_button(enabled=True)
        elif self.there_are_files(nifti_files_count):
            info = f"📂 {self.files_directory}\n🧠 {nifti_files_count} NIfTI files"
            self.files_format = 'nii'
            self.update_show_scans_button(enabled=True)
        else:
            info = f"📂 {self.files_directory}\n⚠ There are not DICOM or NIfTI files"
            self.files_format = ''
            self.update_show_scans_button(enabled=False)
        self.info_label.setText(info)

    @staticmethod
    def there_are_files(files_count):
        return True if files_count > 0 else False

    def setup_modality_combobox(self):
        self.modality_combobox.addItem('Axial')
        self.modality_combobox.addItem('Coronal')
        self.modality_combobox.addItem('Sagittal')

    def setup_show_scans_button(self):
        self.show_scans_button.setText('Show scans')
        self.show_scans_button.setEnabled(False)
        self.show_scans_button.clicked.connect(self.load_scans_visualizer)  # noqa

    def update_show_scans_button(self, enabled=False):
        self.show_scans_button.setEnabled(enabled)

    def load_scans_visualizer(self):
        print(f"Loading scans from {self.files_directory}")
        viewer = ScansViewer(file_directory=self.files_directory,
                             cross_sectional_orientation=self.modality_combobox.currentText(),
                             file_format=self.files_format)
        viewer.render()

    def setup_layout(self):
        self.layout.addWidget(self.request_file_label, 0, 0, 1, 10)
        self.layout.addWidget(self.tree_view, 1, 0, 8, 9)
        self.layout.addWidget(self.info_label, 10, 0, 1, 10)

        self.layout.addWidget(self.request_modality_label, 1, 9, 1, 1)
        self.layout.addWidget(self.modality_combobox, 2, 9, 1, 1)
        self.layout.addWidget(self.show_scans_button, 3, 9, 1, 1)
        self.setLayout(self.layout)

    def setup_window(self):
        self.setWindowTitle("Explore files")
        self.setGeometry(100, 100, 900, 500)
        self.setFont(QFont('Arial', 10))
