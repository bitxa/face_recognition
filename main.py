import cv2
from add_face.new_face_window import AddMediaWindow
from live_recognition.live_recognition import LiveRecognitionThread
import wx
import os

from photo_video_recognition.photo_video_recognition import PhotoVideoRecognitionWindow


class FaceRecognitionApp(wx.Frame):

    def __init__(self, parent, title):
        super(FaceRecognitionApp, self).__init__(
            parent, title=title, size=(1000, 560))
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        # Pastel purple background for the panel
        panel.SetBackgroundColour('#52575D')

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.add_face_button = self.createButtonWithIcon(
            panel, "Añadir nuevo rostro", "assets/icons/face.png", self.OnAddFace)
        vbox.Add(self.add_face_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.TOP, border=25)

        self.live_recognition_button = self.createButtonWithIcon(
            panel, "Reconocimiento facial en vivo", "assets/icons/photo.png", self.OnLiveRecognition)
        vbox.Add(self.live_recognition_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.TOP, border=25)

        self.photo_video_recognition_button = self.createButtonWithIcon(
            panel, "Reconocimiento de foto o video", "assets/icons/live.png", self.OnPhotoVideoRecognition)
        vbox.Add(self.photo_video_recognition_button, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.TOP, border=25)

        panel.SetSizer(vbox)

    def createButtonWithIcon(self, parent, label, iconPath, eventHandler):
        button = wx.Button(parent, -1, label)
        button.Bind(wx.EVT_BUTTON, eventHandler)
        # Pastel red background for the button
        button.SetBackgroundColour('#52575D')
        # Dark text color for better contrast
        button.SetForegroundColour('#3d3d3d')
        if os.path.exists(iconPath):
            image = wx.Image(iconPath, wx.BITMAP_TYPE_ANY).Scale(
                50, 50, wx.IMAGE_QUALITY_HIGH)
            bitmap = wx.Bitmap(image)
            button.SetBitmap(bitmap, wx.LEFT)
            button.SetBitmapMargins((10, 10))
        return button

    def OnAddFace(self, event):
        add_media_window = AddMediaWindow(self, title='Añadir archivos')
        add_media_window.Show()
        pass

    def OnLiveRecognition(self, event):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame = cv2.flip(frame, 1)
            recognizer = LiveRecognitionThread(frame, 'images')
            recognizer.start()
            recognizer.join()

            cv2.imshow('Video Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        pass

    def OnPhotoVideoRecognition(self, event):
        recognition_window = PhotoVideoRecognitionWindow(
            self, title='Photo/Video Recognition')
        recognition_window.Show()
        pass


def main():
    app = wx.App()
    ex = FaceRecognitionApp(None, title='Sistema de Reconocimiento Facial')
    app.MainLoop()


if __name__ == '__main__':
    main()
