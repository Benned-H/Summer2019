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
    box = util.createBox(bb_h,bb_w)
    
    while (True):
        instr = input("What should we do?\n* 1 - Adjust bounding boxes\n* 2 - Adjust resolution\n* 3 - Ready\n* q - Quit program\n")
        if instr == "q":
            print("Program terminated")
            break
        
        # Other cases:
        if instr == "1":
            # Adjust the bounding boxes.
            util.test(camera)
            util.preview(camera)
            break

if __name__ == "__main__":
    main()