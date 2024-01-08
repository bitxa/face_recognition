import shutil
import wx
import os
import cv2


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
            parent, title=title, size=(500, 400))
        self.filePaths = []  # List to store file paths
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#4B4B4B')
        vbox = wx.BoxSizer(wx.VERTICAL)

        instruction_text = wx.StaticText(
            panel, label="Arrastre y suelte las fotos/vídeos aquí o haga clic para seleccionarlos")
        vbox.Add(instruction_text, flag=wx.ALL | wx.CENTER, border=10)

        self.file_list_box = wx.ListBox(panel, style=wx.LB_SINGLE)
        vbox.Add(self.file_list_box, proportion=1,
                 flag=wx.EXPAND | wx.ALL, border=10)

        self.name_entry = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.name_entry.SetHint("Ingrese el nombre de la persona")
        vbox.Add(self.name_entry, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.add_button = wx.Button(panel, label='Añadir rostro')
        self.add_button.Bind(wx.EVT_BUTTON, self.OnAddMedia)
        vbox.Add(self.add_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.remove_button = wx.Button(
            panel, label='Remover el último archivo')
        self.remove_button.Bind(wx.EVT_BUTTON, self.OnRemoveSelected)
        vbox.Add(self.remove_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

        file_drop_target = FileDrop(self)
        self.file_list_box.Bind(wx.EVT_LEFT_DOWN, self.OnFindFiles)

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

    def save_photos(self, file_paths, person_name, base_dir='images'):
        # Create a directory for the person if it doesn't exist
        person_dir = os.path.join(base_dir, person_name)
        if not os.path.exists(person_dir):
            os.makedirs(person_dir)

        # Copy each file to the person's directory
        for file_path in file_paths:
            # Define the destination path
            dest_path = os.path.join(person_dir, os.path.basename(file_path))
            # Copy the file
            shutil.copy(file_path, dest_path)
            print(f"File {file_path} copied to {dest_path}")


def main():
    app = wx.App()
    AddMediaWindow(None, title='Add Media')
    app.MainLoop()


if __name__ == '__main__':
    main()


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
