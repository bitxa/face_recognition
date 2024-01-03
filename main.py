import wx
import os
import shutil
from video_capture_module import capture_frames  # Make sure to define this module
from face_recognition_module import perform_face_recognition  # Define this module
import face_recognition
class FaceRecognitionApp(wx.Frame):
    
    def __init__(self, parent, title):
        super(FaceRecognitionApp, self).__init__(parent, title=title, size=(400, 200))

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.add_face_button = wx.Button(panel, label='Add Face')
        self.add_face_button.Bind(wx.EVT_BUTTON, self.OnAddFace)
        vbox.Add(self.add_face_button, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        self.open_recognizer_button = wx.Button(panel, label='Open Recognizer')
        self.open_recognizer_button.Bind(wx.EVT_BUTTON, self.OnOpenRecognizer)
        vbox.Add(self.open_recognizer_button, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        self.reset_recognizer_button = wx.Button(panel, label='Reset Recognizer')
        self.reset_recognizer_button.Bind(wx.EVT_BUTTON, self.OnResetRecognizer)
        vbox.Add(self.reset_recognizer_button, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        panel.SetSizer(vbox)

    def OnAddFace(self, event):
        with wx.TextEntryDialog(self, "Enter the person's name", "Add Face") as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                name = dialog.GetValue()
                if name:
                    capture_frames(name)

    def OnOpenRecognizer(self, event):
        # Placeholder for face recognition logic
        known_face_encodings, known_face_names = [], []
        base_dir = "captured_faces"
        for name in os.listdir(base_dir):
            person_dir = os.path.join(base_dir, name)
            if os.path.isdir(person_dir):
                for filename in os.listdir(person_dir):
                    if filename.endswith(".jpg"):
                        image_path = os.path.join(person_dir, filename)
                        image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(image)
                        if encodings:
                            known_face_encodings.append(encodings[0])
                            known_face_names.append(name)
        perform_face_recognition(known_face_encodings, known_face_names)

    def OnResetRecognizer(self, event):
        shutil.rmtree("captured_faces", ignore_errors=True)
        wx.MessageBox('Recognizer has been reset.', 'Info', wx.OK | wx.ICON_INFORMATION)

def main():
    app = wx.App()
    ex = FaceRecognitionApp(None, title='Face Recognition System')
    app.MainLoop()

if __name__ == '__main__':
    main()
