class StateSaver:
    mode_num, handed_mode_num = None, None

    def __init__(self):
        pass

    @staticmethod
    def SetMode(num):
        StateSaver.mode_num = num

    @staticmethod
    def SetHandedMode(num):
        StateSaver.handed_mode_num = num