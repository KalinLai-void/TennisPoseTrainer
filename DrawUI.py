import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

from constants import *
from Interactor import Interactor
from StateSaver import StateSaver

class DrawUI:
    def __init__(self, detector):
        self.path_list = list()
        self.detector = detector

    def DrawAngle(self, frame, point, ang):
        if self.detector.DetectAngleInRangle(ang, 180, KNEE_ANGLE):
            new_frame = self.cv2putText(frame, str(ang), point[0], point[1], (0, 255, 0), 15, 1)
        else:
            new_frame = self.cv2putText(frame, str(ang), point[0], point[1], (255, 255, 255), 15, 1)
        #print(ang)
        return new_frame

    def DrawCurve(self, frame, start_point, end_point, control_point1, control_point2):
        curve_points = []
        for t in np.linspace(0, 1, 100):
            x = int((1-t)**3 * start_point[0] + 3*(1-t)**2 * t * control_point1[0] + 3*(1-t) * t**2 * control_point2[0] + t**3 * end_point[0])
            y = int((1-t)**3 * start_point[1] + 3*(1-t)**2 * t * control_point1[1] + 3*(1-t) * t**2 * control_point2[1] + t**3 * end_point[1])
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
            
            cv2.circle(frame, (int(x), int(y)), 10, (0, 255, 0), -1)
            curve_points.append((int(x), int(y)))
        return curve_points

    def cv2putText(self, img, text, x, y, text_color, text_size, border=0):
        if isinstance(img, np.ndarray):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
        draw = ImageDraw.Draw(img)
        font_style = ImageFont.truetype("font/msjhbd.ttc", text_size, encoding="utf-8")
        draw.text((x, y), text, font=font_style, fill=text_color, stroke_width=border, stroke_fill=(0, 0, 0))
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def DrawSwingPath(self, frame):
        if StateSaver.mode_num == 0: # Forehand
            if StateSaver.handed_mode_num == 0: wrist_point = Interactor.wrist_l_point # left-handed
            else: wrist_point = Interactor.wrist_r_point # right-handed
        else: # Backhand
            if StateSaver.handed_mode_num == 0: wrist_point = Interactor.wrist_r_point # left-handed
            else: wrist_point = Interactor.wrist_l_point # right-handed

        cv2.circle(frame, wrist_point, 10, (255, 0, 0), -1)
        self.path_list.append(wrist_point)

        points = np.array(self.path_list)
        cv2.polylines(frame, pts=[points], isClosed=False, color=(0, 0, 0), thickness=15) # border
        cv2.polylines(frame, pts=[points], isClosed=False, color=(255, 255, 255), thickness=10) #fill
        return frame
    
    def ClearSwingPath(self):
        self.path_list.clear()

    def DrawCircleDetector(self, frame, center, detect_area_r, text, color=(0, 0, 255)):
        (b, g, r) = color

        cv2.circle(frame, center, detect_area_r, color, 5) 
        frame = self.cv2putText(frame, text, 
                                center[0]-detect_area_r-15, center[1]-detect_area_r*3, 
                                (r, g, b), 30, 2)
        return frame