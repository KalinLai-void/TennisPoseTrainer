Tennis Pose Trainer
===

[English](/README.md) | [繁體中文 (zh-TW)](/README-zh.md)

## 簡介
此工具主要是針對網球運動，基於 [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) 開發。讓使用者可以訓練正手拍及反手拍的動作，且支援讓使用者選擇慣用手（左/右手）來訓練。使用者在選擇模式並揮拍後，<u>可以看到他們的揮拍軌跡、狀態與姿勢</u>

> 雖然此程式只支援**繁體中文 (zh-TW)** 的顯示 (我未來有機會將會更新英文介面的支援), 你可以在程式中更改語言. 且若你翻譯後樂意將其他語言版本提供給我，可以聯絡我。

> 此工具主要是協助高雄科技大學體育室於 2024/07/15 ~ 2024/07/19 辦理[「113年運動i台灣2.0」計畫的運動科技體驗](https://isports.sa.gov.tw/Apps/TIS/TIS02/TIS0201M_02V1.aspx?SYS=TIS&MENU_PRG_CD=1&ITEM_PRG_CD=2&PKNO=40332)所開發。

### 場域設置
![](/demo/FeildSetting.JPG)
- Camera: 用來**捕捉使用者的姿勢/動作**，讓程式能夠處理。圖中可以看到我們是使用 GoPro。
- Monitor: 為了顯示程式的畫面給使用者看，包括UI、提是文字、讓使用者看到自己的操作等等。
> 所有人物及裝置的距離不需要固定，只須要讓使用者使用舒服、順暢即可。
> **但切記，一次只能有一個使用者使用，即 Camera 只能抓到一個人，否則程式會有 Bug。**

### Demo video
- UI互動：使用者能夠看著畫面，並透過手關節去選擇模式、慣用手及回到上一選擇介面。
![](/demo/demo_ui.gif)
- 網球抽球姿勢訓練：根據手關節及膝蓋角度判斷是否進入準備動作，準備後3秒將會開始訓練一次動作，然後跟著曲線揮動到結束點會畫出揮動軌跡並計數。
![](/demo/demo.gif)

## 依賴環境
### OpenPose
此程式主要基於 [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) 所開發，此函式庫是CMU所開發，主要用來即時辨識人體姿態，可以抓到人體、手勢、表情等。

我們建置此函式庫給 Python 來使用，我們建置的 Python 函式庫檔案及模型檔可以在[這裡下載](https://github.com/KalinLai-void/TennisPoseTrainer/releases/download/OpenPose/openpose.zip).

### 環境要求
- [Anaconda 3](https://www.anaconda.com/)
- Python 3.10.9
- ```requirement.txt``` （以下僅顯示主要依賴的套件）
  - opencv-python==4.7.0.72
  - Pillow==9.4.0
  - numpy==1.24.2
  - tk==0.1.0
  - tkvideoplayer==2.3

## 安裝
1. git clone/下載這個 repository。
2. 下載 Python 函式庫檔案及模型檔，可以從[這裡](https://github.com/KalinLai-void/TennisPoseTrainer/releases/download/OpenPose/openpose.zip)下載，下載後可以解壓縮檔案到這個。repository 的根目錄。
3. 創建你的 Python 環境（Anaconda 與 Python 3.10.9）。
4. 啟動你的環境，且使用指令 ```pip install -r requirement.txt``` 來安裝所需套件。
5. 執行 ```Main.py```！

## 如何使用？
> 如果你想要修改程式碼，我們要先道歉。
> 程式可能寫得有點醜，因為有蠻多東西算是趕出來的，還沒有整理完。
> 未來我們會整理程式碼，讓程式碼有更高的擴充性！

- ```Main.py```中一些基本的調整：
  - 主要會用到**一個**攝影機，所以攝影機可以在程式碼中更改編號/路徑。
    ```python
    cap = cv2.VideoCapture(2) # 2 is GoPro WebCam number in my computer
    ```
  - 匯入 OpenPose，若有需要可以更改路徑（```openpose_path```與```openpose_model_path```）
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
    - 因為我們主要是針對直式畫面處理與顯示，故模型中的 net_resolution 設成 320x480，且這個大小是我們測出在即時處理時，lag 較不嚴重的情況。（原影像比例9:16，若比例不同可能需要自行調整）
    - 目前的程式碼中，雖然不需要偵測手指做一些操作，目前有保留一個擴充性在，能夠透過```IS_USE_HAND_TO_SELECT```的參數決定是否開啟手指偵測，未來可能可以增加手勢辨識來做到更多應用！
    ```python

    # model input
    datum.cvInputData = flip_frame
    opWrapper.emplaceAndPop(op.VectorDatum([datum]))

    ...

    # output img from model
    result = datum.cvOutputData
    ```
  - 其他 functions 就是程式中會做的各項動作。
    - ~~耦合太多，寫得不漂亮我很抱歉~~
- ```constants.py```：此程式碼主要就是一些客製化的常數參數。需要的話可以根據自己需求改動。
- ```utils.py```：此程式碼主要就是會頻繁呼叫的functions。
- ```Detector.py```：此類別主要就是定義一些不同形狀的偵測範圍function，可能有圓形的偵測區（```DetectPointInCircleArea(self, center, radius, point)```）、偵測點在曲線上（```DetectPointOnCurve(self, curve_points, target_point, detect_dist)```）等等。
- ```Interactor.py```：此類別主要就是定義用來互動的keypoints有哪些，在此程式中可能有手及膝蓋。
- ```StateSaver.py```：此**靜態**類別主要用來儲存目前的狀態，以供後續操作使用。比如暫存模式（正/反手拍、左/右慣用手）。
- ```DrawUI.py```：此類別主要就是關於顯示UI介面相關。

> 如果想要將此程式翻譯成其他語言，我認為可以將程式中**所有繁體中文**的部分都取代掉即可（但還是要遵循程式邏輯）。
> 未來可能可以寫一個`lang.yml`來做多語言的切換。