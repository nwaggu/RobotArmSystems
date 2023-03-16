#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
import atexit
__target_color = ('red',)

class ColorSensing():

    def __init__(self):
        #Camera setup
        self.my_camera = Camera.Camera()
        self.my_camera.camera_open()
        atexit.register(self.cleanup)
        
        #Size of camera view
        self.resolution = (640, 480)

        self.roi = ()
        #self.rect
        #self.count
        #self.track
        #self.get_roi
        #self.center_list
        #self.__isRunning
        #self.unreachable
        #self.detect_color
        #self.action_finish
        #self.rotation_angle
        #self.last_x, self.last_y
        #self.world_X, self.world_Y
        #self.world_x, self.world_y
        #self.start_count_t1, self.t1
        #self.start_pick_up, self.first_move


    def processImage(self, img):
        
        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        #Check if running?
        #if not __isRunning:
        #    return img
        frame_resize = cv2.resize(img_copy, self.resolution, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #If a recognized object is detected in an area, the area is detected until there is no
        if get_roi and self.start_pick_up:
            get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.resolution)     
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        return frame_lab
        
    def getMaxValidAreas(self, frame_lab):
        area_max = 0
        areaMaxContour = 0
        for i in color_range:
            if i in __target_color:
                detect_color = i
                frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  #Perform bitwise operations on original image and mask
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Close operation
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #Find the outline
                areaMaxContour, area_max = self.getAreaMaxContour(contours)  # Find the largest contour
        return areaMaxContour, area_max
    
    def getLocation(self, areaMaxContour, area_max, img):
        if area_max > 2500:  # Have found the largest area
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))

            roi = getROI(box) #Get roi area
            get_roi = True

            img_centerx, img_centery = getCenter(rect, roi, size, square_length)  # Get the coordinates of the center of the block
            world_x, world_y = convertCoordinate(img_centerx, img_centery, size) #Convert to real world coordinates
            
            
            cv2.drawContours(img, [box], -1, range_rgb[detect_color], 2)
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1) #draw center point
            distance = math.sqrt(pow(world_x - last_x, 2) + pow(world_y - last_y, 2)) #Compare the last coordinates to determine whether to move
            last_x, last_y = world_x, world_y
            track = True
        return img
    
      
    def run(self, img):
        frame_lab = self.processImage(img)
        areaMaxContour, area_max = self.getMaxValidAreas()
        return self.getLocation(areaMaxContour, area_max, img)
        
        
    def start(self):
        while True:
            img = self.my_camera.frame
            if img is not None:
                frame = img.copy()
                Frame = self.run(frame)           
                cv2.imshow('Frame', Frame)
                key = cv2.waitKey(1)
                if key == 27:
                    break
        self.cleanup()
            
    def cleanup(self):  
        self.my_camera.camera_close()
        cv2.destroyAllWindows()
    
    
    def getAreaMaxContour(contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # 历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max  # 返回最大的轮廓
    
test = ColorSensing()
test.start()