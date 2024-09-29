from constants import *

class Interactor:
    wrist_l_point, wrist_r_point = None, None
    hand_l_point, hand_r_point = None, None
    knee_l_point, knee_r_point = None, None

    def __init__(self):
        pass

    def GetInteractKeypoints(self, datum): # interact keypoint    
        if datum.poseKeypoints is not None:
            Interactor.wrist_l_point = (int(datum.poseKeypoints[0][4][0]), int(datum.poseKeypoints[0][4][1]))
            Interactor.wrist_r_point = (int(datum.poseKeypoints[0][7][0]), int(datum.poseKeypoints[0][7][1]))
        else:
            Interactor.wrist_l_point = (0, 0)
            Interactor.wrist_r_point = (0, 0)

        if IS_USE_HAND_TO_SELECT:
            if datum.handKeypoints[1] is not None: # left hand
                Interactor.hand_l_point = (int(datum.handKeypoints[1][0][9][0]), int(datum.handKeypoints[1][0][9][1]))
            else:
                Interactor.hand_l_point = (0, 0)

            if datum.handKeypoints[0] is not None: # right hand
                Interactor.hand_r_point = (int(datum.handKeypoints[0][0][9][0]), int(datum.handKeypoints[0][0][9][1]))
            else:
                Interactor.hand_r_point = (0, 0)
        else:
            Interactor.hand_l_point = Interactor.wrist_l_point
            Interactor.hand_r_point = Interactor.wrist_r_point

    def GetKneeKeypoints(self, datum):
        if datum.poseKeypoints is not None:
            Interactor.knee_l_point = (int(datum.poseKeypoints[0][10][0]), int(datum.poseKeypoints[0][10][1]))
            Interactor.knee_r_point = (int(datum.poseKeypoints[0][13][0]), int(datum.poseKeypoints[0][13][1]))
        else:
            Interactor.knee_l_point = (0, 0)
            Interactor.knee_r_point = (0, 0)