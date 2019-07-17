"""
The main method for the hand segmentation process.
Author: Benned Hedegaard
Last revised: 7/15/2019
"""
import Utility as util

def main():
    camera = util.setupCamera()
    bb_h = 80 # Bounding box height, width
    bb_w = 100
    
    while (True):
        instr = input("What should we do?\n* 1 - Adjust bounding boxes\n* 2 - Adjust resolution\n* 3 - Ready\n* q - Quit program\n")
        if instr == "q":
            print("Program terminated")
            break
        
        # Other cases:
        if instr == "1":
            # Adjust the bounding boxes.
            util.createMask(camera,0,0,bb_h,bb_w)
            util.preview(camera)
            continue

if __name__ == "__main__":
    main()