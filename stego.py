#!/usr/bin/python
# Stego Dropper For Pentesters v0.1
# Uses https://github.com/RobinDavid/LSB-Steganography

from LSBSteg import LSBSteg
import cv2.cv as cv
import sys
import logging
from optparse import OptionParser


#Hide payload in image, output new stego image
def hide_payload(input_img, payload, output_img):
  carrier = cv.LoadImage(input_img)
  steg = LSBSteg(carrier)
  steg.hideBin(payload)
  steg.saveImage(output_img)


def main():
  # Setup the command line arguments.
  optp = OptionParser()

  # Output verbosity options
  optp.add_option('-q', '--quiet', help='set logging to ERROR',
                  action='store_const', dest='loglevel',
                  const=logging.ERROR, default=logging.INFO)
  optp.add_option('-d', '--debug', help='set logging to DEBUG',
                  action='store_const', dest='loglevel',
                  const=logging.DEBUG, default=logging.INFO)
  optp.add_option('-v', '--verbose', help='set logging to COMM',
                  action='store_const', dest='loglevel',
                  const=5, default=logging.INFO)

  # Image and payload options
  optp.add_option("-i", "--image", dest="input_img",
                  help="The image to embed a payload")
  optp.add_option("-p", "--payload", dest="payload",
                  help="The payload to imbed into an image")
  optp.add_option("-o", "--out", dest="output_img",
                  help="Name of the image to output, with payload embeded steganographicaly")

  opts, args = optp.parse_args()

  # Setup logging
  logging.basicConfig(level=opts.loglevel,
                      format='%(levelname)-8s %(message)s')

  if opts.input_img is None:
    opts.input_img = raw_input("Image to embed a payload: ")
  if opts.payload is None:
    opts.payload = raw_input("Payload to embed in image: ")
  if opts.output_img is None:
    opts.output_img = raw_input("Name of the image to output: ")

  hide_payload(opts.input_img, opts.payload, opts.output_img)


if __name__ == '__main__':
  main()
