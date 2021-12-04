import numpy as np
import cv2
  
  
# Capturing video through webcam
webcam = cv2.VideoCapture(0)
#webcam = cv2.VideoCapture('Shiny Dialga Brilliant Diamond-2.m4v')

# optional argument for trackbars
def nothing(x):
    pass

# named ites for easy reference
barsWindow = 'Bars'
hl = 'H Low'
hh = 'H High'
sl = 'S Low'
sh = 'S High'
vl = 'V Low'
vh = 'V High'

# create window for the slidebars
cv2.namedWindow(barsWindow, flags = cv2.WINDOW_AUTOSIZE)

# create the sliders
cv2.createTrackbar(hl, barsWindow, 0, 179, nothing)
cv2.createTrackbar(hh, barsWindow, 0, 179, nothing)
cv2.createTrackbar(sl, barsWindow, 0, 255, nothing)
cv2.createTrackbar(sh, barsWindow, 0, 255, nothing)
cv2.createTrackbar(vl, barsWindow, 0, 255, nothing)
cv2.createTrackbar(vh, barsWindow, 0, 255, nothing)

# set initial values for sliders
cv2.setTrackbarPos(hl, barsWindow, 0)
cv2.setTrackbarPos(hh, barsWindow, 179)
cv2.setTrackbarPos(sl, barsWindow, 0)
cv2.setTrackbarPos(sh, barsWindow, 255)
cv2.setTrackbarPos(vl, barsWindow, 0)
cv2.setTrackbarPos(vh, barsWindow, 255)

# Start a while loop
while(1):
      
    # Reading the video from the
    # webcam in image frames
    _, imageFrame = webcam.read()
  
    # Convert the imageFrame in 
    # BGR(RGB color space) to 
    # HSV(hue-saturation-value)
    # color space
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # read trackbar positions for all
    hul = cv2.getTrackbarPos(hl, barsWindow)
    huh = cv2.getTrackbarPos(hh, barsWindow)
    sal = cv2.getTrackbarPos(sl, barsWindow)
    sah = cv2.getTrackbarPos(sh, barsWindow)
    val = cv2.getTrackbarPos(vl, barsWindow)
    vah = cv2.getTrackbarPos(vh, barsWindow)
  

    dialga_lower = np.array([hul, sal, val], np.uint8)
    dialga_upper = np.array([huh, sah, vah], np.uint8)
    #dialga_lower = np.array([35, 100, 92], np.uint8)
    #dialga_upper = np.array([100, 150, 130], np.uint8)
    dialga_mask = cv2.inRange(hsvFrame, dialga_lower, dialga_upper)

      
    # Morphological Transform, Dilation
    # for each color and bitwise_and operator
    # between imageFrame and mask determines
    # to detect only that particular color
    kernal = np.ones((5, 5), "uint8")
      
    mask = cv2.inRange(hsvFrame, dialga_lower, dialga_upper)
  
    dialga_mask = cv2.dilate(dialga_mask, kernal)
    res_green = cv2.bitwise_and(imageFrame, imageFrame,
                                mask = dialga_mask)
    
  
    # Creating contour to track 
    contours, hierarchy = cv2.findContours(dialga_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
      
    maskedFrame = cv2.bitwise_and(imageFrame, imageFrame, mask = mask)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if(area > 700):
            x, y, w, h = cv2.boundingRect(contour)
            imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                       (x + w, y + h),
                                       (0, 255, 0), 2)
              
            cv2.putText(imageFrame, "Shiny Dialga", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.0, (0, 255, 0))
    
              
    # Program Termination
    cv2.imshow("Multiple Color Detection in Real-TIme", imageFrame)
    cv2.imshow('Masked', maskedFrame)
    cv2.imshow('Camera', imageFrame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cv2.cap.release()
        cv2.destroyAllWindows()
        break
