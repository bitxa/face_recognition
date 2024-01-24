import queue
import shutil
import threading
import wx
import os
import cv2
import numpy as np


class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filepath in filenames:
            self.window.UpdateFileList(filepath)
        return True


class AddMediaWindow(wx.Frame):
    def __init__(self, parent, title):
        super(AddMediaWindow, self).__init__(
            parent, title=title, size=(800, 600))
        self.filePaths = []  # List to store file paths
        self.camera_panel = None  # Panel for displaying camera feed
        self.camera_thread = None  # To store the camera feed thread
        self.camera_queue = queue.Queue()  # Queue to communicate with camera thread
        self.capture = None  # OpenCV VideoCapture object
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour('#4B4B4B')

        control_panel = wx.Panel(main_panel)
        control_panel.SetBackgroundColour('#4B4B4B')

        self.record_button = wx.Button(
            control_panel, label='Grabar video')
        self.record_button.Bind(wx.EVT_BUTTON, self.OnRecordVideo)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(self.record_button, flag=wx.EXPAND | wx.LEFT |
                 wx.RIGHT | wx.BOTTOM, border=10)

        instruction_text = wx.StaticText(
            control_panel, label="Arrastre y suelte las fotos/vídeos aquí o haga clic para seleccionarlos")
        vbox.Add(instruction_text, flag=wx.ALL | wx.CENTER, border=10)

        self.file_list_box = wx.ListBox(
            control_panel, style=wx.LB_SINGLE)
        vbox.Add(self.file_list_box, proportion=1,
                 flag=wx.EXPAND | wx.ALL, border=10)

        self.name_entry = wx.TextCtrl(
            control_panel, style=wx.TE_PROCESS_ENTER)
        self.name_entry.SetHint("Ingrese el nombre de la persona")
        vbox.Add(self.name_entry, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.add_button = wx.Button(control_panel, label='Añadir rostro')
        self.add_button.Bind(wx.EVT_BUTTON, self.OnAddMedia)
        vbox.Add(self.add_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.remove_button = wx.Button(
            control_panel, label='Remover el último archivo')
        self.remove_button.Bind(wx.EVT_BUTTON, self.OnRemoveSelected)
        vbox.Add(self.remove_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        control_panel.SetSizer(vbox)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(control_panel, 1, wx.EXPAND)
        main_sizer.Add(self.create_camera_panel(main_panel), 2, wx.EXPAND)

        main_panel.SetSizer(main_sizer)

        file_drop_target = FileDrop(self)
        self.file_list_box.Bind(wx.EVT_LEFT_DOWN, self.OnFindFiles)

    def create_camera_panel(self, parent):
        self.camera_panel = wx.Panel(parent)
        self.camera_panel.SetBackgroundColour('#000000')
        return self.camera_panel

    def OnRecordVideo(self, event):
        name = self.name_entry.GetValue()
        if not name:
            wx.MessageBox('Por favor, ingrese un nombre.',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        person_folder = os.path.join("images", name)
        os.makedirs(person_folder, exist_ok=True)

        if self.camera_thread is None or not self.camera_thread.is_alive():
            self.camera_thread = threading.Thread(
                target=self.record_video, args=(person_folder,), daemon=True)
            self.camera_thread.start()
        else:
            wx.MessageBox('La grabación de video ya está en curso.',
                          'Info', wx.OK | wx.ICON_INFORMATION)

    def record_video(self, output_folder):
        self.capture = cv2.VideoCapture(0)

        if not self.capture.isOpened():
            wx.MessageBox('No se pudo abrir la cámara.',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        frame_count = 0
        while self.capture.isOpened():
            ret, frame = self.capture.read()
            if not ret:
                break

            # Send frame to the main thread for display
            self.camera_queue.put(frame)
            self.UpdateCameraPanel(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit loop if 'q' is pressed
                break

            # Guardar el frame
            frame_filename = os.path.join(
                output_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            frame_count += 1

            if frame_count >= 300:  # Limitar a 300 frames, por ejemplo
                break

        self.capture.release()
        cv2.destroyAllWindows()

    def UpdateCameraPanel(self, frame):
        if self.camera_panel:
            height, width, _ = frame.shape
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bitmap = wx.Bitmap.FromBuffer(width, height, image)
            wx.StaticBitmap(self.camera_panel, -1, bitmap)

    def UpdateFileList(self, filepath):
        if filepath not in self.filePaths:
            self.filePaths.append(filepath)
            self.file_list_box.Append(filepath)

    def OnAddMedia(self, event):
        name = self.name_entry.GetValue()
        if not name:
            wx.MessageBox('Please enter a name.',
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        person_folder = os.path.join("images", name)
        if not os.path.exists(person_folder):
            os.makedirs(person_folder)

        for filepath in self.filePaths:
            if filepath.lower().endswith(('.mp4', '.avi', '.mov')):  # Check if the file is a video
                extract_frames_from_video(filepath, person_folder, 20)
            else:
                # If it's not a video, just copy the image to the person's folder
                shutil.copy(filepath, person_folder)

        self.filePaths = []  # Clear the file paths list
        self.file_list_box.Clear()  # Clear the list box
        wx.MessageBox('Media added successfully.',
                      'Info', wx.OK | wx.ICON_INFORMATION)

    def OnRemoveSelected(self, event):
        if self.filePaths:
            last_index = len(self.filePaths) - 1
            self.file_list_box.Delete(last_index)
            del self.filePaths[last_index]
        else:
            wx.MessageBox('No hay archivos por remover.',
                          'Error', wx.OK | wx.ICON_ERROR)

    def OnFindFiles(self, event):
        with wx.FileDialog(self, "Seleccione los archivos", wildcard="Photo and video files (*.jpg;*.jpeg;*.png;*.mp4;*.mov)|*.jpg;*.jpeg;*.png;*.mp4;*.mov",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # User cancelled the dialog
            paths = fileDialog.GetPaths()  # Get the selected files
            for path in paths:
                self.UpdateFileList(path)

        event.Skip()


def extract_frames_from_video(video_path, output_folder, frame_rate=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    saved_frame_count = 0

    while success:
        # Save frame as JPEG file
        if count % frame_rate == 0:
            cv2.imwrite(
                f"{output_folder}/frame_{saved_frame_count}.jpg", image)
            saved_frame_count += 1
        success, image = vidcap.read()
        count += 1


def main():
    app = wx.App()
    AddMediaWindow(None, title='Add Media')
    app.MainLoop()


if __name__ == '__main__':
    main()
