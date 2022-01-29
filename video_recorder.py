import time
from datetime import date, datetime
import cv2
import threading


# VIDEO_FILENAME = "temp_video.mp4"
# REENCODED_FILENAME = "temp_video2.mp4"
REENCODED_FILENAME = "temp_video2.avi"
VIDEO_FILENAME = "temp_video.avi"
FPS = 6

def make_video_txt(start_time):
    """Retun a text to display in the video"""
    text = start_time.ctime()
    return text


class VideoThread(threading.Thread):
	def __init__(self, duration, name='VideoThread'):
		""" constructor, setting initial variables """
		self._stopevent = threading.Event()
		# Capture video from webcam
		self.vid_capture = cv2.VideoCapture(0)
		# self.vid_cod = cv2.VideoWriter_fourcc(*"XVID")
		# self.vid_cod = cv2.VideoWriter_fourcc(*"mp4v")
		self.vid_cod = cv2.VideoWriter_fourcc(*"MJPG")
		self.frame_counts = 1
		self.duration = duration
		self.output = cv2.VideoWriter(VIDEO_FILENAME, self.vid_cod, FPS, (640, 480))
		self.start_time = datetime.now()
		threading.Thread.__init__(self, name=name)


	def run(self):
		""" main control loop"""
		print("Start "+ self.getName())
		while not self._stopevent.isSet():
			ret, frame = self.vid_capture.read()
			if ret is True:
				cv2.putText(img=frame, text=make_video_txt(self.start_time), org=(50, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 255, 0),thickness=1)
				self.output.write(frame)
				self.frame_counts += 1
		 		# 0.16 because 6 FPS
				time.sleep(0.16)
				if cv2.waitKey(1) & 0xFF == ord("x"):
					self._stopevent.set()
					break
		print("Stop "+ self.getName())


	def join(self, timeout=None):
		"""Termination of the thread"""
		self._stopevent.set()
		self.output.release()
		# close the already opened camera
		self.vid_capture.release()
		# close the window and de-allocate any associated memory usage
		cv2.destroyAllWindows()		
		threading.Thread.join(self,timeout)


def thread_video_only(duration):
	"""Create a thread to record video only in VIDEO_FILENAME for duration seconds"""
	video_thread = VideoThread(duration)
	video_thread.start()
	time.sleep(float(duration))
	video_thread.join()

