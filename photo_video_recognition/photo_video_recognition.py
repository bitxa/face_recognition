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

        panel.SetSizer(vbox)
        
        self.close_button = wx.Button(panel, label='Cerrar visualización')
        self.close_button.Bind(wx.EVT_BUTTON, self.OnCloseMedia)
        vbox.Add(self.close_button, flag=wx.EXPAND | wx.ALL, border=10)

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
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            # Convert to RGB for wx.Image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width = frame.shape[:2]
            wx_frame = wx.Image(width, height, frame.flatten())
            W, H = self.image_display.GetSize().Get()
            wx_frame = wx_frame.Scale(W, H, wx.IMAGE_QUALITY_HIGH)
            self.image_display.SetBitmap(wx.Bitmap(wx_frame))
            self.Layout()
        cap.release()

    def analyze_frame(self, frame):
        # Start face recognition in a separate thread
        recognizer = LiveRecognitionThread(frame, "images")
        recognizer.start()
        recognizer.join()
    
        while True:
            # Show the frame
            cv2.imshow('Frame Analysis', frame)
    
            # Check for 'q' key press or if the window is closed
            if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('Frame Analysis', 0) < 0:
                break
    
        cv2.destroyAllWindows()

            
            

    def analyze_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            self.analyze_frame(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def OnAnalyzeFace(self, event):
        if self.loaded_media is not None:
            # Check if it's an image (NumPy array)
            if isinstance(self.loaded_media, np.ndarray):
                self.analyze_frame(self.loaded_media)  # Analyze the image
            elif isinstance(self.loaded_media, str):  # Check if it's a video path
                self.analyze_video(self.loaded_media)  # Analyze the video
            else:
                wx.MessageBox('Archivo no admitido para el análisis.',
                              'Error', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox('No hay medios cargados para el análisis.',
                          'Error', wx.OK | wx.ICON_ERROR)

    def OnCloseMedia(self, event):
        cv2.destroyAllWindows()  # This will close all cv2 windows
        self.loaded_media = None  # Reset the loaded media
        # Optionally, clear the image display if needed
        self.image_display.SetBitmap(wx.Bitmap(wx.Image(1, 1)))  # Set an empty bitmap
        self.Layout()
def main():
    app = wx.App(False)
    frame = PhotoVideoRecognitionWindow(None, title='Reconocimiento de foto/video.')
    app.MainLoop()


if __name__ == '__main__':
    main()
