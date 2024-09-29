from utils import GetDist

class Detector():
    def __init__(self):
        pass

    def DetectPointInCircleArea(self, center, radius, point):
        dist = GetDist(center, point)
        if dist <= radius: return True
        else: return False

    def DetectPointInRectArea(self, rect_start_point, rect_end_point, point):
        if point[0] <= rect_start_point[0] or point[0] >= rect_end_point[0]: return False # check X
        if point[1] <= rect_start_point[1] or point[1] >= rect_end_point[1]: return False # check Y
        return True

    def DetectPointOnCurve(self, curve_points, target_point, detect_dist):
        clostest_dist = float('inf')
        for p in curve_points:
            d = GetDist(p, target_point)
            if d < clostest_dist: clostest_dist = d

        if clostest_dist > detect_dist: return False
        return True

    def DetectAngleInRangle(self, ang1, ang2, tar_ang):
        if abs(ang1-ang2) >= tar_ang: return True
        return False