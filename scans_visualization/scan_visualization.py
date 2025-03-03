from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkDICOMImageReader, vtkNIFTIImageReader
from vtkmodules.vtkInteractionImage import vtkImageViewer2
from vtkmodules.vtkRenderingCore import vtkActor2D, vtkRenderWindowInteractor, vtkTextMapper, vtkTextProperty
from vtkmodules.vtkImagingCore import vtkImageReslice, vtkImageShiftScale

from scans_visualization.custom_interaction import CustomInteractorStyle
from directory_utils.directory_handler import getting_files_directories_path


class ScansViewer:
    def __init__(self, file_directory, cross_sectional_orientation='Axial', file_format='nii'):
        """ """
        self.file_directory = file_directory
        self.file_format = file_format
        self.cross_sectional_orientation = cross_sectional_orientation  # New attribute for view orientation

        # Images
        self.images_data = {}
        self.image_viewer = vtkImageViewer2()
        self.slice_images = vtkImageReslice()

        # Text Actors
        self.slice_text_actor = vtkActor2D()
        self.usage_text_actor = vtkActor2D()
        self.cross_sectional_orientation_actor = vtkActor2D()
        self.modality_actor = vtkActor2D()

        # Interactions integrated
        self.interactor = vtkRenderWindowInteractor()
        self.colors = vtkNamedColors()

        self.setup_reader()
        self.setup_slice_image()
        self.setup_viewer()
        self.setup_text_labels()

        self.interactor_style = CustomInteractorStyle(self.image_viewer, self.cross_sectional_orientation,
                                                      self.slice_images, self.images_data, self.slice_text_actor)
        self.configure_interactor()

    def setup_reader(self):
        if self.file_format == 'nii':
            self.read_nii_files()
        elif self.file_format == 'dcm':
            self.read_dcm_files()
        else:
            print('File format not supported')

    def read_dcm_files(self):
        reader = vtkDICOMImageReader()
        reader.SetDirectoryName(self.file_directory)
        reader.Update()
        self.images_data['dcm'] = reader

    def read_nii_files(self):
        for modality, path in getting_files_directories_path(self.file_directory).items():
            reader = vtkNIFTIImageReader()
            reader.SetFileName(path)
            reader.Update()
            self.images_data[modality] = reader

    def setup_slice_image(self):
        self.normalize_slice_images()
        if self.file_format == 'nii':
            self.slice_images.SetInputData(self.images_data['flair'])
        else:
            self.slice_images.SetInputData(self.images_data['dcm'])
        self.slice_images.SetOutputSpacing(1, 1, 1)
        self.slice_images_by_cross_sectional_orientation()

    def normalize_slice_images(self):
        for modality in self.images_data.keys():
            image_data = self.images_data[modality].GetOutput()
            shiftScale = vtkImageShiftScale()   # noqa
            min_value, max_value = image_data.GetScalarRange()
            shiftScale.SetInputData(image_data)
            shiftScale.SetShift(-min_value)
            shiftScale.SetScale(255.0 / (max_value - min_value))
            shiftScale.SetOutputScalarTypeToUnsignedChar()
            shiftScale.Update()
            self.images_data[modality] = shiftScale.GetOutput()

    def slice_images_by_cross_sectional_orientation(self):
        # Default is axial
        if self.cross_sectional_orientation == 'Coronal':
            self.slice_images.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, -1, 0)
        elif self.cross_sectional_orientation == 'Sagittal':
            self.slice_images.SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0)
        elif self.cross_sectional_orientation == 'Axial':
            self.slice_images.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)

    def setup_viewer(self):
        self.image_viewer.SetInputConnection(self.slice_images.GetOutputPort())

    def setup_text_labels(self):
        self.setup_slice_text_actor()
        self.setup_usage_text_actor()
        self.setup_cross_sectional_orientation_actor()
        self.setup_modality_actor()

    def setup_slice_text_actor(self):
        self.slice_text_actor = self.create_text_actor("", 15, 10, 20, align_bottom=True)

    def setup_usage_text_actor(self):
        self.usage_text_actor = self.create_text_actor(
            "- Slice with mouse wheel or Up/Down-Key"
            "\n- Zoom with pressed right mouse button while dragging",
            0.05, 0.95, 14, normalized=True)

    def setup_cross_sectional_orientation_actor(self):
        self.cross_sectional_orientation_actor = self.create_text_actor(
            "- Press 'a' to see Axial"
            "\n- Press 's' to see Sagittal"
            "\n- Press 'c' to see Coronal",
            0.67, 0.95, 14, normalized=True)

    def setup_modality_actor(self):
        if self.file_format == 'nii':
            self.modality_actor = self.create_text_actor(
                "- '1' Flair"
                "\n- '2' T1"
                "\n- '3' T1ce"
                "\n- '4' T2",
                0.02, 0.85, 14, normalized=True)
        else:
            pass

    def create_text_actor(self, text, x, y, font_size, align_bottom=False, normalized=False):   # noqa
        text_prop = vtkTextProperty()
        text_prop.SetFontFamilyToCourier()
        text_prop.SetFontSize(font_size)
        text_prop.SetVerticalJustificationToBottom() if align_bottom else text_prop.SetVerticalJustificationToTop()
        text_prop.SetJustificationToLeft()
        text_mapper = vtkTextMapper()
        text_mapper.SetInput(text)
        text_mapper.SetTextProperty(text_prop)
        text_actor = vtkActor2D()
        text_actor.SetMapper(text_mapper)
        if normalized:
            text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        text_actor.SetPosition(x, y)
        return text_actor

    def configure_interactor(self):
        self.image_viewer.SetupInteractor(self.interactor)
        self.interactor.SetInteractorStyle(self.interactor_style)

    def add_text_labels_actors_to_render(self):
        self.image_viewer.GetRenderer().AddActor2D(self.slice_text_actor)
        self.image_viewer.GetRenderer().AddActor2D(self.usage_text_actor)
        self.image_viewer.GetRenderer().AddActor2D(self.cross_sectional_orientation_actor)
        if self.file_format == 'nii':
            self.image_viewer.GetRenderer().AddActor2D(self.modality_actor)
        else:
            pass

    def render(self):
        self.add_text_labels_actors_to_render()
        self.image_viewer.Render()
        self.image_viewer.GetRenderer().ResetCamera()
        self.image_viewer.GetRenderer().SetBackground(self.colors.GetColor3d('Black'))
        self.image_viewer.GetRenderWindow().SetSize(700, 700)
        self.image_viewer.GetRenderWindow().SetWindowName('MRI Visualizer -' + self.file_directory)
        self.interactor.Start()
