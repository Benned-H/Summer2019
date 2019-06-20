"""
Testing with the Raspberry Pi camera.
Author: Benned Hedegaard
Last revised: 6/19/2019
"""
from picamera import PiCamera
from time import sleep # Lets us create time delays

camera = PiCamera() # Instance of the main class of picamera.
print(camera.resolution)

camera.rotation = 180 # Rotates image so it's right-side up.
camera.hflip = True # Horizontal flip.
camera.start_preview(alpha=225) # alpha adjusts transparency 0-255
sleep(5)
camera.capture('./image.jpg')
camera.stop_preview()
camera.close()
