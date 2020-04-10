# from threading import Thread
# from datetime import datetime
# from queue import Queue 
# import cv2


# class VideoStream:
#     def __init__(self, src=0, skip_frames=15):
#         # initialize the video camera stream and read the first frame
#         # from the stream
#         self.stream = cv2.VideoCapture(src)
#         self.count_frames = 1
#         self.skip_frames = skip_frames
#         self.current_time = datetime.now()
#         (self.grabbed, self.frame) = self.stream.read()
#         self.queue = Queue(maxsize=60)
#         if self.grabbed:
#             self.queue.put((self.current_time, self.frame))
#         # initialize the variable used to indicate if the thread should
#         # be stopped
#         self.stopped = False

#     def start(self):
#         # start the thread to read frames from the video stream
#         Thread(target=self.update, args=()).start()
#         return self

#     def update(self):
#         # keep looping infinitely until the thread is stopped
#         while True:
#             # if the thread indicator variable is set, stop the thread
#             if self.stopped:
#                 return
#             # otherwise, read the next frame from the stream
#             self.count_frames += self.skip_frames
#             self.stream.set(1, self.count_frames)
#             self.current_time = datetime.now()
#             (self.grabbed, self.frame) = self.stream.read()
#             if self.grabbed:
#                 self.queue.put((self.current_time, self.frame))


#     def read(self):
#         # return the frame most recently read
#         if not self.queue.empty():
#             return self.queue.get()

#     def stop(self):
#         # indicate that the thread should be stopped
#         self.stopped = True



from threading import Thread
from datetime import datetime
import cv2

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.current_time = datetime.now()
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            self.current_time = datetime.now()
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.current_time, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True












if __name__ == "__main__":
    from imutils import resize

    vs1 = VideoStream("temp\\1.MOV").start()
    vs2 = VideoStream("temp\\2.mp4").start()
    vs3 = VideoStream("temp\\3.mp4").start()

    while True:
        count = 0
        for ix, vs in enumerate((vs1,vs2,vs3), start=1):
            if not vs.queue.empty():
                ftime, frame = vs.read()
                print(f"{ix} -- {ftime}")
                if frame is not None:
                    frame = resize(frame, width=min(400, frame.shape[1]))
                    cv2.imshow(f"{ix}", frame)
                else:
                    count += 1
                    vs.stop()
            else:
                print(f"{ix} - No frame found")
            
        if cv2.waitKey(1) == 13 or count == 3:
            for vs in (vs1,vs2,vs3):
                vs.stop()
            break

    cv2.destroyAllWindows()