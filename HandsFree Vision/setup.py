"""
The main method for the hand segmentation process.
Author: Benned Hedegaard
Last revised: 7/20/2019
"""
import Utility as util

def main():
    camera = util.setupCamera()
    bb_h = 100 # Bounding box height, width
    bb_w = 100
    bb_r = 100
    bb_c = 100
    mask_img = util.createMask(camera,bb_r,bb_c,bb_h,bb_w)
    
    while (True):
        instr = input("What should we do?\n* 1 - Adjust bounding boxes\n* 2 - Ready\n* q - Quit program\n")
        if instr == "q":
            print("Program terminated")
            break
        
        # Other cases:
        if instr == "1": # Adjust the bounding box.
            util.adjustMask(camera,mask_img,bb_h,bb_w,bb_r,bb_c)
        elif instr == "2":
            # Ready case.
            continue
        else:
            print("\nInput not recognized. Please try again.")
            continue

if __name__ == "__main__":
    main()