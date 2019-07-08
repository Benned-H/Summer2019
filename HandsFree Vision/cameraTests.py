"""
Testing with the Raspberry Pi camera.
Author: Benned Hedegaard
Last revised: 6/27/2019
"""
from picamera import PiCamera
from time import sleep # Lets us create time delays

def setupCamera(resolution=(1600,980)):
    # Returns a camera with specified settings.
    camera = PiCamera() # Instance of the main class of picamera.
    camera.rotation = 180 # Rotates image so it's right-side up.
    camera.hflip = True # Horizontal flip.
    camera.resolution = resolution
    # Need 15 framerate to use maximum resolution.
    if resolution[0] == 2592 and resolution[1] == 1944:
        camera.framerate = 15
    return camera

def takePicture(camera, filepath):
    camera.start_preview(alpha=225) # alpha adjusts transparency 0-255
    sleep(2)
    camera.capture(filepath)
    camera.stop_preview()
    
def brightnessTest(camera):
    bright = camera.brightness
    text = camera.annotate_text
    
    camera.start_preview()
    for b in range(100):
        camera.annotate_text = "Brightness: %s" % b
        camera.brightness = b
        sleep(0.1)
    camera.stop_preview
    camera.brightness = bright # Reset brightness as it was.
    camera.annotate_text = text
    
def contrastTest(camera):
    contrast = camera.contrast
    text = camera.annotate_text
    
    camera.start_preview()
    for c in range(100):
        camera.annotate_text = "Contrast: %s" % c
        camera.contrast = c
        sleep(0.1)
    camera.stop_preview
    camera.contrast = contrast # Reset contrast as it was.
    camera.annotate_text = text
    
def awbTest(camera):
    # Survey the white balance modes the camera has.
    mode = camera.awb_mode
    text = camera.annotate_text
    
    camera.start_preview()
    for m in camera.AWB_MODES:
        camera.awb_mode = m
        camera.annotate_text = "Mode: %s" % m
        sleep(3)
    camera.stop_preview()
    camera.awb_mode = mode # Reset the AWB mode as it was.
    camera.annotate_text = text

def main():
    camera = setupCamera()
    camera.led = True
    takePicture(camera, "./image1.jpg")
    brightnessTest(camera)
    contrastTest(camera)
    awbTest(camera) # Survey auto white balance modes.
    takePicture(camera, "./image2.jpg")
    camera.close()

if __name__ == "__main__":
    main()