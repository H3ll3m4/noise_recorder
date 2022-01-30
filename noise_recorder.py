import update_diary
import send_email
import noise_detector
import multiplexing

DURATION = 30 #in seconds

def main():
	while True:
		try:
			noise = noise_detector.noise_trigger()
			if noise is not False:
				filename = multiplexing.record_video_with_audio_threads(DURATION)
				update_diary.capture_in_diary(noise,filename)
				send_email.create_send_message(filename)
		except KeyboardInterrupt: # Ctrl-C 
			break


if __name__ == "__main__" : 
	main()