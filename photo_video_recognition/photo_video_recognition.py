import threading
import numpy as np
import wx
import cv2

from live_recognition.live_recognition import LiveRecognitionThread

class PhotoVideoRecognitionWindow(wx.Frame):

    def __init__(self, parent, title):
        super(PhotoVideoRecognitionWindow, self).__init__(
            parent, title=title, size=(900, 700))
        self.loaded_media = None
        self.file_path = None
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#4B4B4B')
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.load_button = wx.Button(panel, label='Cargar foto/video')
        self.load_button.Bind(wx.EVT_BUTTON, self.OnLoadMedia)
        vbox.Add(self.load_button, flag=wx.EXPAND | wx.ALL, border=10)

        # Image display panel
        self.image_display = wx.StaticBitmap(panel)
        vbox.Add(self.image_display, proportion=1,
                 flag=wx.EXPAND | wx.ALL, border=10)

        self.analyze_button = wx.Button(panel, label='Analizar rostro')
        self.analyze_button.Bind(wx.EVT_BUTTON, self.OnAnalyzeFace)
        vbox.Add(self.analyze_button, flag=wx.EXPAND | wx.ALL, border=10)

        self.close_button = wx.Button(panel, label='Cerrar visualización')
        self.close_button.Bind(wx.EVT_BUTTON, self.OnCloseMedia)
        vbox.Add(self.close_button, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

    def OnLoadMedia(self, event):
        with wx.FileDialog(self, "Escoge una foto o video",
                           wildcard="Photo and video files (*.jpg;*.jpeg;*.png;*.mp4;*.mov)|*.jpg;*.jpeg;*.png;*.mp4;*.mov",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # User cancelled the dialog

            self.file_path = fileDialog.GetPath()  # Save the file path
            if self.file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.loaded_media = cv2.imread(self.file_path)
                self.display_image(self.loaded_media)  # Display the image
            else:
                self.loaded_media = self.file_path
                # Display a frame from the video
                self.display_video_frame(self.file_path)

    def display_image(self, image):
        # Convert the cv2 image (numpy array) to a wx.Image
        height, width = image.shape[:2]
        # Convert to RGB for wx.Image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        wx_image = wx.Image(width, height, image.flatten())
        # Resize image to fit the display panel
        W, H = self.image_display.GetSize().Get()
        wx_image = wx_image.Scale(W, H, wx.IMAGE_QUALITY_HIGH)
        self.image_display.SetBitmap(wx.Bitmap(wx_image))
        self.Layout()

    def display_video_frame(self, video_path):
        # Start video processing in a separate thread
        self.video_processing_thread = threading.Thread(target=self.process_and_display_video, args=(video_path,))
        self.video_processing_thread.start()

    def process_and_display_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame for face recognition
            self.process_frame_for_recognition(frame)

            # Convert frame to wx.Image and display it
            wx.CallAfter(self.update_gui_with_frame, frame)

        cap.release()

    def process_frame_for_recognition(self, frame):
        # Perform face recognition on the frame
        recognizer = LiveRecognitionThread(frame, "images")
        recognizer.start()
        recognizer.join()
        # Note: Adjust this method based on your face recognition logic

    def update_gui_with_frame(self, frame):
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width = frame.shape[:2]
            wx_frame = wx.Image(width, height, frame.flatten())
            W, H = self.image_display.GetSize().Get()
            wx_frame = wx_frame.Scale(W, H, wx.IMAGE_QUALITY_HIGH)
            self.image_display.SetBitmap(wx.Bitmap(wx_frame))
            self.Refresh()

    def OnAnalyzeFace(self, event):
        if self.loaded_media is not None:
            if isinstance(self.loaded_media, np.ndarray):
                self.analyze_frame(self.loaded_media)  # Analyze the image
            elif isinstance(self.loaded_media, str):
                self.analyze_video(self.loaded_media)  # Analyze the video
            else:
                wx.MessageBox('Archivo no admitido para el análisis.',
                              'Error', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox('No hay medios cargados para el análisis.',
                          'Error', wx.OK | wx.ICON_ERROR)

    def OnCloseMedia(self, event):
        if hasattr(self, 'video_processing_thread'):
            self.video_processing_thread.join()
        cv2.destroyAllWindows()
        self.loaded_media = None
        self.image_display.SetBitmap(wx.Bitmap(wx.Image(1, 1)))
        self.Layout()

def main():
    app = wx.App(False)
    frame = PhotoVideoRecognitionWindow(None, title='Reconocimiento de foto/video.')
    app.MainLoop()

if __name__ == '__main__':
    main()
