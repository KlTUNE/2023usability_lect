import mediapipe as mp
import cv2
import time

class Trac():
    def __init__(self):
        self.static_image_mode = False
        self.max_hands = 1
        self.model_complexity = 1
        self.detection_confidence = 0.5
        self.track_confidence = 0.5

        self.mp = mp.solutions.hands
        self.handtrac_library = self.mp.Hands(self.static_image_mode, self.max_hands, self.model_complexity,
                                                    self.detection_confidence, self.track_confidence)
        self.drawing = mp.solutions.drawing_utils

    def tracking(self, img, drawing_img):
        draw = True
        landmark = []

        landmarks = self.handtrac_library.process(img)
        if landmarks.multi_hand_landmarks:
            for all_landmark in landmarks.multi_hand_landmarks:
                if draw:
                    self.drawing.draw_landmarks(drawing_img, all_landmark, self.mp.HAND_CONNECTIONS)
                for id, lm in enumerate(all_landmark.landmark):
                    hight, width, channel = img.shape
                    x, y = int(lm.x * width), int(lm.y * hight)
                    landmark.append([id, x, y])

        return landmark

def hands_trac(cap):
    success, img = cap.read()
    RGBimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    flipRGBimg = cv2.flip(RGBimg, 1)
    flipimg = cv2.flip(img, 1)
    landmark = trac.tracking(flipRGBimg, flipimg)
    finger_tips = [4, 8, 12, 16, 20]
    finger_status = []

    if len(landmark) != 0:
        if landmark[finger_tips[1]][1] < landmark[finger_tips[4]][1]:
            dominant_hand = "right"
        elif landmark[finger_tips[1]][1] > landmark[finger_tips[4]][1]:
            dominant_hand = "left"
        else :
            dominant_hand = "error"

        if dominant_hand == "right":
            if landmark[finger_tips[0]][1] < landmark[finger_tips[0] - 1][1]:
                finger_status.append(1)
            else :
                finger_status.append(0)
        elif dominant_hand == "left":
            if landmark[finger_tips[0]][1] > landmark[finger_tips[0] - 1][1]:
                finger_status.append(1)
            else :
                finger_status.append(0)

        for i in range(1, 5):
            if dominant_hand == "error":
                break
            elif landmark[finger_tips[i]][2] < landmark[finger_tips[i] - 2][2]:
                finger_status.append(1)
            else:
                finger_status.append(0)

    # cv2.imshow("Image", flipimg)
    # cv2.waitKey(1)

    #グー
    if finger_status == [0, 0, 0, 0, 0]:
        return 0
    #チョキ
    elif finger_status == [0, 1, 1, 0, 0]:
        return 1
    #パー
    elif finger_status == [1, 1, 1, 1, 1]:
        return 2
    #その他
    else:
        return -1

trac = Trac()

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    while True:
        try:
            score = hands_trac(cap)
            print(score)
        except KeyboardInterrupt:
            cap.release()
            break