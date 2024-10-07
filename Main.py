import sys
from sys import platform
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import os
import time

from Detector import Detector
from Interactor import Interactor
from StateSaver import StateSaver
from DrawUI import DrawUI
from utils import (
    Crop, 
    GetAngle, 
    GetCircleDetectorCenter, 
    GetRectDetectorMaxMinY, 
    DetectTrigger
    )
from constants import *

#########################################################

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(2) # GoPro WebCam
#cap = cv2.VideoCapture(1) # OBS Virtual cam

#########################################################

# OpenPose path settings
openpose_path = f"./openpose"
openpose_model_path = openpose_path + f"/models"

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))

try:
    # Windows Import
    if platform == "win32":
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(openpose_path);
        #os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('../../python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e

detector = Detector()
interactor = Interactor()
ui_drawer = DrawUI(detector)
     

def DetectToStart(datum, frame, handed_mode):
    global hand_handle1, hand_handle2, hand_handle3
    global start_time1, start_time2, start_time3

    # interact keypoint
    if interactor.hand_l_point != (0, 0): 
        cv2.circle(frame, interactor.hand_l_point, 10, (255, 0, 0), -1)
    if interactor.hand_r_point != (0, 0): 
        cv2.circle(frame, interactor.hand_r_point, 10, (255, 0, 0), -1)

    select = None # save select option
    handed_select = HANDED_LIST.index(handed_mode)

    new_frame = ui_drawer.cv2putText(frame, "　　　　　請選擇模式\n（將手上的藍點移動至偵測區內）",
                           w//7, h-h//4, (255, 255, 0), 30, 2)

    new_frame = ui_drawer.cv2putText(new_frame, "慣用手：" + handed_mode, w//2.5, h//15, (255, 255, 0), 20, 2)

    # detect area
    detect_area_l_center = GetCircleDetectorCenter(datum, w, h, -1) # left
    new_frame = ui_drawer.DrawCircleDetector(new_frame, detect_area_l_center, DETECTOR_AREA_R, BALL_HAND_LIST[1])
    detect_area_center = GetCircleDetectorCenter(datum, w, h, 0) # top
    new_frame = ui_drawer.DrawCircleDetector(new_frame, detect_area_center, DETECTOR_AREA_R, "返回選擇慣用手")
    detect_area_r_center = GetCircleDetectorCenter(datum, w, h, 1) # right
    new_frame = ui_drawer.DrawCircleDetector(new_frame, detect_area_r_center, DETECTOR_AREA_R, BALL_HAND_LIST[0])

    is_detected_l = (detector.DetectPointInCircleArea(detect_area_l_center, DETECTOR_AREA_R, interactor.hand_l_point)
                     or detector.DetectPointInCircleArea(detect_area_l_center, DETECTOR_AREA_R, interactor.hand_r_point))
    select, new_frame = DetectTrigger(is_detected_l, ui_drawer, new_frame, detect_area_l_center, w, h, handlers_list, 0, select, 1) # Backhand
    
    is_detected_r = (detector.DetectPointInCircleArea(detect_area_r_center, DETECTOR_AREA_R, interactor.hand_l_point)
                     or detector.DetectPointInCircleArea(detect_area_r_center, DETECTOR_AREA_R, interactor.hand_r_point))
    select, new_frame = DetectTrigger(is_detected_r, ui_drawer, new_frame, detect_area_r_center, w, h, handlers_list, 1, select, 0) # Forehand
    
    is_detected_back = (detector.DetectPointInCircleArea(detect_area_center, DETECTOR_AREA_R, interactor.hand_l_point)
                     or detector.DetectPointInCircleArea(detect_area_center, DETECTOR_AREA_R, interactor.hand_r_point))
    handed_select, new_frame = DetectTrigger(is_detected_back, ui_drawer, new_frame, detect_area_center, w, h, handlers_list, 2, handed_select, None) # Back

    return select, new_frame, handed_select

handlers_list = [False, False, False]

def DetectHanded(datum, frame):
    global hand_handle1, hand_handle2
    global start_time1, start_time2

    # interact keypoint
    if interactor.hand_l_point != (0, 0): 
        cv2.circle(frame, interactor.hand_l_point, 10, (255, 0, 0), -1)
    if interactor.hand_r_point != (0, 0): 
        cv2.circle(frame, interactor.hand_r_point, 10, (255, 0, 0), -1)

    select = None # save select option

    new_frame = ui_drawer.cv2putText(frame, "　　請運用雙手來選擇慣用手\n（將手上的藍點移動至偵測區內）",
                           w//7, h-h//4, (255, 255, 0), 30, 2)

    # detect area
    detect_area_l_center = GetCircleDetectorCenter(datum, w, h, -1) # left
    new_frame = ui_drawer.DrawCircleDetector(new_frame, detect_area_l_center, DETECTOR_AREA_R, HANDED_LIST[0])
    detect_area_r_center = GetCircleDetectorCenter(datum, w, h, 1) # right
    new_frame = ui_drawer.DrawCircleDetector(new_frame, detect_area_r_center, DETECTOR_AREA_R, HANDED_LIST[1])

    is_detected_l = (detector.DetectPointInCircleArea(detect_area_l_center, DETECTOR_AREA_R, interactor.hand_l_point)
                     or detector.DetectPointInCircleArea(detect_area_l_center, DETECTOR_AREA_R, interactor.hand_r_point))
    select, new_frame = DetectTrigger(is_detected_l, ui_drawer, new_frame, detect_area_l_center, w, h, handlers_list, 0, select, 0) # left-handed
    
    is_detected_r = (detector.DetectPointInCircleArea(detect_area_r_center, DETECTOR_AREA_R, interactor.hand_l_point)
                     or detector.DetectPointInCircleArea(detect_area_r_center, DETECTOR_AREA_R, interactor.hand_r_point))
    select, new_frame = DetectTrigger(is_detected_r, ui_drawer, new_frame, detect_area_r_center, w, h, handlers_list, 1, select, 1) # right-handed

    return select, new_frame

def DetectToBack(datum, frame, mode_num):
    
    # interact keypoint
    if interactor.hand_l_point != (0, 0): 
        cv2.circle(frame, interactor.hand_l_point, 10, (255, 0, 0), -1)
    if interactor.hand_r_point != (0, 0): 
        cv2.circle(frame, interactor.hand_r_point, 10, (255, 0, 0), -1)

    select = mode_num

    # detect area
    detect_area_center = GetCircleDetectorCenter(datum, w, h, 0) # top
    new_frame = ui_drawer.DrawCircleDetector(frame, detect_area_center, DETECTOR_AREA_R, "返回選擇模式")

    is_detected = (detector.DetectPointInCircleArea(detect_area_center, DETECTOR_AREA_R, interactor.hand_l_point)
                     or detector.DetectPointInCircleArea(detect_area_center, DETECTOR_AREA_R, interactor.hand_r_point))
    select, new_frame = DetectTrigger(is_detected, ui_drawer, new_frame, detect_area_center, w, h, handlers_list, 0, select, None)

    return select, new_frame

def DetectToStartAction(mode, datum, frame, handed_mode):
    global swing_start_point

    # interact keypoint
    if interactor.hand_l_point != (0, 0): 
        cv2.circle(frame, interactor.hand_l_point, 10, (255, 0, 0), -1)
    if interactor.hand_r_point != (0, 0): 
        cv2.circle(frame, interactor.hand_r_point, 10, (255, 0, 0), -1)

    if IS_REFER_KNEE:
        # interact keypoint
        if interactor.knee_l_point != (0, 0): 
            ang_l = GetAngle((int(datum.poseKeypoints[0][9][0]), int(datum.poseKeypoints[0][9][1])), 
                           interactor.knee_l_point, 
                           (int(datum.poseKeypoints[0][11][0]), int(datum.poseKeypoints[0][11][1])))
            frame = ui_drawer.DrawAngle(frame, interactor.knee_l_point, ang_l)
        else: ang_l = 0
        if interactor.knee_r_point != (0, 0):
            ang_r = GetAngle((int(datum.poseKeypoints[0][12][0]), int(datum.poseKeypoints[0][12][1])), 
                           interactor.knee_r_point, 
                           (int(datum.poseKeypoints[0][14][0]), int(datum.poseKeypoints[0][14][1])))
            frame = ui_drawer.DrawAngle(frame, interactor.knee_r_point, ang_r)
        else: ang_r = 0

        frame = ui_drawer.cv2putText(frame, "膝蓋上的數字皆需<={} （皆變綠色字）".format(180-KNEE_ANGLE),
                                     w//5, h-h//4+90, (255, 255, 0), 20, 2)

    frame = ui_drawer.cv2putText(frame, "　　　　　請擺好預備姿勢\n（請將手置於對應紅色區域內並微蹲）",
                                 w//12, h-h//4, (255, 255, 0), 30, 2)
    
    frame = ui_drawer.cv2putText(frame, "已完成次數/總目標次數：{0}/{1}".format(times, TARGET_SWING_TIME),
                                 w//6, h//20, (255, 255, 0), 30, 2)

    frame = ui_drawer.cv2putText(frame, "{}訓練　慣用手：{}".format(mode, handed_mode), w//3.5, h//10, (255, 255, 0), 20, 2)

    poseKeypoints_maxY, poseKeypoints_minY = None, None
    poseKeypoints_X = list()
    offset = 75
    if mode == BALL_HAND_LIST[0]: # Forehand
        if handed_mode == HANDED_LIST[0]: # left-handed
                poseKeypoints_X.append(datum.poseKeypoints[0][5][0]+offset) # right shoulder
                poseKeypoints_X.append(datum.poseKeypoints[0][2][0]-offset) # left shoulder
                poseKeypoints_minY = datum.poseKeypoints[0][2][1] # left shoulder
                poseKeypoints_maxY = datum.poseKeypoints[0][9][1] # left hip
        else: # right_handed
            poseKeypoints_X.append(datum.poseKeypoints[0][2][0]-offset) # left shoulder
            poseKeypoints_X.append(datum.poseKeypoints[0][5][0]+offset) # right shoulder
            poseKeypoints_minY = datum.poseKeypoints[0][5][1] # right shoulder
            poseKeypoints_maxY = datum.poseKeypoints[0][12][1] # right hip
    else: # Backhand
        if handed_mode == HANDED_LIST[0]: # left-handed
            poseKeypoints_X.append(datum.poseKeypoints[0][5][0]) # right shoulder
            poseKeypoints_minY = datum.poseKeypoints[0][5][1] # right shoulder
            poseKeypoints_maxY = datum.poseKeypoints[0][12][1] # right hip
        else: # right_handed
            poseKeypoints_X.append(datum.poseKeypoints[0][2][0]) # left shoulder
            poseKeypoints_minY = datum.poseKeypoints[0][2][1] # left shoulder
            poseKeypoints_maxY = datum.poseKeypoints[0][9][1] # left hip

    # detect area
    detect_area_minY, detect_area_maxY = GetRectDetectorMaxMinY(datum, w, h, poseKeypoints_X, poseKeypoints_minY, poseKeypoints_maxY)

    global swing_start_point
    overlay = frame.copy()
    if handed_mode == HANDED_LIST[0]: # left-handed
        cv2.rectangle(overlay, (poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), (0, 0 , 255), -1) # right
        if mode == BALL_HAND_LIST[1]: # Forehand
            is_detected_l = (detector.DetectPointInRectArea((poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), interactor.hand_l_point)
                                and detector.DetectPointInRectArea((poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), interactor.hand_r_point))
            is_detected_r = True
        else: # Backhand
            cv2.rectangle(overlay, (0, detect_area_minY), (poseKeypoints_X[1], detect_area_maxY), (0, 0 , 255), -1) # left
            is_detected_l = detector.DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[1], detect_area_maxY), interactor.hand_l_point)
            is_detected_r = detector.DetectPointInRectArea((poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), interactor.hand_r_point)

        swing_start_point = interactor.wrist_l_point

    else: # right-handed
        cv2.rectangle(overlay, (0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), (0, 0 , 255), -1) # left
        if mode == BALL_HAND_LIST[1]: # Backhand
            is_detected_l = (detector.DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), interactor.hand_l_point)
                                and detector.DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), interactor.hand_r_point))
            is_detected_r = True
        else: # Forehand
            cv2.rectangle(overlay, (poseKeypoints_X[1], detect_area_minY), (w, detect_area_maxY), (0, 0 , 255), -1) # right
            is_detected_l = detector.DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), interactor.hand_l_point)
            is_detected_r = detector.DetectPointInRectArea((poseKeypoints_X[1], detect_area_minY), (w, detect_area_maxY), interactor.hand_r_point)

        swing_start_point = interactor.wrist_r_point

    is_detected = is_detected_l and is_detected_r

    alpha = 0.3
    new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    if IS_REFER_KNEE:
        is_detected_knee = (detector.DetectAngleInRangle(ang_l, 180, KNEE_ANGLE) 
                            and detector.DetectAngleInRangle(ang_r, 180, KNEE_ANGLE))

        if is_detected and not is_detected_knee:
            new_frame = ui_drawer.cv2putText(new_frame, "請微蹲！", w//3, h//4, (255, 255, 0), 30, 2)
        elif not is_detected and is_detected_knee:
            new_frame = ui_drawer.cv2putText(new_frame, "請將手置於對應紅色區域！", w//5, h//4, (255, 255, 0), 30, 2)

        is_detected = is_detected and is_detected_knee

    if mode == BALL_HAND_LIST[1]: # Forehand
        if handed_mode == HANDED_LIST[0]: # left-handed
            new_frame = ui_drawer.cv2putText(new_frame, " 左&右手\n（持球拍）", 
                                (poseKeypoints_X[0]+w)//2-75, (detect_area_minY+detect_area_maxY)//2-30, 
                                (255, 255, 255), 30, 2)
        else: # right-handed
            new_frame = ui_drawer.cv2putText(new_frame, " 左&右手\n（持球拍）", 
                            poseKeypoints_X[0]//2-75, (detect_area_minY+detect_area_maxY)//2-30, 
                            (255, 255, 255), 30, 2)
    else: # Backhand
        if handed_mode == HANDED_LIST[0]: # left-handed
            new_frame = ui_drawer.cv2putText(new_frame, "　  左手\n（持球拍）", 
                            poseKeypoints_X[1]//2-75, (detect_area_minY+detect_area_maxY)//2-30,
                            (255, 255, 255), 30, 2)
            new_frame = ui_drawer.cv2putText(new_frame, "右手", 
                            (poseKeypoints_X[0]+w)//2-30, (detect_area_minY+detect_area_maxY)//2-30, 
                            (255, 255, 255), 30, 2)
        else: # right-handed
            new_frame = ui_drawer.cv2putText(new_frame, "左手", 
                            poseKeypoints_X[0]//2-30, (detect_area_minY+detect_area_maxY)//2-30,
                            (255, 255, 255), 30, 2)
            new_frame = ui_drawer.cv2putText(new_frame, "　  右手\n（持球拍）", 
                            (poseKeypoints_X[1]+w)//2-75, (detect_area_minY+detect_area_maxY)//2-30, 
                            (255, 255, 255), 30, 2)

    is_ready, new_frame = DetectTrigger(is_detected, ui_drawer, new_frame, 
                                        (w//2, (detect_area_minY+detect_area_maxY)//2-20),
                                        w, h, handlers_list, 1, False, True)

    return is_ready, new_frame

def DetectToEndAction(mode, datum, frame, handed_mode):
    global times

    select = BALL_HAND_LIST.index(mode)
    if mode == BALL_HAND_LIST[0]: # Forehand
        if handed_mode == HANDED_LIST[0]: # left-handed
            detect_area_center = (int(datum.poseKeypoints[0][0][0]) + w//20, 
                                    (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][5][1]))//2)
        else: # right-handed
            detect_area_center = (int(datum.poseKeypoints[0][0][0]) - w//20, 
                                    (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][2][1]))//2)
    else: # Backhand
        if handed_mode == HANDED_LIST[0]: # left-handed
            detect_area_center = (int(datum.poseKeypoints[0][0][0]) - w//20, 
                                    (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][2][1]))//2)
        else: # right-handed
            detect_area_center = (int(datum.poseKeypoints[0][0][0]) + w//20, 
                                    (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][5][1]))//2)
    detect_area_r = 70     

    overlay = frame.copy()
    cv2.circle(overlay, detect_area_center, detect_area_r, (0, 0, 255), -1)
    
    # draw swing curve
    global swing_start_point
    if mode == BALL_HAND_LIST[0]: # Forehand
        if handed_mode == HANDED_LIST[0]: # left-handed
            curve_points = ui_drawer.DrawCurve(overlay, swing_start_point, detect_area_center, 
                                        (w, (swing_start_point[1]+h)//2.3), 
                                        (detect_area_center[0], (swing_start_point[1] + detect_area_center[1])//2))
        else: # right-handed
            curve_points = ui_drawer.DrawCurve(overlay, swing_start_point, detect_area_center, 
                                        (0, (swing_start_point[1]+h)//2.3), 
                                        (detect_area_center[0], (swing_start_point[1] + detect_area_center[1])//2))
    else: # Backhand
        if handed_mode == HANDED_LIST[0]: # left-handed
            curve_points = ui_drawer.DrawCurve(overlay, swing_start_point, detect_area_center, 
                                        (0, (swing_start_point[1]+h)//2.3), 
                                        (detect_area_center[0], (swing_start_point[1] + detect_area_center[1])//2))
        else: # right-handed
            curve_points = ui_drawer.DrawCurve(overlay, swing_start_point, detect_area_center, 
                                        (w, (swing_start_point[1]+h)//2.3), 
                                        (detect_area_center[0], (swing_start_point[1] + detect_area_center[1])//2))
            
    alpha = 0.3
    new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    new_frame = ui_drawer.cv2putText(new_frame, "Target!", 
                           detect_area_center[0]-detect_area_r+15, detect_area_center[1]-15,
                           (255, 255, 255), 30, 1)

    global is_failed
    if (detector.DetectPointInCircleArea(detect_area_center, detect_area_r, interactor.wrist_l_point)
        and detector.DetectPointInCircleArea(detect_area_center, detect_area_r, interactor.wrist_r_point)):
        print("Perfect Trigger!")
        select = 3
        if not is_failed: times += 1
    else:
        s1, s2 = None, None
        if (detector.DetectPointInCircleArea(detect_area_center, detect_area_r, interactor.wrist_l_point)
            or detector.DetectPointInCircleArea(detect_area_center, detect_area_r, interactor.wrist_r_point)):
            s1 = "請雙手到達結束點！（收尾動作）"

        if handed_mode == HANDED_LIST[0]: # left-handed
            if not detector.DetectPointOnCurve(curve_points, interactor.wrist_l_point, SWING_CURVE_DETECT_DIST):
                is_failed = True
                s2 = "請盡可能沿著曲線揮拍！"
        else: # right-handed
            if not detector.DetectPointOnCurve(curve_points, interactor.wrist_r_point, SWING_CURVE_DETECT_DIST):
                is_failed = True
                s2 = "請盡可能沿著曲線揮拍！"
        
        s = s1
        s_w = w//6
        if s1 is None: 
            s = s2
            s_w = w//3
        elif s2 is not None: 
            s += "\n　 " + s2

        if s is not None:
            new_frame = ui_drawer.cv2putText(new_frame, s, s_w, h//4, (255, 255, 0), 30, 2)

    return select, new_frame


    
def main():
    # init OpenPose
    params = dict()
    params["model_folder"] = openpose_model_path
    #params["net_resolution"] = '480x320'
    params["net_resolution"] = '320x480' # if is vertical view
    #params["number_people_max"] = 1
    params["model_pose"] = "BODY_25"
    
    if IS_USE_HAND_TO_SELECT:
        params["hand"] = True
        params["hand_net_resolution"] = '320x320'
    
    opWrapper, datum = op.WrapperPython(), op.Datum()
    opWrapper.configure(params)
    opWrapper.start()

    #cv2.namedWindow("test", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("test", 720, 1080)

    root = tk.Tk()
    root.title("網球揮拍訓練系統")
    root.attributes("-fullscreen", True)
    panel = tk.Frame()
    panel.pack()

    originImg = tk.Label(panel)
    originImg.grid(column=1, row=0)
    poseImg = tk.Label(panel)
    poseImg.grid(column=0, row=0)
    resultImg = tk.Label(panel)
    resultImg.grid(column=2, row=0)

    global handlers_list
    handlers_list = [False, False, False]

    global times, is_failed
    select, handed_select, can_start = None, None, False
    tmp_select = select
    times = 0
    is_failed = False

    reset_handle = False
    reset_time = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret: break

        crop_frame = Crop(frame)
        flip_frame = cv2.flip(crop_frame, 1) # let user see his/her action on the screen can correspond
        global h, w
        (h, w, _) = flip_frame.shape
        #print(w, h)

        datum.cvInputData = flip_frame
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))

        #print("Left hand keypoints: \n" + str(datum.handKeypoints[0]))
        #print("Right hand keypoints: \n" + str(datum.handKeypoints[1]))

        '''if datum.handKeypoints[0] is not None:
            print("Left hand keypoints: \n" + str(datum.handKeypoints[0]))
        if datum.handKeypoints[1] is not None:
            print("Right hand keypoints: \n" + str(datum.handKeypoints[1]))'''

        # output img from model
        result = datum.cvOutputData

        interactor.GetInteractKeypoints(datum)
        if IS_REFER_KNEE: interactor.GetKneeKeypoints(datum)

        try:
            new_frame = flip_frame.copy()
            if handed_select is None:
                handed_select, new_frame = DetectHanded(datum, new_frame)
                StateSaver.SetHandedMode(handed_select)
            else:
                if select is None:
                    times = 0
                    select, new_frame, handed_select = DetectToStart(datum, new_frame, HANDED_LIST[StateSaver.handed_mode_num])
                else:
                    if can_start:
                        if select == 0 or select == 1: # Forehand / Backhand
                            tmp_select = select
                            new_frame = ui_drawer.cv2putText(new_frame, 
                                            "已完成次數/總目標次數：{0}/{1}".format(times, TARGET_SWING_TIME),
                                            w//6, h//20, (255, 255, 0), 30, 2)
                            new_frame = ui_drawer.cv2putText(new_frame, 
                                                "{}訓練　慣用手：{}".format(BALL_HAND_LIST[StateSaver.mode_num], HANDED_LIST[StateSaver.handed_mode_num]), w//3.5, h//10, (255, 255, 0), 20, 2)
                            
                            new_frame = ui_drawer.DrawSwingPath(new_frame)
                            select, new_frame = DetectToEndAction(BALL_HAND_LIST[StateSaver.mode_num], datum, new_frame, HANDED_LIST[StateSaver.handed_mode_num])

                            result_tk = ImageTk.PhotoImage(
                                image=Image.fromarray(
                                    cv2.cvtColor(
                                        cv2.resize(
                                            cv2.addWeighted(result.copy(), 0.5, new_frame.copy(), 0.5, 0), 
                                            (int(w/1.5), int(h/1.5))
                                            ), cv2.COLOR_BGR2RGBA
                                        )
                                    )
                                )
                            resultImg["image"] = result_tk

                        elif select == 3: # standard action
                            can_start = False
                            ui_drawer.ClearSwingPath()
                            select = tmp_select
                            is_failed = False
                            if times == TARGET_SWING_TIME:
                                select = None
                                handed_select = None
                    else:
                        can_start, new_frame = DetectToStartAction(BALL_HAND_LIST[StateSaver.mode_num], datum, new_frame, HANDED_LIST[StateSaver.handed_mode_num]) 
                        select, new_frame = DetectToBack(datum, new_frame, StateSaver.mode_num)
                    
                StateSaver.SetMode(select)

            reset_handle = False
        except Exception as e: # no person in view
            new_frame = datum.cvInputData
            print(e)

            if not reset_handle:
                reset_handle = True
                reset_time = time.time()
            else:
                stay_time = time.time() - reset_time
                if stay_time >= 60:
                    reset_handle = False
                    
                    can_start = False
                    ui_drawer.ClearSwingPath()
                    select = 0
                    handed_select = None

        #cv2.imshow("Origin", new_frame)
        frame_tk = ImageTk.PhotoImage(
            image=Image.fromarray(
                cv2.cvtColor(new_frame, cv2.COLOR_BGR2RGBA)
                )
            )
        originImg["image"] = frame_tk

        #flip_result = cv2.flip(result, 1) # let user see his/her action on the screen can correspond
        #cv2.imshow("test", flip_result)
        pose_tk = ImageTk.PhotoImage(
            image=Image.fromarray(
                cv2.cvtColor(cv2.resize(result.copy(), (int(w/1.5), int(h/1.5))), cv2.COLOR_BGR2RGBA)
                )
            )
        poseImg["image"] = pose_tk        

        # for i in range(len(datum.poseKeypoints)):
        #     print(datum.poseKeypoints[i])

        keycode = cv2.waitKey(1)
        if keycode == ord("q"): 
            print("Escape hit, closing...")
            break

        root.update()
    
    cap.release()

if __name__ == "__main__":
    main()