import vtkmodules.all as vtk


class CustomInteractorStyle(vtk.vtkInteractorStyleImage):
    def __init__(self, image_viewer, cross_sectional_orientation, slice_images, images_data, status_actor):
        super().__init__()
        self.AddObserver('MouseWheelForwardEvent', self.move_slice_forward) # noqa
        self.AddObserver('MouseWheelBackwardEvent', self.move_slice_backward)   # noqa
        self.AddObserver('KeyPressEvent', self.key_press_event) # noqa
        self.image_viewer = image_viewer
        self.cross_sectional_orientation = cross_sectional_orientation
        self.slice_images = slice_images
        self.images_data = images_data
        self.status_actor = status_actor
        self.slice = image_viewer.GetSliceMin()
        self.min_slice = image_viewer.GetSliceMin()
        self.max_slice = image_viewer.GetSliceMax()
        self.update_status_message()

    def update_status_message(self):
        # Update the status message with the current slice
        message = f'Slice Number {self.slice + 1}/{self.max_slice + 1} - {self.cross_sectional_orientation}'
        self.status_actor.GetMapper().SetInput(message)

    def move_slice_forward(self, obj, event):   # noqa
        if self.slice < self.max_slice:
            self.slice += 1
            self.image_viewer.SetSlice(self.slice)
            self.update_status_message()

    def move_slice_backward(self, obj, event):  # noqa
        if self.slice > self.min_slice:
            self.slice -= 1
            self.image_viewer.SetSlice(self.slice)
            self.update_status_message()

    def update_render(self):
        self.update_status_message()
        self.image_viewer.Render()

    def update_viewer(self):
        self.slice_images.Update()
        self.image_viewer.SetInputData(self.slice_images.GetOutput())

    def key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == 'Up':
            self.move_slice_forward(obj, event)
        elif key == 'Down':
            self.move_slice_backward(obj, event)

        if key in ['a', 'c', 's']:
            self.update_cross_sectional_orientation(key)

        if key in ['1', '2', '3', '4']:
            self.update_modality(key)

    def update_cross_sectional_orientation(self, key):
        if key == 'a':
            self.slice_images.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)
            self.cross_sectional_orientation = 'Axial'
        elif key == 'c':
            self.slice_images.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, -1, 0)
            self.cross_sectional_orientation = 'Coronal'
        elif key == 's':
            self.slice_images.SetResliceAxesDirectionCosines(0, 1, 0, 0, 0, 1, 1, 0, 0)
            self.cross_sectional_orientation = 'Sagittal'
        self.update_viewer()
        self.min_slice = self.image_viewer.GetSliceMin()
        self.max_slice = self.image_viewer.GetSliceMax()
        if self.slice <= self.max_slice:
            self.image_viewer.SetSlice(self.slice)
        else:
            self.image_viewer.SetSlice(self.max_slice)
            self.slice = self.max_slice
        self.update_render()

    def update_modality(self, key):
        if key == '1':
            self.slice_images.SetInputData(self.images_data['flair'])
        elif key == '2':
            self.slice_images.SetInputData(self.images_data['t1'])
        elif key == '3':
            self.slice_images.SetInputData(self.images_data['t1ce'])
        elif key == '4':
            self.slice_images.SetInputData(self.images_data['t2'])
        self.update_viewer()
        self.update_render()
