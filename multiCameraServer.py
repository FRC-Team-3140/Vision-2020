#!/usr/bin/env python3
#----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import json
import time
import sys
import cv2

import numpy
import math
from enum import Enum

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, VideoCamera
from networktables import NetworkTablesInstance
import ntcore

class GripPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """
    
    def __init__(self):
        """initializes all values to presets or None if need to be set
        """
        print("grip setting up camera...")
        self.__hsl_threshold_hue = [0.0, 180.0]
        self.__hsl_threshold_saturation = [0.0, 64.5076400679117]
        self.__hsl_threshold_luminance = [165.10791366906474, 255.0]

        self.hsl_threshold_output = None

        print("setting countour finder...")

        self.__find_contours_input = self.hsl_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None
        print("setting up filter pipeline")
        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 200.0
        self.__filter_contours_min_perimeter = 100.0
        self.__filter_contours_min_width = 100.0
        self.__filter_contours_max_width = 1000
        self.__filter_contours_min_height = 0
        self.__filter_contours_max_height = 1000
        self.__filter_contours_solidity = [0.0, 28.692699490662132]
        self.__filter_contours_max_vertices = 1000000
        self.__filter_contours_min_vertices = 0.0
        self.__filter_contours_min_ratio = 2.0
        self.__filter_contours_max_ratio = 3.0

        self.filter_contours_output = None

        print("completed filter pipeline setup")


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSL_Threshold0:
        self.__hsl_threshold_input = source0
        (self.hsl_threshold_output) = self.__hsl_threshold(self.__hsl_threshold_input, self.__hsl_threshold_hue, self.__hsl_threshold_saturation, self.__hsl_threshold_luminance)

        # Step Find_Contours0:
        self.__find_contours_input = self.hsl_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input, self.__find_contours_external_only)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours, self.__filter_contours_min_area, self.__filter_contours_min_perimeter, self.__filter_contours_min_width, self.__filter_contours_max_width, self.__filter_contours_min_height, self.__filter_contours_max_height, self.__filter_contours_solidity, self.__filter_contours_max_vertices, self.__filter_contours_min_vertices, self.__filter_contours_min_ratio, self.__filter_contours_max_ratio)
        
		#find bounding rectangles?
        x,y,w,h=cv2.boundingRect(self.filter_contours_output[0])
        #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

        print("got one")
        return x,y,w,h


    @staticmethod
    def __hsl_threshold(input, hue, sat, lum):
        """Segment an image based on hue, saturation, and luminance ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max luminance.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HLS)
        return cv2.inRange(out, (hue[0], lum[0], sat[0]),  (hue[1], lum[1], sat[1]))

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy =cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        count = 0
        for contour in input_contours:
            count+=1
            x,y,w,h = cv2.boundingRect(contour)
            if (count == 1):
                print("Found one at x = "+str(x)+"!")
                ntinst.getTable('SmartDashboard').putNumber('amos_x',x)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

class GripPipeline2:
    """
    An OpenCV pipeline generated by GRIP.
    """
    
    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__rgb_threshold_red = [0, 43]
        self.__rgb_threshold_green = [101, 255]
        self.__rgb_threshold_blue = [61, 255]

        self.rgb_threshold_output = None

        self.__find_contours_input = self.rgb_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 50
        self.__filter_contours_min_perimeter = 0
        self.__filter_contours_min_width = 0.0
        self.__filter_contours_max_width = 1000
        self.__filter_contours_min_height = 0
        self.__filter_contours_max_height = 1000
        self.__filter_contours_solidity = [0, 53]
        self.__filter_contours_max_vertices = 1000000
        self.__filter_contours_min_vertices = 0
        self.__filter_contours_min_ratio = 0.0
        self.__filter_contours_max_ratio = 1000

        self.filter_contours_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step RGB_Threshold0:
        self.__rgb_threshold_input = source0
        (self.rgb_threshold_output) = self.__rgb_threshold(self.__rgb_threshold_input, self.__rgb_threshold_red, self.__rgb_threshold_green, self.__rgb_threshold_blue)

        # Step Find_Contours0:
        self.__find_contours_input = self.rgb_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input, self.__find_contours_external_only)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours, self.__filter_contours_min_area, self.__filter_contours_min_perimeter, self.__filter_contours_min_width, self.__filter_contours_max_width, self.__filter_contours_min_height, self.__filter_contours_max_height, self.__filter_contours_solidity, self.__filter_contours_max_vertices, self.__filter_contours_min_vertices, self.__filter_contours_min_ratio, self.__filter_contours_max_ratio)

		#find bounding rectangles?
        if(len(self.filter_contours_output) > 0): # if it has something
            #print(cv2.boundingRect(self.filter_contours_output[0]))
            x,y,w,h = cv2.boundingRect(self.filter_contours_output[0])
 
            return x,y,w,h, self.filter_contours_output[0]
        
        return -1,-1,-1,-1, -1

    @staticmethod
    def __rgb_threshold(input, red, green, blue):
        """Segment an image based on color ranges.
        Args:
            input: A BGR numpy.ndarray.
            red: A list of two numbers the are the min and max red.
            green: A list of two numbers the are the min and max green.
            blue: A list of two numbers the are the min and max blue.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)
        return cv2.inRange(out, (red[0], green[0], blue[0]),  (red[1], green[1], blue[1]))

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy =cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output





#   JSON format:
#   {
#       "team": <team number>,
#       "ntmode": <"client" or "server", "client" if unspecified>
#       "cameras": [
#           {
#               "name": <camera name>
#               "path": <path, e.g. "/dev/video0">
#               "pixel format": <"MJPEG", "YUYV", etc>   // optional
#               "width": <video mode width>              // optional
#               "height": <video mode height>            // optional
#               "fps": <video mode fps>                  // optional
#               "brightness": <percentage brightness>    // optional
#               "white balance": <"auto", "hold", value> // optional
#               "exposure": <"auto", "hold", value>      // optional
#               "properties": [                          // optional
#                   {
#                       "name": <property name>
#                       "value": <property value>
#                   }
#               ],
#               "stream": {                              // optional
#                   "properties": [
#                       {
#                           "name": <stream property name>
#                           "value": <stream property value>
#                       }
#                   ]
#               }
#           }
#       ]
#       "switched cameras": [
#           {
#               "name": <virtual camera name>
#               "key": <network table key used for selection>
#               // if NT value is a string, it's treated as a name
#               // if NT value is a double, it's treated as an integer index
#           }
#       ]
#   }

configFile = "/boot/frc.json"

class CameraConfig: pass

team = 3140
server = False
cameraConfigs = []
switchedCameraConfigs = []
cameras = []

def parseError(str):
    """Report parse error."""
    print("config error in '" + configFile + "': " + str, file=sys.stderr)

def readCameraConfig(config):
    """Read single camera configuration."""
    cam = CameraConfig()

    # name
    try:
        cam.name = config["name"]
    except KeyError:
        parseError("could not read camera name")
        return False

    # path
    try:
        cam.path = config["path"]
    except KeyError:
        parseError("camera '{}': could not read path".format(cam.name))
        return False

    # stream properties
    cam.streamConfig = config.get("stream")

    cam.config = config

    cameraConfigs.append(cam)
    return True

def readSwitchedCameraConfig(config):
    """Read single switched camera configuration."""
    cam = CameraConfig()

    # name
    try:
        cam.name = config["name"]
    except KeyError:
        parseError("could not read switched camera name")
        return False

    # path
    try:
        cam.key = config["key"]
    except KeyError:
        parseError("switched camera '{}': could not read key".format(cam.name))
        return False

    switchedCameraConfigs.append(cam)
    return True

def readConfig():
    """Read configuration file."""
    global team
    global server

    # parse file
    try:
        with open(configFile, "rt", encoding="utf-8") as f:
            j = json.load(f)
    except OSError as err:
        print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
        return False

    # top level must be an object
    if not isinstance(j, dict):
        parseError("must be JSON object")
        return False

    # team number
    try:
        team = j["team"]
    except KeyError:
        parseError("could not read team number")
        return False

    # ntmode (optional)
    if "ntmode" in j:
        str = j["ntmode"]
        if str.lower() == "client":
            server = False
        elif str.lower() == "server":
            server = True
        else:
            parseError("could not understand ntmode value '{}'".format(str))

    # cameras
    try:
        cameras = j["cameras"]
    except KeyError:
        parseError("could not read cameras")
        return False
    for camera in cameras:
        if not readCameraConfig(camera):
            return False

    # switched cameras
    if "switched cameras" in j:
        for camera in j["switched cameras"]:
            if not readSwitchedCameraConfig(camera):
                return False

    return True

def startCamera(config):
    """Start running the camera."""
    print("Starting camera '{}' on {}".format(config.name, config.path))
    inst = CameraServer.getInstance()
    camera = UsbCamera(config.name, config.path)
    server = inst.startAutomaticCapture(camera=camera, return_server=True)

    camera.setConfigJson(json.dumps(config.config))
    camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

    if config.streamConfig is not None:
        server.setConfigJson(json.dumps(config.streamConfig))

    return camera

def startSwitchedCamera(config):
    """Start running the switched camera."""
    print("Starting switched camera '{}' on {}".format(config.name, config.key))
    server = CameraServer.getInstance().addSwitchedCamera(config.name)

    def listener(fromobj, key, value, isNew):
        if isinstance(value, float):
            i = int(value)
            if i >= 0 and i < len(cameras):
              server.setSource(cameras[i])
        elif isinstance(value, str):
            for i in range(len(cameraConfigs)):
                if value == cameraConfigs[i].name:
                    server.setSource(cameras[i])
                    break

    NetworkTablesInstance.getDefault().getEntry(config.key).addListener(
        listener,
        ntcore.constants.NT_NOTIFY_IMMEDIATE |
        ntcore.constants.NT_NOTIFY_NEW |
        ntcore.constants.NT_NOTIFY_UPDATE)

    return server

# normalizes from image coords to a points on interval [-1,1]
def normalize(resX, resY, point):
    nx = (2/resX) * (point[0] - resX/2+.5)
    ny = (-2/resY) * (point[1] - resY/2+.5)
    return [nx,ny]

if __name__ == "__main__":
    # constants
    resolutionX = 1280
    resolutionY = 720
    hfov = 70.42 # degrees
    vfov = 43.30
    cameraAngle = 8.32
    cameraHeight = .58 # meters
    targetHeight = 1.02#2.49555 # meters; top midpoint
    targetWidth = 0.99695
    dh = targetHeight - cameraHeight
    #2.794

    if len(sys.argv) >= 2:
        configFile = sys.argv[1]

    # read configuration
    if not readConfig():
        sys.exit(1)

    # start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    if server:
        print("Setting up NetworkTables server")
        ntinst.startServer()
    else:
        print("Setting up NetworkTables client for team {}".format(team))
        ntinst.startClientTeam(team)

    camera = 0
    # start cameras
    for config in cameraConfigs:
        camera = startCamera(config)
        cameras.append(camera)

    # start switched cameras
    for config in switchedCameraConfigs:
        startSwitchedCamera(config)

    print("trying to set up pipeline")
    inst = CameraServer.getInstance()
    gp = GripPipeline2()
    cvSink = inst.getVideo()
    img = numpy.zeros(shape=(resolutionX, resolutionY, 3), dtype=numpy.uint8)
    outputStream = inst.putVideo("Rectangle", resolutionX, resolutionY)
	
    table = ntinst.getTable('Target Info')
    ntinst.getTable('SmartDashboard').putNumber('Exposure', 1)
    lastExposure = 1
	
    print("hi")
	
    # loop forever
    while True:
        _, img = cvSink.grabFrame(img)
        x,y,w,h,c = gp.process(img)
        
        exp = ntinst.getTable('SmartDashboard').getNumber('Exposure',1)
        if(exp != lastExposure):
            lastExposure = exp
            #VideoCamera.setExposureManual(camera,exp)
            camera.setExposureManual(int(exp))
        
        if x != -1:
            cv2.rectangle(img, (x, y), (x+w, h+y), (255, 255, 255), 1)
            
            # determine the most extreme points along the contour (top left/right points)
            extLeft = tuple(c[c[:, :, 0].argmin()][0])
            extRight = tuple(c[c[:, :, 0].argmax()][0])
			
			# draw the extreme points as circles
            cv2.circle(img, extLeft, 8, (0, 0, 255), -1)
            cv2.circle(img, extRight, 8, (0, 0, 255), -1)
            cv2.line(img, extLeft, extRight, (0, 255, 0), 1)
			
            # normalize top left and right points
            nLeft = normalize(resolutionX, resolutionY,[extLeft[0], extLeft[1]])
            nRight = normalize(resolutionX, resolutionY,[extRight[0], extRight[1]])

            # find bearing and elevation angles for each point
            bearingLeft = nLeft[0] * hfov
            bearingRight = nRight[0] * hfov
            elevationLeft = nLeft[1] * vfov
            elevationRight = nRight[1] * vfov
            
            # find distance between each point and the camera
            leftD = abs(dh / (math.tan(math.radians(cameraAngle + elevationLeft))))
            rightD = abs(dh / (math.tan(math.radians(cameraAngle + elevationRight))))

            aLeft = 0
            # we can imagine a triangle with leftD, rightD, and targetWidth as its sides (bird's view)
            # we use law of cosines to solve for the angles of this triangle
            aCamera = abs(bearingLeft-bearingRight)
            table.putNumber('weird num', (-rightD*rightD + leftD*leftD + targetWidth*targetWidth)/(2*targetWidth*leftD))
            if(abs(-rightD*rightD + leftD*leftD + targetWidth*targetWidth)/(2*targetWidth*leftD) <=1):
                aLeft = math.acos((-rightD*rightD + leftD*leftD + targetWidth*targetWidth)/(2*targetWidth*leftD)) #radians
            else:
                print('reeee')
                print((-rightD*rightD + leftD*leftD + targetWidth*targetWidth)/(2*targetWidth*leftD))
                
            
            # find length of above triangle's median
            median = math.sqrt(leftD*leftD + targetWidth*targetWidth - 2*leftD*targetWidth*math.cos(aLeft))
            
            # from that, find the angle of the angle between the median line and leftD with law of consines 
            midAngle = 360/(2*math.pi)* math.acos((-targetWidth*targetWidth+median*median+leftD*leftD)/(2*leftD*median))
            
            # find the true bearing and elevation of the true midpoint of the target
            bearing = bearingLeft + midAngle
            elevation = math.atan(dh/median)
			
			# draw top midpoint (not correct)
            #cv2.circle(img,(int((extLeft[0]+extRight[0])/2), int((extRight[1]+extLeft[1])/2)), 8, (0, 255, 0), -1)

			# get top midpoint normalized
            #topMidpoint = normalize(resolutionX, resolutionY,[(extLeft[0]+extRight[0])/2, (extRight[1]+extLeft[1])/2])
			
            table.putNumber('bearing left', bearingLeft)
            table.putNumber('bearing right', bearingRight)
            table.putNumber('elevationLeft', elevationLeft)
            table.putNumber('elevationRight', elevationRight)
            table.putNumber('bearing', bearing)
            table.putNumber('elevation', elevation)
            table.putNumber('distance', median)
            table.putNumber('left d', leftD)
            table.putNumber('right d', rightD)


  			
        outputStream.putFrame(img)
