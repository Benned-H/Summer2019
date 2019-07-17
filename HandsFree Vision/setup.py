"""
The main method for the hand segmentation process.
Author: Benned Hedegaard
Last revised: 7/17/2019
"""
import Utility as util

def main():
    camera = util.setupCamera()
    bb_h = 100 # Bounding box height, width
    bb_w = 100
    bb_r = 0
    bb_c = 0
    mask = None
    
    while (True):
        instr = input("What should we do?\n* 1 - Adjust bounding boxes\n* 2 - Adjust resolution\n* 3 - Ready\n* q - Quit program\n")
        if instr == "q":
            print("Program terminated")
            break
        
        # Other cases:
        if instr == "1":
            # Adjust the bounding boxes.
            util.previewText(camera,"Here's the current bounding box:",1)
            if mask == None:
                print("good")
                mask = util.createMask(camera,bb_r,bb_c,bb_h,bb_w)
            util.showMask(camera,mask)
            input("Should we adjust this placement or size? (y/n) \n")
            continue

if __name__ == "__main__":
    main()