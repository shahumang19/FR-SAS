from threading import Thread
from queue import Queue
from datetime import datetime
import time
import cv2


class WebcamVideoStream:
    def __init__(self, src=0, skip_frames=15, time_stamp=10, queue_threshold=20):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.time_stamp = time_stamp
        self.count_frames = 1
        self.skip_frames = skip_frames
        self.current_time = datetime.now()
        (self.grabbed, self.frame) = self.stream.read()
        self.queue = Queue(maxsize=128)
        self.queue_counter = 1
        self.queue_threshold = queue_threshold
        if self.grabbed:
            self.queue.put((self.current_time, self.frame))
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        self.start_time = time.time()
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            minutes = int(((time.time() - self.start_time) % 3600) // 60)
            # print(minutes, self.time_stamp)
            if minutes >= self.time_stamp:
                self.queue_counter = 0
                self.start_time = time.time()

            if (minutes >= self.time_stamp) or (self.queue_counter <= self.queue_threshold):
                # otherwise, read the next frame from the stream
                self.count_frames += self.skip_frames
                self.stream.set(1, self.count_frames)
                self.current_time = datetime.now()
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    # print(f"{self.queue_counter}")
                    self.queue_counter += 1
                    self.queue.put((self.current_time, self.frame))


    def read(self):
        # return the frame most recently read
        if not self.queue.empty():
            return self.queue.get()

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        # tries = 0
        # while self.queue.qsize() == 0 and not self.stopped and tries < 5:
        #     time.sleep(0.01)
        #     tries += 1

        return self.queue.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True




# class WebcamVideoStream:
#     def __init__(self, src=0, name="WebcamVideoStream", skip_frames=15):
#         # initialize the video camera stream and read the first frame
#         # from the stream
#         self.stream = cv2.VideoCapture(src)
#         self.count_frames = 1
#         self.skip_frames = skip_frames
#         self.current_time = datetime.now()
#         (self.grabbed, self.frame) = self.stream.read()
#         # initialize the thread name
#         self.name = name

#         # initialize the variable used to indicate if the thread should
#         # be stopped
#         self.stopped = False

#     def start(self):
#         # start the thread to read frames from the video stream
#         t = Thread(target=self.update, name=self.name, args=())
#         t.daemon = True
#         t.start()
#         return self

#     def update(self):
#         # keep looping infinitely until the thread is stopped
#         while True:
#             # if the thread indicator variable is set, stop the thread
#             if self.stopped:
#                 return

#             self.count_frames += self.skip_frames
#             self.stream.set(1, self.count_frames)

#             # otherwise, read the next frame from the stream
#             self.current_time = datetime.now()
#             (self.grabbed, self.frame) = self.stream.read()

#     def read(self):
#         # return the frame most recently read
#         return self.current_time, self.frame

#     def stop(self):
#         # indicate that the thread should be stopped
#         self.stopped = True




class FileVideoStream:
    def __init__(self, path, transform=None, queue_size=128, skip_frames=15):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        self.transform = transform
        self.count_frames = 0
        self.skip_frames = skip_frames
        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize=queue_size)
        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                current_time = datetime.now()
                (grabbed, frame) = self.stream.read()
                self.count_frames += self.skip_frames
                self.stream.set(1, self.count_frames)

                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stopped = True
                    
                # if there are transforms to be done, might as well
                # do them on producer thread before handing back to
                # consumer thread. ie. Usually the producer is so far
                # ahead of consumer that we have time to spare.
                #
                # Python is not parallel but the transform operations
                # are usually OpenCV native so release the GIL.
                #
                # Really just trying to avoid spinning up additional
                # native threads and overheads of additional
                # producer/consumer queues since this one was generally
                # idle grabbing frames.
                if self.transform:
                    frame = self.transform(frame)

                # add the frame to the queue
                self.Q.put((current_time, frame))
            else:
                time.sleep(0.1)  # Rest for 10ms, we have a full queue

        self.stream.release()

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of
    # file stream.
    def running(self):
        return self.more() or not self.stopped

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.1)
            tries += 1

        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()



if __name__ == "__main__":
    from imutils import resize

    # vs1 = FileVideoStream("temp\\1.MOV").start()
    # vs2 = FileVideoStream("temp\\2.mp4").start()
    # vs3 = FileVideoStream("temp\\3.mp4").start()
    # vss = (vs1,vs2,vs3)
    vss = [WebcamVideoStream(time_stamp=1).start()]

    while True:
        count = 0
        for ix, vs in enumerate(vss, start=1):
            if vs.more():
                ftime, frame = vs.read()
                print(f"{ix} -- {ftime}")
                if frame is not None:
                    frame = resize(frame, width=min(400, frame.shape[1]))
                    cv2.imshow(f"{ix}", frame)
                else:
                    count += 1
                    vs.stop()
            else:
                pass
                # print(f"{ix} - No frame found")
            
        if cv2.waitKey(1) == 13 or count == 3:
            for vs in vss:
                vs.stop()
            break


    cv2.destroyAllWindows()