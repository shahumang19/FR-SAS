# from __future__ import print_function
# from PIL import Image
# from PIL import ImageTk
# import tkinter as tki
# import threading
# import datetime
# import imutils
# import cv2
# import os

# class PhotoBoothApp:
#     def __init__(self, vs, outputPath):
#         # store the video stream object and output path, then initialize
#         # the most recently read frame, thread for reading frames, and
#         # the thread stop event
#         self.vs = vs
#         self.outputPath = outputPath
#         self.frame = None
#         self.thread = None
#         self.stopEvent = None
#         # initialize the root window and image panel
#         self.root = tki.Tk()
#         self.panel = None
#         self.check = False

#         # create a button, that when pressed, will take the current
#         # frame and save it to file
#         btn = tki.Button(self.root, text="Snapshot!",
#             command=self.takeSnapshot)
#         btn.pack(side="bottom", fill="both", expand="yes", padx=10,
#             pady=10)
#         # start a thread that constantly pools the video sensor for
#         # the most recently read frame

#         self.stopEvent = threading.Event()
#         self.thread = threading.Thread(target=self.videoLoop, args=())
#         self.thread.start()

#         # set a callback to handle when the window is closed
#         self.root.wm_title("PyImageSearch PhotoBooth")
#         self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

#     def videoLoop(self):
#         # DISCLAIMER:
#         # I'm not a GUI developer, nor do I even pretend to be. This
#         # try/except statement is a pretty ugly hack to get around
#         # a RunTime error that Tkinter throws due to threading
#         try:
#             # keep looping over frames until we are instructed to stop
#             while not self.stopEvent.is_set():
#                 # grab the frame from the video stream and resize it to
#                 # have a maximum width of 300 pixels
#                 ret, self.frame = self.vs.read()
#                 self.frame = imutils.resize(self.frame, width=300)
        
#                 # OpenCV represents images in BGR order; however PIL
#                 # represents images in RGB order, so we need to swap
#                 # the channels, then convert to PIL and ImageTk format
#                 image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
#                 image = Image.fromarray(image)
#                 image = ImageTk.PhotoImage(image)
        
#                 # if the panel is not None, we need to initialize it
#                 if self.panel is None:
#                     self.panel = tki.Label(image=image)
#                     self.panel.image = image
#                     self.panel.pack(side="left", padx=10, pady=10)
        
#                 # otherwise, simply update the panel
#                 else:
#                     self.panel.configure(image=image)
#                     self.panel.image = image
#         except RuntimeError as e:
#             print("[INFO] caught a RuntimeError : ", e)

#     def takeSnapshot(self):
#     	# grab the current timestamp and use it to construct the
# 		# output path
#         ts = datetime.datetime.now()
#         filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
#         p = os.path.sep.join((self.outputPath, filename))
# 		# save the file
#         cv2.imwrite(p, self.frame.copy())
#         print("[INFO] saved {}".format(filename))

#     def onClose(self):
#     	# set the stop event, cleanup the camera, and allow the rest of
# 		# the quit process to continue
#         print("[INFO] closing...")
#         self.stopEvent.set()
#         self.thread.stop
#         print("[INFO] stop event...")
#         self.vs.release()
#         print("[INFO] release...")
#         self.root.quit()
#         self.root.destroy()
#         print("[INFO] root quit...")



# if __name__ == "__main__":
#     vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#     pb = PhotoBoothApp(vs, "temp\\temp")
#     print("HELLO")
#     pb.root.mainloop()
#     print("HELLO2")
#     # pb.root.destroy()
#     print("EXIT")




import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from FaceDetectionSSD import FaceDetectionSSD

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        detector = FaceDetectionSSD()
        while True:
            ret, frame = cap.read()
            if ret:
                face_locations = detector.detect_faces(frame)
                if len(face_locations) > 0:
                    frame = detector.draw_faces(frame, face_locations)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(800, 600)
        # create a label
        self.label = QLabel(self)
        self.label.move(1, 1)
        self.label.resize(640, 480)
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())