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
from concurrency import Bus
from CameraSensing import ColorSensing
import concurrent.futures

class ArmMove():
    def __init__(self) -> None:

        #Initializing move servos and position
        self.servo1 = 500
        self.AK = ArmIK()

        
        self.unreachable = False 
        atexit.register(self.cleanup)
    
    #Runs color sorting code
    def colorSort(self, position_bus:Bus ,color_bus:Bus,roi_bus:Bus, start_pickup_bus:Bus):
        #Get targets from Bus
        position = position_bus.read()
        world_X = position[0]
        world_Y = position[1]
        rotation_angle = position[2]
        
        #Get color from Bus
        detect_color = color_bus.read()
        
        start_pick_up = start_pickup_bus.read()
        coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        
        while True:      
            if detect_color != 'None' and start_pick_up:  #If it detects that the block has not moved for a while, start gripping 
                #If no runtime parameter is given, it is automatically calculated and returned by the result
                self.set_rgb(detect_color)
                self.setBuzzer(0.1)
                result = self.AK.setPitchRangeMoving((world_X, world_Y, 7), -90, -90, 0)  
                if result == False:
                    self.unreachable = True
                else:
                    self.unreachable = False
                    time.sleep(result[2]/1000) #If the specified location can be reached, get the running time

                    servo2_angle = getAngle(world_X, world_Y, rotation_angle) #计算夹持器需要旋转的角度
                    Board.setBusServoPulse(1, self.servo1 - 280, 500)  # 爪子张开
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)

                    self.AK.setPitchRangeMoving((world_X, world_Y, 1.5), -90, -90, 0, 1000)
                    time.sleep(1.5)

                    Board.setBusServoPulse(1, self.servo1, 500)  #夹持器闭合
                    time.sleep(0.8)

                    Board.setBusServoPulse(2, 500, 500)
                    self.AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  #机械臂抬起
                    time.sleep(1)

                    result = self.AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0)   
                    time.sleep(result[2]/1000)
                                      
                    servo2_angle = getAngle(coordinate[detect_color][0], coordinate[detect_color][1], -90)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)

                    self.AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], coordinate[detect_color][2] + 3), -90, -90, 0, 500)
                    time.sleep(0.5)
                                       
                    self.AK.setPitchRangeMoving((coordinate[detect_color]), -90, -90, 0, 1000)
                    time.sleep(0.8)

                    Board.setBusServoPulse(1, self.servo1 - 200, 500)  # 爪子张开  ，放下物体
                    time.sleep(0.8)

                    self.AK.setPitchRangeMoving((coordinate[detect_color][0], coordinate[detect_color][1], 12), -90, -90, 0, 800)
                    time.sleep(0.8)

                    self.initMove()  # 回到初始位置
                    time.sleep(1.5)

                    detect_color = 'None'
                    get_roi = False
                    roi_bus.write(get_roi)
                    start_pick_up = False
                    start_pickup_bus.write(start_pick_up)
                    self.set_rgb(detect_color)
            else:
                if _stop:
                    _stop = False
                    Board.setBusServoPulse(1, self.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)
    
    def initMove(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
    
    
    def cleanup(self):
        Board.setBusServoPulse(1, self.servo1 - 70, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.5)
    time.sleep(0.01)
    
    def setBuzzer(timer):
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)
    
    def set_rgb(color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()
            


pos = Bus([0,0,0])
color = Bus('None') 
roia = Bus(False)  
start = Bus(False)

sensor = ColorSensing()
arm = ArmMove()

with concurrent.futures.ThreadPoolExecutor(max_workers =2) as executor:
        eSensor = executor.submit(sensor.run, pos, color, roia, start, 0.05)
        eController = executor.submit(arm.colorSort, pos, color, roia, start, 0.05)
eSensor.result()
eController.result()



