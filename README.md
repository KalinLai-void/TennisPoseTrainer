Tennis Pose Trainer
===

[English](/README.md) | [繁體中文 (zh-TW)](/README-zh.md)

## Intro
This application is the sport tool, developing based on [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose), it can let user train strokes in tennis. It support forehand and backhand, and user can select dominant hand (right hand/left hand). <u>After user select mode and start swing training, he/she can see his/her swing status, pose and trajectory.</u>

> Alought this software only support to show **Tranditional Chinese** tip text (we will support to show English in the future), you can modify the text language in code. And you can contact to me if you willing to translate to other languages.

> This program was developed for [Sport Technology Experience Activity of "Sports i Taiwan 2.0 Project"](https://isports.sa.gov.tw/Apps/TIS/TIS02/TIS0201M_02V1.aspx?SYS=TIS&MENU_PRG_CD=1&ITEM_PRG_CD=2&PKNO=40332) in National Kaohsiung University of Science and Technology (NKUST).

### Field Settings

![](/demo/FeildSetting.JPG)

- Camera: It is used to **capture user pose**, let the program to process. In the picture, it uses GoPro in our case.
- Monitor: It show program screen, including UI, tips, and the result after processing. User can see he/she in monitor, then using according to the tips.
> The distance of any devices/people need not to fixed, it just be used comfortably by user.
> **Notice: The program only 1 user once, that is to say, the camera only can capture 1 person once. Otherwise, it has bug!**

### Demo video
- Interact UI: See screen and through hand joints to selecting dominant hand (right/left hand), mode (forehand/backhand),and back to last UI.

![](/demo/demo_ui.gif)

- Training Tennis Stroke Action: Ready to start (according to knee angle and hand joints), and swing to draw stroke trajectory and counting.

![](/demo/demo.gif)

> In the "Program Screen", it has three view to shown. The left view is just keypoints output from OpenPose, the right view show last swing action trajectory, and the center view is to interact mainly.

## Pre-Requirements
### OpenPose
This software is based on [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose), a library that detects real-time keypoints for human body, hand, facial, and foot is developed by CMU.

We build the library for Python, the models and lib files can download from [here](https://github.com/KalinLai-void/TennisPoseTrainer/releases/download/OpenPose/openpose.zip).

### Environment and requirements
- [Anaconda 3](https://www.anaconda.com/)
- Python 3.10.9
- ```requirement.txt``` (show main libs in following)
  - opencv-python==4.7.0.72
  - Pillow==9.4.0
  - numpy==1.24.2
  - tk==0.1.0
  - tkvideoplayer==2.3

## Installation
1. git clone/download this repository.
2. download the models and lib files from [here](https://github.com/KalinLai-void/TennisPoseTrainer/releases/download/OpenPose/openpose.zip), and unzip to this repository's root.
3. create your python env (Anaconda and Python 3.10.9).
4. activate your env, and ```pip install -r requirement.txt```.
5. run ```Main.py```!

## How to use?
> If you want to modify the code, we apology to you.
> The code may be a little ugly, because we whip this code up for the project. We are very sorry!
> In the future, we will arrange the code to the program have more expandability.

- In ```Main.py```, some essential setting:
  - Mainly, this case use **1 camera**, so camera location/number can be modify in the code.
    ```python
    cap = cv2.VideoCapture(2) # 2 is GoPro WebCam number in my computer
    ```
  - Importing OpenPose, you can change path if you need.(```openpose_path```&```openpose_model_path```)
    ```python
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
    ```
  - OpenPose Settings
    ```python
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
    ```
    - Because we are processing and showing for vertical view, so "net_resolution" in model is set to "320x480". And this scale has good performance for Real-Time processing. (Original scale is 9:16. You should modify for your case.)
    - Although it need not do something through hand/fingers now, we still reserved some expandabilities. If you want, you can use the constant in code ```IS_USE_HAND_TO_SELECT``` to decide to detect hand/fingers. Maybe, we can use the gesture recognition to do more application!
    ```python

    # model input
    datum.cvInputData = flip_frame
    opWrapper.emplaceAndPop(op.VectorDatum([datum]))

    ...

    # output img from model
    result = datum.cvOutputData
    ```
  - Other functions: each actions in code.
    - ~~Coupling is too much, the code is ugly. I am sorry.~~
- ```constants.py```：This code has some customize constants. You can modify according to your case.
- ```utils.py```：This code has some functions to call frequently.
- ```Detector.py```：This class define some detectors, different shapes area to detect, maybe has circle area（```DetectPointInCircleArea(self, center, radius, point)```）or point on curve（```DetectPointOnCurve(self, curve_points, target_point, detect_dist)```）, etc.
- ```Interactor.py```：This class define what some keypoints can use to interact. It has hand and knee in our case.
- ```StateSaver.py```：This **static** class is saving some status to use in the follow-up, such as mode (forehand/backhand, right/left dominant hand).
- ```DrawUI.py```：This class is about UI showing.

> If you want to translate to your language, I think you can modify **ALL Tranditional Chinese** in the code. (But must keeping the prgram logic.)
> In the future, maybe can write `lang.yml` to switch mutiple language.