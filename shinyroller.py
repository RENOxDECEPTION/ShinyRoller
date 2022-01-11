'''opencv imports'''

import cv2
import numpy as np


'''keyboard control imports'''
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
from pynput.keyboard import Key, Controller
import re

'''threading'''
import threading
from multiprocessing import Process

'''Optional MQTT Publish on Find'''
import paho.mqtt.client as paho
import paho.mqtt.publish as publish
from PIL import Image
import io

import time
import random

'''Save Image of Pokemon to file'''
import os

capture = False
found = False
scanned = False
filename = None
counter = 0

class AdjustmentBars():
    def __init__(self):
        print("Adjustment Bars...")
        # named ites for easy reference
        self.barsWindow = 'Bars'
        self.hl = 'H Low'
        self.hh = 'H High'
        self.sl = 'S Low'
        self.sh = 'S High'
        self.vl = 'V Low'
        self.vh = 'V High'
        cv2.namedWindow(self.barsWindow, cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(self.barsWindow, 300,350)
        # create the sliders
        self.trackbar()
        # set initial values for sliders
        cv2.setTrackbarPos(self.hl, self.barsWindow, 69)
        cv2.setTrackbarPos(self.hh, self.barsWindow, 86)
        cv2.setTrackbarPos(self.sl, self.barsWindow, 66)
        cv2.setTrackbarPos(self.sh, self.barsWindow, 135)
        cv2.setTrackbarPos(self.vl, self.barsWindow, 170)
        cv2.setTrackbarPos(self.vh, self.barsWindow, 219)
    
    def trackbar(self):
        cv2.createTrackbar(self.hl, self.barsWindow, 0, 179, self.nothing)
        cv2.createTrackbar(self.hh, self.barsWindow, 0, 179, self.nothing)
        cv2.createTrackbar(self.sl, self.barsWindow, 0, 255, self.nothing)
        cv2.createTrackbar(self.sh, self.barsWindow, 0, 255, self.nothing)
        cv2.createTrackbar(self.vl, self.barsWindow, 0, 255, self.nothing)
        cv2.createTrackbar(self.vh, self.barsWindow, 0, 255, self.nothing)
    
    def nothing(x, junk):
        pass

class Video():
    global capture, found
    
    def __init__(self):
        self.webcam = cv2.VideoCapture(0)
        #self.webcam = cv2.VideoCapture('Video Examples/Shiny Dialga Brilliant Diamond.avi')
        self.adjbars = AdjustmentBars()
        print("Video Drawing...")
        
        while True:
            # print a message from the main thread
            self.video()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    '''def get_frame(self):
        img = self.webcam.read()
        if img:  # frame captures without errors...
            pass
        return img'''

    def release_video(self):
        self.webcam.release()
        
    def video(self):
            global capture, found, scanned, filename
            ret, frame = self.webcam.read()
            
            dimension = (480,270)
            frame = cv2.resize(frame, dimension,interpolation = cv2.INTER_AREA)
            untouchedframe = cv2.resize(frame, dimension,interpolation = cv2.INTER_AREA)
            hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsvFrame = cv2.GaussianBlur(hsvFrame,(5,5),cv2.BORDER_DEFAULT)

            # read trackbar positions for all
            hul = cv2.getTrackbarPos(self.adjbars.hl, self.adjbars.barsWindow)
            huh = cv2.getTrackbarPos(self.adjbars.hh, self.adjbars.barsWindow)
            sal = cv2.getTrackbarPos(self.adjbars.sl, self.adjbars.barsWindow)
            sah = cv2.getTrackbarPos(self.adjbars.sh, self.adjbars.barsWindow)
            val = cv2.getTrackbarPos(self.adjbars.vl, self.adjbars.barsWindow)
            vah = cv2.getTrackbarPos(self.adjbars.vh, self.adjbars.barsWindow)
            dialga_lower = np.array([hul, sal, val], np.uint8)
            dialga_upper = np.array([huh, sah, vah], np.uint8) 
            #dialga_mask = cv2.inRange(hsvFrame, dialga_lower, dialga_upper)            


            # Morphological Transform, Dilation
            # for each color and bitwise_and operator
            # between imageFrame and mask determines
            # to detect only that particular color
            #kernal = np.ones((5, 5), "uint8")
            
            mask = cv2.inRange(hsvFrame, dialga_lower, dialga_upper)
        
            #dialga_mask = cv2.dilate(dialga_mask, kernal)
            #res_green = cv2.bitwise_and(frame, frame, mask = dialga_mask)            
        
            # Creating contour to track 
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            maskedFrame = cv2.bitwise_and(frame, frame, mask = mask)

            #cv2.imshow("original",frame)
            if capture is True and found is False:
                #wtf why is this affecting frame and untouched frame
                scanned = True
                for pic, contour in enumerate(contours):
                    if capture is True and found is False:
                        area = cv2.contourArea(contour)
                        print(".", end ="")
                        if(area > 1550):
                            print("\nQualifing Area Was: ", area)
                            found = True
                            x, y, w, h = cv2.boundingRect(contour)
                            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, "Shiny Dialga", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
                    #writing image to disk.
            if capture is False and scanned is True:
                filename = os.getcwd()
                filename += "/images/"
                filename += str(counter)
                filename += ".jpg"
                print(os.getcwd())
                print(filename)

                exists = os.path.exists(filename)
                if not exists:
                    print("Writing image...",filename)
                    img = untouchedframe
                    cv2.imwrite(filename, img)
                    scanned = False
                else:
                    pass
                        
            if found is True:
                mqtt()
                quit()
            #cv2.imshow("original2",untouchedframe)            
            #cv2.imshow("original",frame)
            self.lastthree()
            numpy_horizontal_concat = np.concatenate((frame,untouchedframe,maskedFrame), axis=1)
            numpy_horizontal_concat2 = np.concatenate((numpy_horizontal_concat,self.pastone,self.pasttwo, self.pastthree),axis=1)
            
            numpy_vertical_concat = np.concatenate((numpy_horizontal_concat,numpy_horizontal_concat2), axis = 0)
            
            cv2.imshow('=-Shiny Roller-=', numpy_vertical_concat)
            cv2.moveWindow('=-Shiny Roller-=',460,120)

            # Program Termination
            #cv2.imshow("Boxed", frame)

    def lastthree(self):
        global counter
        
        filename = os.getcwd()
        filename += "/images/"
        filename1,filename2,filename3 = filename
        
        filename1 +=counter
        filename1 +=".jpg"
        counter2 = counter
        counter2 -= 1
        filename2 += counter2
        filename2 +=".jpg"
        counter2 -= 2
        filename3 += counter2
        filename3 +=".jpg"
        
        self.pastone = cv2.imread(filename1)
        self.pasttwo = cv2.imread(filename2)
        self.pastthree = cv2.imread(filename3)
        
        self.pastone = cv2.cvtColor(self.pastone, cv2.COLOR_BGR2HSV)
        self.pasttwo = cv2.cvtColor(self.pasttwo, cv2.COLOR_BGR2HSV)
        self.pastthree = cv2.cvtColor(self.pastthree, cv2.COLOR_BGR2HSV)
          
        
        dimension = (480,270)
        
        self.pastone = cv2.resize(self.pastone, dimension,interpolation = cv2.INTER_AREA)
        self.pasttwo = cv2.resize(self.pasttwo, dimension,interpolation = cv2.INTER_AREA)     
        self.pastthree = cv2.resize(self.pastthree, dimension,interpolation = cv2.INTER_AREA)             
            
class Keyboard:
    
    def __init__(self): 
        self.ready = False
        print("Selenium Thread Starting...")
        self.thread = threading.Thread(target=self.initial, args=())
        self.thread.daemon = True
        self.thread.start()
        
    
    def initial(self): 
        #path to seleniumn profile:
        #profile_path = r'C:\Users\John\AppData\Roaming\Mozilla\Firefox\Profiles\x1f79v3u.NewProfile'
        options=Options()
        #options.set_preference('profile', profile_path)
        #path to geckodriver executable.
        #service = Service(r'C:\geckodriver\geckodriver.exe')
        service = Service(r'/home/john/nxbt/geckodriver')

        self.driver = Firefox(service=service, options=options)

        self.URL = "http://127.0.0.1:8000"
        self.keyboard = Controller()       
        self.driver.get(self.URL)
        self.driver.switch_to.window(self.driver.current_window_handle)
        element = self.driver.find_element_by_id("controller-selection")

        #<div id="loader-text" class="surface-lighter">connecting</div>

        if element.text.__contains__("PRO CONTROLLER"):
            time.sleep(1)   
            element.click()
            time.sleep(10)

        element = self.driver.find_element_by_id("loader-text")

        while re.search("connecting", element.text, re.IGNORECASE) or re.search("loading", element.text, re.IGNORECASE):
            time.sleep(1)
            print("Waiting for connection....is something wrong?")   


        element = self.driver.find_element_by_id("controller-underlay-container")
        self.ready = True
        print("Keyboard Ready...")
        #print(element.text)
        
        #These close interface.
        #element.send_keys("w")
        #element.submit()



    def dialgamacro(self):
        global capture, found, scanned
        
        #self.thread = threading.Thread(target=self.initial, args=())
        #self.thread.daemon = True
        #self.thread.start()
        
        while self.ready is not True:
            time.sleep(1)
        
        print("Macro Started...")
        # Press and release space
        self.keyboard.press('l') #press A to select game
        time.sleep(0.3)
        self.keyboard.release('l')
        time.sleep(0.75)
        self.keyboard.press('w') #press w to avoid updating prompt
        time.sleep(0.3)
        self.keyboard.release('w')
        time.sleep(0.75)

        self.keyboard.press('l') #press w to start software
        time.sleep(0.3)
        self.keyboard.release('l')

        time.sleep(2)

        self.keyboard.press('l') #press A to select user profile.
        time.sleep(0.3)
        self.keyboard.release('l')

        time.sleep(24.55)

        self.keyboard.press('l') #press A to enter game main menu
        time.sleep(0.2)
        self.keyboard.release('l')
        time.sleep(0.2)
        self.keyboard.press('l') #press A to enter game main menu
        time.sleep(0.2)
        self.keyboard.release('l')

        time.sleep(3)

        self.keyboard.press('l') #press A to load save game.
        time.sleep(0.2)
        self.keyboard.release('l')
        time.sleep(0.2)
        self.keyboard.press('l') #press A to load save game.
        time.sleep(0.2)
        self.keyboard.release('l')

        time.sleep(13) #wait time to load

        self.keyboard.press('w') #walk up to dialga
        time.sleep(3)
        self.keyboard.release('w')

        time.sleep(3.0) #wait time between walk and "Gugyugubah!"
        

        self.keyboard.press('l') #press A to enter battle.
        time.sleep(0.2)
        self.keyboard.release('l')
        time.sleep(0.2)
        self.keyboard.press('l') #press A to enter battle.
        time.sleep(0.2)
        self.keyboard.release('l')

        time.sleep(0.5)

        self.keyboard.press('l') #press A to enter battle.
        time.sleep(0.2)
        self.keyboard.release('l')
        time.sleep(0.2)
        self.keyboard.press('l') #press A to enter battle.
        time.sleep(0.2)
        self.keyboard.release('l')

        time.sleep(3) #wait time for CV to detect if shiny
        
        '''Need to set capture bool here to check if shiny.'''
        print("Checking Shiny...")
        capture = True
        time.sleep(6)
        if found is False:
            capture = False
            print("\n")
            print("End Checking Shiny...")
            time.sleep(0.5)
            scanned = False

            
            self.keyboard.press('[') #press home to return to main menu.
            time.sleep(0.3)
            self.keyboard.release('[')

            time.sleep(1.2)

            self.keyboard.press('i') #press X to open software menu.
            time.sleep(0.3)
            self.keyboard.release('i')

            time.sleep(0.75)


            self.keyboard.press('l') #press A to close software.
            time.sleep(0.3)
            self.keyboard.release('l')

            time.sleep(1)
        else:
            mqtt()
            quit()
        


def main():
    
    global found, counter
    
    loadcounter()

    print("Defining Keyboard...")
    kb1 = Keyboard()
    print("Starting Video Thread...")
    t1= threading.Thread(target = videocall)
    t1.start() 
    #t2= threading.Thread(target = mqtt)

    while found == False:
        kb1.dialgamacro()
        counter += 1
        mqtt()
        print("Counter: ",counter)
        
         
    
    print("FOUND!!")
    mqtt()
    
    t1.join()
    
    return()

def videocall():
    cam1=Video()
    cam1.release_video()

def mqtt():
    global counter, filename
    
    #counter += 1
    broker="10.0.0.75"
    #define callback
    def on_message(client, userdata, message):
        time.sleep(1)
        print("Received Message =",str(message.payload.decode("utf-8")))

    client= paho.Client("client-001") #create client object client1.on_publish = on_publish #assign function to callback client1.connect(broker,port) #establish connection client1.publish("house/bulb1","on")
    ######Bind function to callback
    client.on_message=on_message
    #####
    print("Connecting to broker:",broker, "...")
    client.connect(broker)#connect
    client.loop_start() #start loop to process received messages
    print("Subscribing...")
    client.subscribe("shinyroller")#subscribe
    time.sleep(2)
    print("Publishing...")
    if found is False:
        client.publish("shinyroller", counter)#publish

    else:    
        client.publish("shinyroller", "found")#publish
    #img = Image.open(filename, mode='r')
    #byteArr = image_to_byte_array(img)
    
    #publish.single('shinyimage', byteArr, qos=1, hostname='10.0.0.75')
    time.sleep(4)
    client.disconnect() #disconnect
    client.loop_stop() #stop loop
    writecounter()


def image_to_byte_array(image:Image):
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format=image.format)
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

def loadcounter():
    global counter
    with open('data.txt') as f:
        lines = f.readlines()
    
    for i in lines:
        if i.isdigit() == True:
            counter += int(i)
    print ("Starting counter is: ", counter)
    
def writecounter():
    global counter
    
    f = open("data.txt", "w")
    f.write(str(counter))
    f.close()
    print("Counter Status Saved...")
if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()


    
