# This box is all you should need to get everything up and running for experiments here.

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


os.chdir("gdrive/My Drive/Colab Notebooks/HandsFree/Photos")


### GET IMAGES ###
print("Importing images... (About 60 seconds remaining overall)")
michael = mpimg.imread("Office.png")
ashley = mpimg.imread("Ashley.png")
gwb = mpimg.imread("GWB.png")
seth = mpimg.imread("Seth.png")
tiger = mpimg.imread("Tiger.png")
steven = mpimg.imread("Steven.png")
wesley = mpimg.imread("Wesley.png")


images = [michael,ashley,gwb,seth,tiger,steven,wesley]


### SKIN SAMPLE BOUNDING BOXES ###
print("Defining bounding boxes...")
boxes = [np.zeros(4)] * len(images) # Stores r,c,h,w.
boxes[0] = [192,304,27,40] # These were all taken from above.
boxes[1] = [1100,550,100,200]
boxes[2] = [575,1550,225,200]
boxes[3] = [183,75,25,25]
boxes[4] = [375,395,100,75]
boxes[5] = [100,220,80,90]
boxes[6] = [80,90,35,35]


def getSamples(images,boxes):
 # Function likely not needed.
 samples = []
  for i in range(len(images)):
   img = images[i]
   box = boxes[i]
   sample = np.zeros((box[2],box[3],3)) # Create RGB array for cropped image.
   for r in range(sample.shape[0]):
     for c in range(sample.shape[1]):
       sample[r][c] = img[box[0]+r][box[1]+c]  
   samples.append(sample)
  
 return samples


### CONVERT SAMPLE COLOR SPACE ###
def RGB_to_YCbCr(image):
 # Converts a given RGB image to the YCbCr color space.
 if len(image[0,0]) != 3:
   print("Error: Image is not RGB.")
   return
 output = np.zeros((image.shape[0],image.shape[1],3))
 for r in range(image.shape[0]):
   for c in range(image.shape[1]):
     rgb = image[r,c]
     output[r,c,0] =  0.2568*rgb[0] + 0.5041*rgb[1] + 0.0979*rgb[2] + 0.0625
     output[r,c,1] = -0.1482*rgb[0] - 0.2910*rgb[1] + 0.4392*rgb[2] + 0.5
     output[r,c,2] =  0.4392*rgb[0] - 0.3678*rgb[1] - 0.0714*rgb[2] + 0.5
  output = output * 256 # Convert into clean 0-255 range.
 return output.astype(np.int64)


def RGB_to_YCbCr_MAT(image):
 # Matrix version of RGB --> YCbCr.
 if len(image[0,0]) != 3:
   print("Error: Image is not RGB.")
   return
  transform = np.array([[0.2568,0.5041,0.0979],
                       [-0.1482,-0.2910,0.4392],
                       [0.4392,-0.3678,-0.0714]])
 output = np.zeros((image.shape[0],image.shape[1],3))
 for r in range(image.shape[0]):
   for c in range(image.shape[1]):
     rgb = image[r,c]
     output[r,c] = np.matmul(transform,rgb) + [0.0625,0.5,0.5]
  output = output * 256 # Convert into clean 0-255 range.
 return output.astype(np.int64)


def RGB_to_CbCr(image):
 # Converts a given RGB image to the YCbCr color space.
 if len(image[0,0]) != 3:
   print("Error: Image is not RGB.")
   return
 output = np.zeros((image.shape[0],image.shape[1],2))
 for r in range(image.shape[0]):
   for c in range(image.shape[1]):
     rgb = image[r,c]
     output[r,c,0] = -0.1482*rgb[0] - 0.2910*rgb[1] + 0.4392*rgb[2] + 0.5
     output[r,c,1] =  0.4392*rgb[0] - 0.3678*rgb[1] - 0.0714*rgb[2] + 0.5
  output = output * 256 # Convert into clean 0-255 range.
 return output.astype(np.int64)


def RGB_to_CbCr_MAT(image):
 # Matrix version of RGB --> CbCr.
 if len(image[0,0]) != 3:
   print("Error: Image is not RGB.")
   return
  transform = np.array([[-0.1482,-0.2910,0.4392],
                       [0.4392,-0.3678,-0.0714]])
 output = np.zeros((image.shape[0],image.shape[1],2))
 for r in range(image.shape[0]):
   for c in range(image.shape[1]):
     rgb = image[r,c]
     output[r,c] = np.matmul(transform,rgb) + [0.5,0.5]
  output = output * 256 # Convert into clean 0-255 range.
 return output.astype(np.int64)
 ### CREATE SKIN COLOR PLANES ###
# Here's the code for dilating/eroding:
def splitKernel(kernel):
 """Splits given kernel into individual offsets from its center.
 Also gives maximum offsets in order left right up down."""
  
 if not isinstance(kernel, np.ndarray):
   print("Error: Invalid kernel. Need numpy array")
   return None
  # Require 2D array.
 if len(kernel.shape) != 2:
   print("Error: Invalid kernel. Need 2D array")
   return None
  height = kernel.shape[0]
 width = kernel.shape[1]
  # Require odd dimensions on kernel. Input pixel at center.
 if (height % 2 != 1) or (width % 2 != 1):
   print("Error: Invalid kernel. Need odd dimensions")
   return None
  center_r = int(height) // 2
 center_c = int(width) // 2
 outputs = []
  # Loop over all pixels
 for r in range(height):
   for c in range(width):
     if kernel[r][c] == 1:
       outputs.append((r - center_r, c - center_c))
      
 return outputs


def maxOffsets(offsets):
 # Do this to avoid if statements on all input pixels.
 left = 0
 right = 0
 up = 0
 down = 0
  # Find max offset in each direction.
 for o in offsets:
   left = max(left, -o[1])
   right = max(right, o[1])
   up = max(up, -o[0])
   down = max(down, o[0])
  
 return left,right,up,down


def dilate(image, kernel, times=1):
 """Dilate the given image using the given kernel.
 Note: Only uses binary images/kernel."""
  # Split the kernel into individual offset coordinates.
 kernel_parts = splitKernel(kernel)
  # Fetch the maximum offsets from any input pixel in our kernel.
 left,right,up,down = maxOffsets(kernel_parts)
  output = np.zeros(image.shape)
  # Main part of image checking, no if statements needed:
 for r in range(0 + up, image.shape[0] - down):
   for c in range(0 + left, image.shape[1] - right):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if image[curr_r][curr_c] == 1:
         output[r][c] = 1
        
 # Now cover four sides and corners:
  # Left side:
 for r in range(0 + up, image.shape[0] - down):
   for c in range(0, left):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_c >= 0:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
          
 # Right side:
 for r in range(0 + up, image.shape[0] - down):
   for c in range(image.shape[1] - right, image.shape[1]):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_c < image.shape[1]:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
  # Top side:
 for r in range(0, up):
   for c in range(0 + left, image.shape[1] - right):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r >= 0:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
          
 # Bottom side:
 for r in range(image.shape[0] - down, image.shape[0]):
   for c in range(0 + left, image.shape[1] - right):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r < image.shape[0]:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
  # Left top corner:
 for r in range(0, up):
   for c in range(0, left):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r >= 0 and curr_c >= 0:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
        
 # Right top corner:
 for r in range(0, up):
   for c in range(image.shape[1] - right, image.shape[1]):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r >= 0 and curr_c < image.shape[1]:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
          
 # Left bottom corner:
 for r in range(image.shape[0] - down, image.shape[0]):
   for c in range(0, left):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r < image.shape[0] and curr_c >= 0:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
          
 # Right bottom corner:
 for r in range(image.shape[0] - down, image.shape[0]):
   for c in range(image.shape[1] - right, image.shape[1]):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r < image.shape[0] and curr_c < image.shape[1]:
         if image[curr_r][curr_c] == 1:
           output[r][c] = 1
          
 if times > 1:
   return dilate(output, kernel, times-1)
 return output


def erode(image, kernel, times=1):
 """Erode the given image using the given kernel.
 Note: Only uses binary images/kernel."""
  # Split the kernel into individual offset coordinates.
 kernel_parts = splitKernel(kernel)
  # Fetch the maximum offsets from any input pixel in our kernel.
 left,right,up,down = maxOffsets(kernel_parts)
  output = np.ones(image.shape)
  # Main part of image checking, no if statements needed:
 for r in range(up, image.shape[0] - down):
   for c in range(left, image.shape[1] - right):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if image[curr_r][curr_c] == 0:
         output[r][c] = 0
        
 # Now cover four sides and corners:
  # Left side:
 for r in range(0 + up, image.shape[0] - down):
   for c in range(0, left):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_c >= 0:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
          
 # Right side:
 for r in range(0 + up, image.shape[0] - down):
   for c in range(image.shape[1] - right, image.shape[1]):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_c < image.shape[1]:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
  # Top side:
 for r in range(0, up):
   for c in range(0 + left, image.shape[1] - right):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r >= 0:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
          
 # Bottom side:
 for r in range(image.shape[0] - down, image.shape[0]):
   for c in range(0 + left, image.shape[1] - right):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r < image.shape[0]:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
  # Left top corner:
 for r in range(0, up):
   for c in range(0, left):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r >= 0 and curr_c >= 0:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
        
 # Right top corner:
 for r in range(0, up):
   for c in range(image.shape[1] - right, image.shape[1]):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r >= 0 and curr_c < image.shape[1]:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
          
 # Left bottom corner:
 for r in range(image.shape[0] - down, image.shape[0]):
   for c in range(0, left):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r < image.shape[0] and curr_c >= 0:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
          
 # Right bottom corner:
 for r in range(image.shape[0] - down, image.shape[0]):
   for c in range(image.shape[1] - right, image.shape[1]):
     for k in kernel_parts:
       curr_r = r + k[0]
       curr_c = c + k[1]
       if curr_r < image.shape[0] and curr_c < image.shape[1]:
         if image[curr_r][curr_c] == 0:
           output[r][c] = 0
  if times > 1:
   return erode(output, kernel, times-1)
 return output


kernel_1x1 = np.array([[1]])
kernel_cross = np.array([[0,1,0],[1,1,1],[0,1,0]])
kernel_3x3 = np.array([[1,1,1],[1,1,1],[1,1,1]])


def createPlane_YMAT(image,box):
 # Input images and sample boxes, outputs dilated color planes.
 ycbcr = RGB_to_YCbCr_MAT(image)
 plane = np.zeros((255,255))
  for r in range(box[0],box[0]+box[2]): # Only scan pixels in the box.
   for c in range(box[1],box[1]+box[2]): # Only scan pixels in the box.
     cb = ycbcr[r,c][1]
     cr = ycbcr[r,c][2]
     plane[cb,cr] = 1
    
 # Uses the box-cross-erode-cross morphological edit, we could change this easily.
 plane = dilate(plane, kernel_cross)
 plane = dilate(plane, kernel_3x3)
 plane = erode(plane, kernel_cross)
 return plane


print("Creating skin color model planes...")
planes = []
for num,image in enumerate(images):
 planes.append(createPlane_YMAT(image,boxes[num]))


### SEGMENT IMAGES ###
def segment_YMAT(image, plane):
 # Segments the given hand colors within the given RGB image.
 ycbcr = RGB_to_YCbCr_MAT(image)
 output = np.zeros(image.shape)
 for r in range(output.shape[0]):
   for c in range(output.shape[1]):
     cb = ycbcr[r,c][1]
     cr = ycbcr[r,c][2]
     if plane[cb,cr] == 1:
       output[r,c] = 1
 return output


print("Done.")