"""
The main method for the hand segmentation process.
Author: Benned Hedegaard
Last revised: 8/7/2019
"""
from picamera import PiCamera
import picamera.array
from time import sleep
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def setupCamera(resolution=(640,416)):
    # Returns a camera with specified settings.
    camera = PiCamera() # Instance of the main class of picamera.
    camera.rotation = 180 # Rotates image so it's right-side up.
    camera.hflip = True # Horizontal flip.
    camera.resolution = resolution
    # Need 15 framerate to use maximum resolution.
    if resolution[0] == 2592 and resolution[1] == 1944:
        camera.framerate = 15
    return camera

def addBox(mask,r,c,h,w):
    """Adds a red box to given mask at [r,c]
    with height h, width w."""
    
    if w < 2 or h < 2:
        print("Invalid input: Box dimension < 2.")
        return mask
    if r < 0 or r >= mask.shape[0] or r + h >= mask.shape[0]:
        print("Invalid input: Row out of bounds.")
        return mask
    if c < 0 or c >= mask.shape[1] or c + w >= mask.shape[1]:
        print("Invalid input: Column out of bounds.")
        return mask
    
    pixel_val = [255,0,0,255]
    mask[r,c:c+w] = pixel_val # Top side.
    mask[r+1,c:c+w] = pixel_val
    mask[r+h,c:c+w] = pixel_val # Bottom side.
    mask[r+h-1,c:c+w] = pixel_val
    mask[r:r+h,c] = pixel_val # Left side.
    mask[r:r+h,c+1] = pixel_val
    mask[r:r+h,c+w] = pixel_val # Right side.
    mask[r:r+h,c+w-1] = pixel_val
    return mask

def createMask(camera,bb_r,bb_c,bb_h,bb_w):
    res = camera.resolution # This will be columns by rows.
    mask = np.zeros((res[1],res[0],4), dtype=np.uint8)
    mask = addBox(mask,bb_r,bb_c,bb_h,bb_w)
    mask_img = Image.fromarray(mask)
    # mask_img.save("test.png")
    return mask_img

def adjustMask(camera,box):
    # A user interface for editing the box.
    save_text = camera.annotate_text
    text_size = camera.annotate_text_size
    
    w = camera.resolution[0]
    h = camera.resolution[1]
    step = 50 # Will decrease as user narrows in on goal.
    size_step = 10
    
    bb_r = box[0]
    bb_c = box[1]
    bb_h = box[2]
    bb_w = box[3]
    
    mask_img = createMask(camera,bb_r,bb_c,bb_h,bb_w)
    o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                layer = 3, alpha = 10)
    camera.start_preview(alpha=225) # alpha adjusts transparency 0-255
    
    while (True):
        camera.annotate_text = "Should we adjust this box? (Y/N)"
        instr = input().lower()
    
        if instr == "n":
            camera.annotate_text = "Ok, sounds good."
            sleep(3)
            # Reset camera as-was.
            camera.stop_preview()
            camera.remove_overlay(o)
            camera.annotate_text = save_text
            camera.annotate_text_size = text_size
            return box
        elif instr == "y":
            break
        else:
            camera.annotate_text = "Input not recognized."
            sleep(0.5)
            continue
    
    while (True):
        camera.annotate_text = "Move box: (WASD, C to continue)"
        instr = input().lower()
        if instr == "c":
            break # Exit the move loop.
        elif instr == "w": # Move box up.
            if bb_r > step:
                bb_r -= step
            else:
                camera.annotate_text = "Box already close to top."
                sleep(0.5)
                continue
        elif instr == "a": # Move box left.
            if bb_c > step:
                bb_c -= step
            else:
                camera.annotate_text = "Box already close to left side."
                sleep(0.5)
                continue
        elif instr == "s": # Move box down.
            if (bb_r + bb_h) < (h - step):
                bb_r += step
            else:
                camera.annotate_text = "Box already close to bottom."
                sleep(0.5)
                continue
        elif instr == "d": # Move box right.
            if (bb_c + bb_w) < (w - step):
                bb_c += step
            else:
                camera.annotate_text = "Box already close to right side."
                sleep(0.5)
                continue
        else:
            camera.annotate_text = "Input not recognized."
            sleep(0.5)
            continue
        # If we reach here, the mask should be changed.
        mask_img = createMask(camera,bb_r,bb_c,bb_h,bb_w)
        camera.remove_overlay(o)
        o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                           layer = 3, alpha = 10)
        
    while (True):
        camera.annotate_text_size = 24
        camera.annotate_text = "Input E/R to enlarge/reduce box. (C to continue)"
        instr = input().lower()
        if instr == "c":
            camera.annotate_text_size = 32
            break # Exit the size loop.
        elif instr == "e": # Enlarge box.
            while (True): # Enlarge loop...
                camera.annotate_text = "Which direction? (WASD, C to continue)"
                instr = input().lower()
                if instr == "c":
                    break # Exit the enlarge loop.
                elif instr == "w": # Enlarge upwards.
                    if bb_r > size_step:
                        bb_r -= size_step
                        bb_h += size_step
                    else:
                        camera.annotate_text = "No room on top."
                        sleep(0.5)
                        continue
                elif instr == "a": # Enlarge to the left.
                    if bb_c > size_step:
                        bb_c -= size_step
                        bb_w += size_step
                    else:
                        camera.annotate_text = "No room on left."
                        sleep(0.5)
                        continue
                elif instr == "s": # Enlarge downwards.
                    if (bb_r + bb_h) < (h - size_step):
                        bb_h += size_step
                    else:
                        camera.annotate_text = "No room on bottom."
                        sleep(0.5)
                        continue
                elif instr == "d": # Enlarge to the right.
                    if (bb_c + bb_w) < (w - size_step):
                        bb_w += size_step
                    else:
                        camera.annotate_text = "No room on right."
                        sleep(0.5)
                        continue
                else:
                    camera.annotate_text = "Input not recognized."
                    sleep(0.5)
                    continue
                
                # If we reach here, changes were made.
                mask_img = createMask(camera,bb_r,bb_c,bb_h,bb_w)
                camera.remove_overlay(o)
                o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                           layer = 3, alpha = 10)
            continue # Enlarge always exits to top of size loop.
        elif instr == "r": # Reduce box.
            while (True): # Reduce loop...
                camera.annotate_text = "Which direction? (WASD, C to continue)"
                instr = input().lower()
                if instr == "c":
                    break # Exit the reduce loop.
                elif instr == "w": # Reduce from top.
                    if bb_h > size_step:
                        bb_r += size_step
                        bb_h -= size_step
                    else:
                        camera.annotate_text = "No room from top."
                        sleep(0.5)
                        continue
                elif instr == "a": # Reduce from the left.
                    if bb_w > size_step:
                        bb_c += size_step
                        bb_w -= size_step
                    else:
                        camera.annotate_text = "No room from left."
                        sleep(0.5)
                        continue
                elif instr == "s": # Reduce from the bottom.
                    if bb_h > size_step:
                        bb_h -= size_step
                    else:
                        camera.annotate_text = "No room from bottom."
                        sleep(0.5)
                        continue
                elif instr == "d": # Reduce from the right.
                    if bb_w > size_step:
                        bb_w -= size_step
                    else:
                        camera.annotate_text = "No room from right."
                        sleep(0.5)
                        continue
                else:
                    camera.annotate_text = "Input not recognized."
                    sleep(0.5)
                    continue
                
                # If we reach here, changes were made.
                mask_img = createMask(camera,bb_r,bb_c,bb_h,bb_w)
                camera.remove_overlay(o)
                o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                           layer = 3, alpha = 10)
            continue # Reduce always exits to top of size loop.
        else:
            camera.annotate_text = "Input not recognized."
            sleep(0.5)
            continue
        
    # Reset camera as-was.
    camera.stop_preview()
    camera.remove_overlay(o)
    camera.annotate_text = save_text
    camera.annotate_text_size = text_size
    
    return [bb_r,bb_c,bb_h,bb_w]

def captureROI(camera,box,YUV = False):
    # Captures and returns a numpy array of ROI.
    save_text = camera.annotate_text
    camera.annotate_text = "Taking sample in 3..."
    mask_img = createMask(camera,box[0],box[1],box[2],box[3])
    o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                layer = 3, alpha = 10)
    
    camera.start_preview(alpha=225) # alpha adjusts transparency 0-255
    sleep(1)
    camera.annotate_text = "Taking sample in 2..."
    sleep(1)
    camera.annotate_text = "Taking sample in 1..."
    sleep(1)
    camera.annotate_text = ""
    
    roi = np.zeros((box[2],box[3],3))
    print(roi.shape)
    if YUV:
        with picamera.array.PiYUVArray(camera) as output:
            camera.capture(output, 'yuv', use_video_port = True)
            print("Captured %dx%d image." % (output.array.shape[1],output.array.shape[0]))
            for r in range(box[2]):
                for c in range(box[3]):
                    pixel = output.array[box[0]+r, box[1]+c]
                    roi[r,c] = pixel
    else:
        with picamera.array.PiRGBArray(camera) as output:
            camera.capture(output, 'rgb', use_video_port = True)
            print("Captured %dx%d image." % (output.array.shape[1],output.array.shape[0]))
            for r in range(box[2]):
                for c in range(box[3]):
                    pixel = output.array[box[0]+r, box[1]+c]
                    roi[r,c] = pixel
        
    camera.stop_preview()
    camera.remove_overlay(o)
    camera.annotate_text = save_text
    
    return roi

def getROImask(mask,bb_r,bb_c,bb_h,bb_w,v_offset,h_offset,scale):
    # Return ROI mask with current box.
    mask_copy = np.copy(mask)
    edge = [255,0,0]
    
    # These are the box's starting pixels in the actual mask
    img_r = v_offset+(bb_r*scale)
    img_c = h_offset+(bb_c*scale)
    mask_copy[img_r:img_r+(bb_h*scale),img_c] = edge
    mask_copy[img_r:img_r+(bb_h*scale),img_c+(bb_w*scale)] = edge
    mask_copy[img_r,img_c:img_c+(bb_w*scale)] = edge
    mask_copy[img_r+(bb_h*scale),img_c:img_c+(bb_w*scale)] = edge
    return Image.fromarray(mask_copy)

def getTextImg(camera,text,size):
    res = camera.resolution # This will be columns by rows.
    img = Image.new("RGBA", res, color=(0,0,0,0))
    fnt = ImageFont.truetype("Quicksand-Regular.ttf", size)
    
    d = ImageDraw.Draw(img)
    d.text((10,10), text, font=fnt, fill=(255,255,255,255))
    
    return img

def overlayText(camera,text,size=32,duration=0.5):
    # Overlays the given text onscreen for given duration.
    img = getTextImg(camera,text,size)
    
    o = camera.add_overlay(img.tobytes(), size = img.size,
                layer = 3, alpha = 225)
    sleep(duration)
    camera.remove_overlay(o)
    return

def prompt(camera,text,size=32):
    t_img = getTextImg(camera,text,size)
    t_o = camera.add_overlay(t_img.tobytes(), size = t_img.size,
        layer = 2, alpha = 225)        
    instr = input().lower()
    camera.remove_overlay(t_o)
    return instr

def getSample(camera,roi):
    res = camera.resolution # This will be columns by rows.
    mask = np.zeros((res[1],res[0],3), dtype=np.uint8)
    
    # Scale roi as large as possible.
    h = res[1]
    w = res[0]
    roi_h = roi.shape[0]
    roi_w = roi.shape[1]
    scale = 1
    
    while(True):
        if (scale+1)*roi_h < h and (scale+1)*roi_w < w:
            scale += 1
        else:
            break
        
    scaled_h = roi_h * scale
    scaled_w = roi_w * scale
    v_offset = (h - scaled_h) // 2
    h_offset = (w - scaled_w) // 2
    
    # Add ROI to the mask.
    for r in range(roi_h):
        for c in range(roi_w):
            for rs in range(scale):
                for cs in range(scale):
                    row = v_offset + r*scale + rs
                    col = h_offset + c*scale + cs
                    mask[row,col] = roi[r,c]
    
    # Now extract skin sample.
    save_text = camera.annotate_text
    
    size_step = 3
    
    # Box scrolls within context of the ROI image.
    bb_r = 0
    bb_c = 0
    bb_h = roi_h
    bb_w = roi_w
    
    mask_img = getROImask(mask,bb_r,bb_c,bb_h,bb_w,v_offset,h_offset,scale)
    backdrop = np.zeros((res[1],res[0],3), dtype=np.uint8)
    b_img = Image.fromarray(backdrop)
    backdrop_o = camera.add_overlay(b_img.tobytes(), size = b_img.size,
                layer = 1, alpha = 225)
    
    o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                layer = 2, alpha = 225)
    overlayText(camera,"Time to zoom in on only pixels of skin.",32,2)

    while (True):
        instr = prompt(camera,"Input E/R to enlarge/reduce box. (C to continue)",24)
        if instr == "c":
            break # Exit the size loop.
        elif instr == "e": # Enlarge box.
            while (True): # Enlarge loop...
                instr = prompt(camera,"Which direction? (WASD, C to continue)",32)
                if instr == "c":
                    break # Exit the enlarge loop.
                elif instr == "w": # Enlarge upwards.
                    if bb_r > size_step:
                        bb_r -= size_step
                        bb_h += size_step
                    else:
                        overlayText(camera,"No room on top.")
                        continue
                elif instr == "a": # Enlarge to the left.
                    if bb_c > size_step:
                        bb_c -= size_step
                        bb_w += size_step
                    else:
                        overlayText(camera,"No room on left.")
                        continue
                elif instr == "s": # Enlarge downwards.
                    if (bb_r + bb_h) < (roi_h - size_step):
                        bb_h += size_step
                    else:
                        overlayText(camera,"No room on bottom.")
                        continue
                elif instr == "d": # Enlarge to the right.
                    if (bb_c + bb_w) < (roi_w - size_step):
                        bb_w += size_step
                    else:
                        overlayText(camera,"No room on right.")
                        continue
                else:
                    overlayText(camera,"Input not recognized.")
                    continue
                    
                # If we reach here, changes were made.
                mask_img = getROImask(mask,bb_r,bb_c,bb_h,bb_w,v_offset,h_offset,scale)
                camera.remove_overlay(o)
                o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                    layer = 2, alpha = 225)
            continue # Enlarge always exits to top of size loop.
        elif instr == "r": # Reduce box.
            while (True): # Reduce loop...
                instr = prompt(camera, "Which direction? (WASD, C to continue)",32)
                if instr == "c":
                    break # Exit the reduce loop.
                elif instr == "w": # Reduce from top.
                    if bb_h > size_step:
                        bb_r += size_step
                        bb_h -= size_step
                    else:
                        overlayText(camera,"No room from top.")
                        continue
                elif instr == "a": # Reduce from the left.
                    if bb_w > size_step:
                        bb_c += size_step
                        bb_w -= size_step
                    else:
                        overlayText(camera,"No room from left.")
                        continue
                elif instr == "s": # Reduce from the bottom.
                    if bb_h > size_step:
                        bb_h -= size_step
                    else:
                        overlayText(camera,"No room from bottom.")
                        continue
                elif instr == "d": # Reduce from the right.
                    if bb_w > size_step:
                        bb_w -= size_step
                    else:
                        overlayText(camera,"No room from right.")
                        continue
                else:
                    overlayText(camera,"Input not recognized.")
                    continue
                    
                # If we reach here, changes were made.
                mask_img = getROImask(mask,bb_r,bb_c,bb_h,bb_w,v_offset,h_offset,scale)
                camera.remove_overlay(o)
                o = camera.add_overlay(mask_img.tobytes(), size = mask_img.size,
                    layer = 2, alpha = 225)
                continue # Reduce always exits to top of size loop.
        else:
            overlayText(camera,"Input not recognized.")
            continue
        
    # Reset camera as-was.
    camera.remove_overlay(o)
    camera.remove_overlay(backdrop_o)
    camera.annotate_text = save_text
    
    # Crop and return sample.
    sample = np.zeros((bb_h,bb_w,3), dtype=np.uint8)
    for r in range(bb_h):
        for c in range(bb_w):
            pixel = roi[bb_r+r,bb_c+c]
            sample[r,c] = pixel
    
    sample_img = Image.fromarray(np.copy(sample))
    sample_img.save("sample.png")
    return sample

def main():
    camera = setupCamera()
    box = [60, 390, 200, 140] # Ordered r,c,h,w.
    while (True):
        instr = input("What should we do?\n* 1 - Adjust bounding boxes\n* 2 - Ready\n* q - Quit program\n")
        if instr == "q":
            print("Program terminated")
            break
        
        # Other cases:
        if instr == "1": # Adjust the bounding box.
            box = adjustMask(camera,box)
            print(box)
        elif instr == "2":
            # Ready case.
            roi = captureROI(camera,box)
            print(roi.shape)
            sample = getSample(camera,roi)
        else:
            print("\nInput not recognized. Please try again.")
            continue

if __name__ == "__main__":
    main()