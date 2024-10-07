import math
import numpy as np
import time

from constants import *

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

def GetAngle(point1,point2,point3):
    a=math.sqrt((point2[0]-point3[0])*(point2[0]-point3[0])+(point2[1]-point3[1])*(point2[1] - point3[1]))
    b=math.sqrt((point1[0]-point3[0])*(point1[0]-point3[0])+(point1[1]-point3[1])*(point1[1] - point3[1]))
    c=math.sqrt((point1[0]-point2[0])*(point1[0]-point2[0])+(point1[1]-point2[1])*(point1[1]-point2[1]))

    if (-2*a*c)!=0:
        if (b*b-a*a-c*c)/(-2*a*c)<-1 or (b*b-a*a-c*c)/(-2*a*c)>1:
            B=180
            #keepangle.append(B)         
        else:
            B=round(math.degrees(math.acos((b*b-a*a-c*c)/(-2*a*c)))) #取得角度
    return B

def GetCircleDetectorCenter(datum, w, h, side=0): # side = -1(left), 0 (top), 1 (right)
    if side == 1 or side == -1: # right / left
        if IS_DETECTOR_FOLLOW_PLAYER and datum.poseKeypoints is not None: # right
            keypoint = datum.poseKeypoints[0][12] if side == 1 else datum.poseKeypoints[0][9]
            if IS_USE_HAND_TO_SELECT:
                center = (int(keypoint[0])+(w//4*side), int(keypoint[1]))
            else:
                center = (int(keypoint[0])+(w//6*side), int(keypoint[1])-h//30)
        else: center = (w//2+(w//4*side), h//2)
    elif side == 0: # top
        if IS_DETECTOR_FOLLOW_PLAYER and datum.poseKeypoints is not None: # top
            keypoint = datum.poseKeypoints[0][0]
            if IS_USE_HAND_TO_SELECT:
                center = (int(keypoint[0]), int(keypoint[1])-h//8)
            else:
                center = (int(keypoint[0]), int(keypoint[1])-h//10)
        else: center = (w//2, h//5)
    else:
        return None

    return center

def GetRectDetectorMaxMinY(datum, w, h, poseKeypoints_X, poseKeypoints_minY, poseKeypoints_maxY):
    if IS_DETECTOR_FOLLOW_PLAYER and datum.poseKeypoints is not None:
        for i in range(len(poseKeypoints_X)):
            poseKeypoints_X[i] = int(poseKeypoints_X[i])
        detect_area_minY = int(poseKeypoints_minY)
        detect_area_maxY = int(poseKeypoints_maxY)
    else: 
        poseKeypoints_X[0] = w//3
        if len(poseKeypoints_X) == 2: poseKeypoints_X[1] = w-w//3
        detect_area_minY = h//3
        detect_area_maxY = h//2
    return detect_area_minY, detect_area_maxY

start_time = 0
def DetectTrigger(is_detected, ui_drawer, frame, center, w, h, handlers_list, target_handler_num, ori_value, value):
    global start_time
    ret = ori_value
    new_frame = frame
    if is_detected:
        if not handlers_list[target_handler_num]:
            handlers_list[target_handler_num] = True
            start_time = time.time()
        else:
            can_trigger = True
            for i in range(len(handlers_list)):
                if i != target_handler_num:
                    if handlers_list[i] == True:
                        can_trigger = False
                        break

            if can_trigger:
                stay_time = time.time() - start_time
                if ui_drawer is not None:
                    new_frame = ui_drawer.cv2putText(new_frame, "{}".format(int(DETECT_STAY_TIME-stay_time+1)), 
                                                    center[0]-10, center[1]-DETECTOR_AREA_R+5,
                                                    (255, 255, 255), 30, 2)
                if stay_time >= DETECT_STAY_TIME:
                    print("Trigger Area!")
                    ret = value
                    handlers_list[target_handler_num] = False
            else:
                new_frame = ui_drawer.cv2putText(new_frame, "請將手離開其中一個偵測區！", w//6, h//4, (255, 255, 0), 30, 2)
                start_time = time.time()
    else: # cancel
        handlers_list[target_handler_num]= False

    return ret, new_frame