import sys

# 영상 처리
import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import pyautogui

# 연산 처리
import math
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta

# GUI 처리
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5.QtWidgets import *


import SelectWindowCapture
from dlg_motionSetting import dialog_window
# 이건훈 또또  왔다감
# Main Branch
# ----------------------------------------------------------------------------------------------------------------------

# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("untitled.ui")[0]


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.tabIndex = 0           # 탭 인덱스 번호
        self.old = None             # 타이머 시작 시간

        self.running = False        # Camera 구동 여부
        self.record = False         # 녹화 여부
        self.recordVideo = None     # 녹화 프레임

        # Camera 세팅
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 530)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 510)

        # 손 거리 측정 용
        self.motionData = ['None']  # 모션 데이터 List
        # 손 거리 측정
        x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
        y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        self.coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)  # 핸드 디텍터

        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # 파일 불러오기
        self.Btn_PPTFileOpen.clicked.connect(self.pptfileOpen)
        self.Btn_SaveFolder.clicked.connect(self.saveFolderSelect)

        # 탭 변경시
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # 설정 변경 다이얼로그 버튼
        self.pt_Btn_OptionDialog.clicked.connect(self.OptionDialog)
        self.ptex_Btn_OptionDialog.clicked.connect(self.OptionDialog)

        # 시작 종료 버튼
        self.pt_Btn_Start.clicked.connect(self.start)
        self.ptex_Btn_Start.clicked.connect(self.start)

        self.pt_Btn_Stop.clicked.connect(self.stop)
        self.ptex_Btn_Stop.clicked.connect(self.stop)

        # 녹화 버튼
        self.pt_Btn_Recording.clicked.connect(self.recording)
        self.ptex_Btn_Recording.clicked.connect(self.recording)

    # ppt 파일 열기
    def pptfileOpen(self):
        fliename = QFileDialog.getOpenFileName(self, '파일 불러오기', '', 'PowerPoint(*.pptx *ppt);; All File(*)')

        if fliename[0]:
            self.Line_PPTLink.setText(fliename[0])
        else:
            print("파일을 선택하지 않았습니다.")

    # 저장 폴더 지정
    def saveFolderSelect(self):
        fliename = QFileDialog.getExistingDirectory(self, "select Directory")
        if fliename == "":
            print("폴더를 선택하지 않았습니다.")
        else:
            self.Line_SaveFolder.setText(fliename)
        self.isFolder()

    def isFolder(self):
        if self.Line_SaveFolder.text() == '':
            self.pt_Btn_Recording.setEnabled(False)
            self.ptex_Btn_Recording.setEnabled(False)
        else:
            self.record = True
            self.pt_Btn_Recording.setEnabled(True)
            self.ptex_Btn_Recording.setEnabled(True)
            self.recordVideo = cv2.VideoWriter(
                f'{self.Line_SaveFolder.text()}/test.mp4v',
                cv2.VideoWriter_fourcc(*'XVID'), 15,
                (1024, 717))

    # 탭 변경시
    def tabChanged(self):
        self.tabIndex = self.tabWidget.currentIndex()
        self.stop()

    # 다이얼로그 띄우기
    def OptionDialog(self):
        # self.hide()
        # self.dlg_set = dialog_window()
        # self.dlg_set.exec()
        # self.show()
        win = dialog_window(self.motionData)

        if win.showModal():
            self.motionData = win.motionData
            print(self.motionData)

    # 중지 버튼 클릭시
    def stop(self):
        self.buttonEnabled(self.tabIndex, True, True, True, True, False, True)
        self.isFolder()

        if self.record:
            self.recordingStop()
        else:
            self.cameraStop()

    # 시작 버튼 클릭시
    def start(self):
        self.running = True
        self.buttonEnabled(self.tabIndex, False, False, False, False, True, False)
        self.videoCam()

    # 카메라 컨트롤
    def videoCam(self):
        self.old = datetime.now()
        capture = SelectWindowCapture.WindowCapture("Presentation Project", 20)
        while self.running:
            ret, frame = self.cap.read()
            hands = self.detector.findHands(frame, draw=False)
            if ret is True:
                # 손을 이용한 거리 분석
                if hands:
                    lmList = hands[0]['lmList']
                    # x, y, w, h = hands[0]['bbox']
                    x1 = lmList[5][0]
                    y1 = lmList[5][1]
                    x2 = lmList[17][0]
                    y2 = lmList[17][1]

                    distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
                    A, B, C = self.coff
                    distanceCM = A * distance ** 2 + B * distance + C
                    self.distanceSilder(distanceCM)

                self.updateTimeCount(self.old)

                self.displayImage(frame, 1)
                # 녹화 기능 -------------------------------------------------------
                if self.record:
                    img = capture.screenshot()
                    self.recordVideo.write(img)

                cv2.waitKey()

    # 영상 출력시 시간 카운트
    def updateTimeCount(self, old):
        # 현재 시각을 불러와 문자열로 저장
        now = datetime.now()
        timer = now - old
        min = timer.seconds // 60
        sec = timer.seconds % 60

        if self.tabWidget.currentIndex() == 0:
            self.pt_lcdNumber.display(f'{min}:{sec}')
        elif self.tabWidget.currentIndex() == 1:
            self.ptex_lcdNumber.display(f'{min}:{sec}')

    # 거리에 따른 슬라이더 이동
    def distanceSilder(self, distanceCM):
        if self.tabWidget.currentIndex() == 0:
            if distanceCM >= self.pt_Bar_Distance.maximum():
                self.pt_Line_CameraDistance.setText("너무 멀리 이동하셨습니다.")
            elif distanceCM <= self.pt_Bar_Distance.minimum():
                self.pt_Line_CameraDistance.setText("너무 가까이 이동하셨습니다.")
            else:
                self.pt_Line_CameraDistance.setText("적정 거리")
                self.pt_Bar_Distance.setValue(distanceCM)

        elif self.tabWidget.currentIndex() == 1:
            if distanceCM >= self.pt_Bar_Distance.maximum():
                self.ptex_Line_CameraDistance.setText("너무 멀리 이동하셨습니다.")
            elif distanceCM <= self.pt_Bar_Distance.minimum():
                self.ptex_Line_CameraDistance.setText("너무 가까이 이동하셨습니다.")
            else:
                self.ptex_Line_CameraDistance.setText("적정 거리")
                self.ptex_Bar_Distance.setValue(distanceCM)

    # 카메라 실시간 영상 처리
    def displayImage(self, frame, window=1):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)

        # 출력 영상을 resize해 주기
        p = pixmap.scaled(int(w*400/h), 400, QtCore.Qt.IgnoreAspectRatio)

        if self.tabWidget.currentIndex() == 0:
            self.pt_WebCamera.setPixmap(p)
            self.pt_WebCamera.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignHCenter)
        elif self.tabWidget.currentIndex() == 1:
            self.ptex_WebCamera.setPixmap(p)
            self.ptex_WebCamera.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignHCenter)

    # 카메라 정지
    def cameraStop(self):
        self.running = False
        if self.tabIndex == 0:
            self.pt_WebCamera.clear()
        elif self.tabIndex == 1:
            self.ptex_WebCamera.clear()

    # 녹화 버튼 클릭시
    def recording(self):
        self.running = True
        self.buttonEnabled(self.tabIndex, False, False, False, False, True, False)
        self.videoCam()

    # 녹화 종료
    def recordingStop(self):
        self.running = False
        self.record = False
        self.recordVideo.release()

        if self.tabIndex == 0:
            self.pt_WebCamera.clear()
        elif self.tabIndex == 1:
            self.ptex_WebCamera.clear()

    # 버튼의 활성 여부 변경
    def buttonEnabled(self, index, ppt, folder, record, start, stop, option):
        self.Btn_PPTFileOpen.setEnabled(ppt)
        self.Btn_SaveFolder.setEnabled(folder)

        if index == 0:
            self.pt_Btn_Recording.setEnabled(record)
            self.pt_Btn_Start.setEnabled(start)
            self.pt_Btn_Stop.setEnabled(stop)
            self.pt_Btn_OptionDialog.setEnabled(option)

        elif index == 1:
            self.ptex_Btn_Recording.setEnabled(record)
            self.ptex_Btn_Start.setEnabled(start)
            self.ptex_Btn_Stop.setEnabled(stop)
            self.ptex_Btn_OptionDialog.setEnabled(option)

    # # 웹캠 조작 메서드
    # def run(self):
    #     cap = cv2.VideoCapture(0)
    #     cap.set(3, self.pt_WebCamera.width())
    #     cap.set(4, self.pt_WebCamera.height())
    #     while self.running:
    #         ret, img = cap.read()
    #         if ret:
    #             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #             h, w, c = img.shape
    #             qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
    #             pixmap = QtGui.QPixmap.fromImage(qImg)
    #             self.pt_WebCamera.setPixmap(pixmap)
    #         else:
    #             QtWidgets.QMessageBox.about(win, "Error", "Cannot read frame.")
    #             print("cannot read frame.")
    #             break
    #     cap.release()
    #     print("Thread end.")
    #
    #
    # # 시작 버튼
    # def start(self):
    #     self.running = True
    #     th = threading.Thread(target=self.run)
    #     th.start()
    #     print("started..")
    #
    # # 종료 버튼
    # def onExit(self):
    #     print("exit")
    #     self.stop()
