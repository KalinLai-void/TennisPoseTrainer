import sys
from sys import platform
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk
import os
import math
import time

#########################################################

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(2) # GoPro WebCam
#cap = cv2.VideoCapture(1) # OBS Virtual cam

is_detector_follow_player = True
is_use_hand_to_select = False # if False will use wrist
detect_time = 3

target_times = 5

#########################################################

# OpenPose path settings
openpose_path = f"D:/Lab/Project/openpose-1.7.0/build/python/openpose/Release"
openpose_model_path = f"D:/Lab/Project/openpose-1.7.0/models/"

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

def Crop(image):
    y_nonzero, x_nonzero, _ = np.nonzero(image)
    try:
        new_img = image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]
        # np array to cv 
        new_img_np_array = new_img.astype(np.uint8)
        return np.asarray(new_img_np_array)
    except ValueError:
        return image

def GetDist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 )

def DetectPointInCircleArea(center, radius, point):
    dist = GetDist(center, point)
    if dist <= radius: return True
    else: return False

def DetectPointInRectArea(rect_start_point, rect_end_point, point):
    if point[0] <= rect_start_point[0] or point[0] >= rect_end_point[0]: return False # check X
    if point[1] <= rect_start_point[1] or point[1] >= rect_end_point[1]: return False # check Y
    return True

def cv2putText(img, text, left, top, text_color, text_size, border=0):
    if isinstance(img, np.ndarray):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype("font/msjhbd.ttc", text_size, encoding="utf-8")
    draw.text((left, top), text, font=font_style, fill=text_color, stroke_width=border, stroke_fill=(0, 0, 0))
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def GetInteractKeypoints(datum): # interact keypoint
    global hand_l_point, hand_r_point 
    global wrist_l_point, wrist_r_point
    
    if datum.poseKeypoints is not None:
        wrist_l_point = (int(datum.poseKeypoints[0][4][0]), int(datum.poseKeypoints[0][4][1]))
        wrist_r_point = (int(datum.poseKeypoints[0][7][0]), int(datum.poseKeypoints[0][7][1]))
    else:
        wrist_l_point = (0, 0)
        wrist_r_point = (0, 0)

    if is_use_hand_to_select:
        if datum.handKeypoints[1] is not None: # left hand
            hand_l_point = (int(datum.handKeypoints[1][0][9][0]), int(datum.handKeypoints[1][0][9][1]))
        else:
            hand_l_point = (0, 0)

        if datum.handKeypoints[0] is not None: # right hand
            hand_r_point = (int(datum.handKeypoints[0][0][9][0]), int(datum.handKeypoints[0][0][9][1]))
        else:
            hand_r_point = (0, 0)
    else:
        hand_l_point = wrist_l_point
        hand_r_point = wrist_r_point

def DetectToStart(datum, frame):
    global handed_select
    global hand_handle1, hand_handle2, hand_handle3
    global start_time1, start_time2, start_time3

    global hand_l_point, hand_r_point # interact keypoint
    if hand_l_point != (0, 0): cv2.circle(frame, hand_l_point, 10, (255, 0, 0), -1)
    if hand_r_point != (0, 0): cv2.circle(frame, hand_r_point, 10, (255, 0, 0), -1)

    select = None # save select option

    new_frame = cv2putText(frame, "　　　　　請選擇模式\n（將手上的藍點移動至偵測區內）",
                           w//7, h-h//4, (255, 255, 0), 30, 2)

    new_frame = cv2putText(new_frame, "慣用手：" + handed_select, w//2.5, h//15, (255, 255, 0), 20, 2)

    # detect area
    if is_detector_follow_player and datum.poseKeypoints is not None: # right
        if is_use_hand_to_select:
            detect_area_r_center = (int(datum.poseKeypoints[0][12][0])+w//4, int(datum.poseKeypoints[0][12][1]))
        else:
            detect_area_r_center = (int(datum.poseKeypoints[0][12][0])+w//6, int(datum.poseKeypoints[0][12][1])-h//30)
    else: detect_area_r_center = (w//2+w//4, h//2) 
    detect_area_r_r = 30
    cv2.circle(new_frame, detect_area_r_center, detect_area_r_r, (0, 0, 255), 5) 
    new_frame = cv2putText(new_frame, "正\n手\n拍", 
                           detect_area_r_center[0]+detect_area_r_r*2, detect_area_r_center[1]-detect_area_r_r*2, 
                           (255, 0, 0), 30, 2)

    if is_detector_follow_player and datum.poseKeypoints is not None: # left
        if is_use_hand_to_select:
            detect_area_l_center = (int(datum.poseKeypoints[0][9][0])-w//4, int(datum.poseKeypoints[0][9][1]))
        else:
            detect_area_l_center = (int(datum.poseKeypoints[0][9][0])-w//6, int(datum.poseKeypoints[0][9][1])-h//30)
    else: detect_area_l_center = (w//4, h//2)
    detect_area_l_r = 30
    cv2.circle(new_frame, detect_area_l_center, detect_area_l_r, (0, 0, 255), 5) 
    new_frame = cv2putText(new_frame, "反\n手\n拍", 
                           detect_area_l_center[0]-detect_area_l_r*3, detect_area_l_center[1]-detect_area_l_r*2, 
                           (255, 0, 0), 30, 2)

    if is_detector_follow_player and datum.poseKeypoints is not None: # top
        if is_use_hand_to_select:
            detect_area_center = (int(datum.poseKeypoints[0][0][0]), int(datum.poseKeypoints[0][0][1])-h//8)
        else:
            detect_area_center = (int(datum.poseKeypoints[0][0][0]), int(datum.poseKeypoints[0][0][1])-h//10)
    else: detect_area_center = (w//2, h//5) 
    detect_area_r = 30
    cv2.circle(new_frame, detect_area_center, detect_area_r, (0, 0, 255), 5) 
    new_frame = cv2putText(new_frame, "返回選擇慣用手", 
                           detect_area_center[0]-detect_area_r*3.5, detect_area_center[1]-detect_area_r*2-15, 
                           (255, 0, 0), 30, 2)

    # left
    if (DetectPointInCircleArea(detect_area_l_center, detect_area_l_r, hand_l_point)
        or DetectPointInCircleArea(detect_area_l_center, detect_area_l_r, hand_r_point)):
        if not hand_handle1:
            hand_handle1 = True
            start_time1 = time.time()
        elif not hand_handle2 and not hand_handle3:
            stay_time = time.time() - start_time1
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    detect_area_l_center[0]-10, detect_area_l_center[1]-detect_area_l_r+5,
                                    (255, 0, 0), 30, 1)
            if stay_time >= detect_time:
                print("Trigger Left Area!")
                select = "反手拍"
                hand_handle1 = False
        else:
            new_frame = cv2putText(new_frame, "請將手離開其中一個偵測區！", w//6, h//3, (255, 255, 0), 30, 2)
            start_time1 = time.time()
    else: # cancel
        hand_handle1 = False

    # right
    if (DetectPointInCircleArea(detect_area_r_center, detect_area_r_r, hand_r_point)
        or DetectPointInCircleArea(detect_area_r_center, detect_area_r_r, hand_l_point)):
        if not hand_handle2:
            hand_handle2 = True
            start_time2 = time.time()
        elif not hand_handle1 and not hand_handle3:
            stay_time = time.time() - start_time2
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    detect_area_r_center[0]-10, detect_area_r_center[1]-detect_area_r_r+5,
                                    (255, 0, 0), 30, 1)
            if stay_time >= detect_time:
                print("Trigger Right Area!")
                select = "正手拍"
                hand_handle2 = False
        else:
            new_frame = cv2putText(new_frame, "請將手離開其中一個偵測區！", w//6, h//3, (255, 255, 0), 30, 2)
            start_time2 = time.time()
    else: # cancel
        hand_handle2 = False

    # top
    if (DetectPointInCircleArea(detect_area_center, detect_area_r, hand_l_point)
        or DetectPointInCircleArea(detect_area_center, detect_area_r, hand_r_point)):
        if not hand_handle3:
            hand_handle3 = True
            start_time3 = time.time()
        elif not hand_handle1 and not hand_handle2:
            stay_time = time.time() - start_time3
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    detect_area_center[0]-10, detect_area_center[1]-detect_area_r+5,
                                    (255, 0, 0), 30, 1)
            if stay_time >= detect_time:
                print("Trigger!")
                select = None
                handed_select = None
                hand_handle1 = False
        else:
            new_frame = cv2putText(new_frame, "請將手離開其中一個偵測區！", w//6, h//3, (255, 255, 0), 30, 2)
            start_time3 = time.time()
    else: # cancel
        hand_handle3 = False

    return select, new_frame

def DetectHanded(datum, frame):
    global hand_handle1, hand_handle2
    global start_time1, start_time2

    global hand_l_point, hand_r_point # interact keypoint
    if hand_l_point != (0, 0): cv2.circle(frame, hand_l_point, 10, (255, 0, 0), -1)
    if hand_r_point != (0, 0): cv2.circle(frame, hand_r_point, 10, (255, 0, 0), -1)

    select = None # save select option

    new_frame = cv2putText(frame, "　　請運用雙手來選擇慣用手\n（將手上的藍點移動至偵測區內）",
                           w//7, h-h//4, (255, 255, 0), 30, 2)

    # detect area
    if is_detector_follow_player and datum.poseKeypoints is not None: # right
        if is_use_hand_to_select:
            detect_area_r_center = (int(datum.poseKeypoints[0][12][0])+w//4, int(datum.poseKeypoints[0][12][1]))
        else:
            detect_area_r_center = (int(datum.poseKeypoints[0][12][0])+w//6, int(datum.poseKeypoints[0][12][1])-h//30)
    else: detect_area_r_center = (w//2+w//4, h//2) 
    detect_area_r_r = 30
    cv2.circle(new_frame, detect_area_r_center, detect_area_r_r, (0, 0, 255), 5) 
    new_frame = cv2putText(new_frame, "右\n撇\n子", 
                           detect_area_r_center[0]+detect_area_r_r*2, detect_area_r_center[1]-detect_area_r_r*2, 
                           (255, 0, 0), 30, 2)

    if is_detector_follow_player and datum.poseKeypoints is not None: # left
        if is_use_hand_to_select:
            detect_area_l_center = (int(datum.poseKeypoints[0][9][0])-w//4, int(datum.poseKeypoints[0][12][1]))
        else:
            detect_area_l_center = (int(datum.poseKeypoints[0][9][0])-w//6, int(datum.poseKeypoints[0][12][1])-h//30)
    else: detect_area_l_center = (w//4, h//2)
    detect_area_l_r = 30
    cv2.circle(new_frame, detect_area_l_center, detect_area_l_r, (0, 0, 255), 5) 
    new_frame = cv2putText(new_frame, "左\n撇\n子", 
                           detect_area_l_center[0]-detect_area_l_r*3, detect_area_l_center[1]-detect_area_l_r*2, 
                           (255, 0, 0), 30, 2)

    # left
    if (DetectPointInCircleArea(detect_area_l_center, detect_area_l_r, hand_l_point)
        or DetectPointInCircleArea(detect_area_l_center, detect_area_l_r, hand_r_point)):
        if not hand_handle1:
            hand_handle1 = True
            start_time1 = time.time()
        elif not hand_handle2:
            stay_time = time.time() - start_time1
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    detect_area_l_center[0]-10, detect_area_l_center[1]-detect_area_l_r+5,
                                    (255, 0, 0), 30, 1)
            if stay_time >= detect_time:
                print("Trigger Left Area!")
                select = "左撇子"
                hand_handle1 = False
        else:
            new_frame = cv2putText(new_frame, "請將手離開其中一個偵測區！", w//6, h//4, (255, 255, 0), 30, 2)
            start_time1 = time.time()
    else: # cancel
        hand_handle1 = False

    # right
    if (DetectPointInCircleArea(detect_area_r_center, detect_area_r_r, hand_r_point)
        or DetectPointInCircleArea(detect_area_r_center, detect_area_r_r, hand_l_point)):
        if not hand_handle2:
            hand_handle2 = True
            start_time2 = time.time()
        elif not hand_handle1:
            stay_time = time.time() - start_time2
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    detect_area_r_center[0]-10, detect_area_r_center[1]-detect_area_r_r+5,
                                    (255, 0, 0), 30, 1)
            if stay_time >= detect_time:
                print("Trigger Right Area!")
                select = "右撇子"
                hand_handle2 = False
        else:
            new_frame = cv2putText(new_frame, "請將手離開其中一個偵測區！", w//6, h//4, (255, 255, 0), 30, 2)
            start_time2 = time.time()
    else: # cancel
        hand_handle2 = False

    return select, new_frame

def DetectToBack(datum, frame, mode):
    global hand_handle1, start_time1
    
    global hand_l_point, hand_r_point # interact keypoint
    if hand_l_point != (0, 0): cv2.circle(frame, hand_l_point, 10, (255, 0, 0), -1)
    if hand_r_point != (0, 0): cv2.circle(frame, hand_r_point, 10, (255, 0, 0), -1)

    select = mode

    # detect area
    if is_detector_follow_player and datum.poseKeypoints is not None:
        if is_use_hand_to_select:
            detect_area_center = (int(datum.poseKeypoints[0][0][0]), int(datum.poseKeypoints[0][0][1])-h//8)
        else:
            detect_area_center = (int(datum.poseKeypoints[0][0][0]), int(datum.poseKeypoints[0][0][1])-h//10)
    else: detect_area_center = (w//2, h//5) 
    detect_area_r = 30
    cv2.circle(frame, detect_area_center, detect_area_r, (0, 0, 255), 5) 
    new_frame = cv2putText(frame, "返回選擇模式", 
                           detect_area_center[0]-detect_area_r*3, detect_area_center[1]-detect_area_r*2-15, 
                           (255, 0, 0), 30, 2)

    if (DetectPointInCircleArea(detect_area_center, detect_area_r, hand_l_point)
        or DetectPointInCircleArea(detect_area_center, detect_area_r, hand_r_point)):
        if not hand_handle1:
            hand_handle1 = True
            start_time1 = time.time()
        elif not hand_handle2:
            stay_time = time.time() - start_time1
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    detect_area_center[0]-10, detect_area_center[1]-detect_area_r+5,
                                    (255, 0, 0), 30, 1)
            if stay_time >= detect_time:
                print("Trigger!")
                select = None
                hand_handle1 = False
    else: # cancel
        hand_handle1 = False

    return select, new_frame

def DetectToStartAction(mode, datum, frame):
    global handed_select
    global hand_handle2, start_time2
    global swing_start_point

    global hand_l_point, hand_r_point # interact keypoint
    if hand_l_point != (0, 0): cv2.circle(frame, hand_l_point, 10, (255, 0, 0), -1)
    if hand_r_point != (0, 0): cv2.circle(frame, hand_r_point, 10, (255, 0, 0), -1)

    frame = cv2putText(frame, "　　　　請擺好預備姿勢\n  （請將手置於對應紅色區域內）",
                           w//7, h-h//4, (255, 255, 0), 30, 2)
    
    frame = cv2putText(frame, "已完成次數/總目標次數：{0}/{1}".format(times, target_times),
                           w//6, h//20, (255, 255, 0), 30, 2)

    frame = cv2putText(frame, "{}訓練　慣用手：{}".format(select, handed_select), w//3.5, h//10, (255, 255, 0), 20, 2)

    poseKeypoints_maxY, poseKeypoints_minY = None, None
    poseKeypoints_X = list()
    offset = 75
    match mode:
        case "正手拍":
            if handed_select == "左撇子":
                    poseKeypoints_X.append(datum.poseKeypoints[0][5][0]+offset) # right shoulder
                    poseKeypoints_X.append(datum.poseKeypoints[0][2][0]-offset) # left shoulder
                    poseKeypoints_minY = datum.poseKeypoints[0][2][1] # left shoulder
                    poseKeypoints_maxY = datum.poseKeypoints[0][9][1] # left hip
            else:
                poseKeypoints_X.append(datum.poseKeypoints[0][2][0]-offset) # left shoulder
                poseKeypoints_X.append(datum.poseKeypoints[0][5][0]+offset) # right shoulder
                poseKeypoints_minY = datum.poseKeypoints[0][5][1] # right shoulder
                poseKeypoints_maxY = datum.poseKeypoints[0][12][1] # right hip
        case "反手拍":
            if handed_select == "左撇子":
                poseKeypoints_X.append(datum.poseKeypoints[0][5][0]) # right shoulder
                poseKeypoints_minY = datum.poseKeypoints[0][5][1] # right shoulder
                poseKeypoints_maxY = datum.poseKeypoints[0][12][1] # right hip
            else:
                poseKeypoints_X.append(datum.poseKeypoints[0][2][0]) # left shoulder
                poseKeypoints_minY = datum.poseKeypoints[0][2][1] # left shoulder
                poseKeypoints_maxY = datum.poseKeypoints[0][9][1] # left hip

    # detect area
    if is_detector_follow_player and datum.poseKeypoints is not None:
        for i in range(len(poseKeypoints_X)):
            poseKeypoints_X[i] = int(poseKeypoints_X[i])
        detect_area_minY = int(poseKeypoints_minY)
        detect_area_maxY = int(poseKeypoints_maxY)
    else: 
        poseKeypoints_X[0] = w//3
        if len(poseKeypoints_X) == 2: poseKeypoints_X[1] = w-w//3
        detect_area_minY = h//3
        detect_area_maxY = h//2

    overlay = frame.copy()
    if handed_select == "左撇子":
        cv2.rectangle(overlay, (poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), (0, 0 , 255), -1) # right
        if mode == "反手拍":
            is_detected_l = (DetectPointInRectArea((poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), hand_l_point)
                                and DetectPointInRectArea((poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), hand_r_point))
            is_detected_r = True
        else:
            cv2.rectangle(overlay, (0, detect_area_minY), (poseKeypoints_X[1], detect_area_maxY), (0, 0 , 255), -1) # left
            is_detected_l = DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[1], detect_area_maxY), hand_l_point)
            is_detected_r = DetectPointInRectArea((poseKeypoints_X[0], detect_area_minY), (w, detect_area_maxY), hand_r_point)

        swing_start_point = wrist_l_point

    else:
        cv2.rectangle(overlay, (0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), (0, 0 , 255), -1) # left
        if mode == "反手拍":
            is_detected_l = (DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), hand_l_point)
                                and DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), hand_r_point))
            is_detected_r = True
        else:
            cv2.rectangle(overlay, (poseKeypoints_X[1], detect_area_minY), (w, detect_area_maxY), (0, 0 , 255), -1) # right
            is_detected_l = DetectPointInRectArea((0, detect_area_minY), (poseKeypoints_X[0], detect_area_maxY), hand_l_point)
            is_detected_r = DetectPointInRectArea((poseKeypoints_X[1], detect_area_minY), (w, detect_area_maxY), hand_r_point)

        swing_start_point = wrist_r_point

    alpha = 0.3
    new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    if mode == "反手拍":
        if handed_select == "左撇子":
            new_frame = cv2putText(new_frame, " 左&右手\n（持球拍）", 
                                (poseKeypoints_X[0]+w)//2-75, (detect_area_minY+detect_area_maxY)//2-30, 
                                (255, 255, 255), 30, 2)
        else:
            new_frame = cv2putText(new_frame, " 左&右手\n（持球拍）", 
                            poseKeypoints_X[0]//2-75, (detect_area_minY+detect_area_maxY)//2-30, 
                            (255, 255, 255), 30, 2)
    else:
        if handed_select == "左撇子":
            new_frame = cv2putText(new_frame, "　  左手\n（持球拍）", 
                            poseKeypoints_X[1]//2-75, (detect_area_minY+detect_area_maxY)//2-30,
                            (255, 255, 255), 30, 2)
            new_frame = cv2putText(new_frame, "右手", 
                            (poseKeypoints_X[0]+w)//2-30, (detect_area_minY+detect_area_maxY)//2-30, 
                            (255, 255, 255), 30, 2)
        else:
            new_frame = cv2putText(new_frame, "左手", 
                            poseKeypoints_X[0]//2-30, (detect_area_minY+detect_area_maxY)//2-30,
                            (255, 255, 255), 30, 2)
            new_frame = cv2putText(new_frame, "　  右手\n（持球拍）", 
                            (poseKeypoints_X[1]+w)//2-75, (detect_area_minY+detect_area_maxY)//2-30, 
                            (255, 255, 255), 30, 2)

    if (is_detected_l and is_detected_r):
        if not hand_handle2:
            hand_handle2 = True
            start_time2 = time.time()
        else:
            stay_time = time.time() - start_time2
            new_frame = cv2putText(new_frame, "{}".format(int(detect_time-stay_time+1)), 
                                    w//2, (detect_area_minY+detect_area_maxY)//2-20,
                                    (255, 255, 255), 40, 1)
            if stay_time >= detect_time:
                print("Trigger!")
                hand_handle2 = False
                return True, new_frame
    else: # cancel
        hand_handle2 = False

    return False, new_frame

def DetectToEndAction(mode, datum, frame):
    global times, handed_select
    global swing_start_point

    global wrist_l_point, wrist_r_point # interact keypoint
    select = mode
    match mode:
        case "正手拍": 
            if handed_select == "左撇子":
                detect_area_center = (int(datum.poseKeypoints[0][0][0]) + w//10, 
                                      (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][5][1]))//2)
            else:
                detect_area_center = (int(datum.poseKeypoints[0][0][0]) - w//10, 
                                      (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][2][1]))//2)
        case "反手拍":
            if handed_select == "左撇子":
                detect_area_center = (int(datum.poseKeypoints[0][0][0]) - w//10, 
                                      (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][2][1]))//2)
            else:
                detect_area_center = (int(datum.poseKeypoints[0][0][0]) + w//10, 
                                      (int(datum.poseKeypoints[0][0][1])+int(datum.poseKeypoints[0][5][1]))//2)
    detect_area_r = 70     

    overlay = frame.copy()
    cv2.circle(overlay, detect_area_center, detect_area_r, (0, 0, 255), -1)

    alpha = 0.3
    new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    new_frame = cv2putText(new_frame, "Target!", 
                           detect_area_center[0]-detect_area_r+15, detect_area_center[1]-15,
                           (255, 255, 255), 30, 1)

    if (DetectPointInCircleArea(detect_area_center, detect_area_r, wrist_l_point)
        and DetectPointInCircleArea(detect_area_center, detect_area_r, wrist_r_point)):
        print("Perfect Trigger!")
        select = "結果"
        times += 1
    else:
        match mode:
            case "正手拍":
                pass
            case "反手拍":
                pass

    return select, new_frame

def DrawSwingPath(frame, mode):
    global path_list
    global wrist_l_point, wrist_r_point # interact keypoint
    match mode:
        case "正手拍": 
            if handed_select == "左撇子": wrist_point = wrist_l_point
            else: wrist_point = wrist_r_point
        case "反手拍": 
            if handed_select == "左撇子": wrist_point = wrist_r_point
            else: wrist_point = wrist_l_point

    cv2.circle(frame, wrist_point, 10, (255, 0, 0), -1)
    path_list.append(wrist_point)

    points = np.array(path_list)
    cv2.polylines(frame, pts=[points], isClosed=False, color=(0, 0, 0), thickness=15) # border
    cv2.polylines(frame, pts=[points], isClosed=False, color=(255, 255, 255), thickness=10) #fill
    return frame
    
if __name__ == "__main__":
    # init OpenPose
    params = dict()
    params["model_folder"] = openpose_model_path
    #params["net_resolution"] = '480x320'
    params["net_resolution"] = '320x480' # if is vertical view
    #params["number_people_max"] = 1
    params["model_pose"] = "BODY_25"
    
    if is_use_hand_to_select:
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

    hand_handle1, hand_handle2, hand_handle3 = False, False, False
    start_time1, start_time2, start_time3 = 0, 0, 0
    select, handed_select, can_start, continue_or_back = None, None, False, None
    tmp_select = select
    path_list = list()
    times = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret: break

        crop_frame = Crop(frame)
        flip_frame = cv2.flip(crop_frame, 1) # let user see his/her action on the screen can correspond
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

        # ouput img from model
        result = datum.cvOutputData

        GetInteractKeypoints(datum)

        new_frame = flip_frame.copy()
        if handed_select is None:
            handed_select, new_frame = DetectHanded(datum, new_frame)
        else:
            if select is None:
                times = 0
                select, new_frame = DetectToStart(datum, new_frame)
            else:
                if can_start:
                    if select == "正手拍" or select == "反手拍":
                        tmp_select = select
                        new_frame = cv2putText(new_frame, 
                                           "已完成次數/總目標次數：{0}/{1}".format(times, target_times),
                                           w//6, h//20, (255, 255, 0), 30, 2)
                        new_frame = cv2putText(new_frame, 
                                               "{}訓練　慣用手：{}".format(select, handed_select), w//3.5, h//10, (255, 255, 0), 20, 2)
                        
                        new_frame = DrawSwingPath(new_frame, select)
                        select, new_frame = DetectToEndAction(select, datum, new_frame)

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

                    elif select == "結果":
                        can_start = False
                        path_list.clear()
                        select = tmp_select
                        if times == target_times:
                            select = None
                            handed_select = None
                else:
                    can_start, new_frame = DetectToStartAction(select, datum, new_frame) 
                    select, new_frame = DetectToBack(datum, new_frame, select)

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