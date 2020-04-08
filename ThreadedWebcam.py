from threading import Thread
import cv2


class VideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped or not self.grabbed:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

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
            frame = vs.read()
            if frame is not None:
                frame = resize(frame, width=min(400, frame.shape[1]))
                cv2.imshow(f"{ix}", frame)
            else:
                count += 1
                vs.stop()
            
        if cv2.waitKey(1) == 13 or count == 3:
            for vs in (vs1,vs2,vs3):
                vs.stop()
            break

    cv2.destroyAllWindows()