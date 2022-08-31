from multiprocessing.connection import wait
from traceback import print_tb
import cv2
import mediapipe as mp 
import numpy as np
import math
import time 
import random

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

jab_counter = 0
jab_counter_for_game = 0
straight_counter = 0
straight_counter_for_game = 0
lead_hook_counter = 0 
lead_hook_counter_for_game = 0 
jab_stage = None
straight_stage = None
box_color = [255,255,255]
off_vs_def_box = [255,255,255]
off_vs_def_text = ''
stance_num = 0
stance = ""
display_info = True #Option to modify
show_landmarks = True #Option to modify

globalStartTime = time.time()
startTime = ''
lastTime = startTime
endTime = ''
timeValue = ''
timeForCombo = ''
frameCounter = 0
randomFrameNumber = random.randint(30,60)
comboResetChecker = 1

combo = ''
combos ={
    1: "1",
    2: "2",
    3: "1,2"
}

numberOfCorrect = 0
numberOfTooSlow = 0

# VIDEO FEED
cap = cv2.VideoCapture(0)

# Get capture info
video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT ))
video_fps =  cap.get(cv2.CAP_PROP_FPS)
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while(True):      
        # Capture the video frame by frame
        ret, frame = cap.read()
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        # Make detection
        results = pose.process(image)
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        #settings
        # if cv2.waitKey(1) & 0xFF == ord('o'):
        #     display_info = False
        # if cv2.waitKey(1) & 0xFF == ord('i'):
        #     display_info = True
        # if cv2.waitKey(1) & 0xFF == ord('l'):
        #     show_landmarks = False
        # if cv2.waitKey(1) & 0xFF == ord('k'):
        #     show_landmarks = True
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        totalTime = round((time.time() - globalStartTime), 2)

        if show_landmarks == True:
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(0, 150, 0), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                                    )

        
        def calculate_angle(a, b, c):
            a = np.array(a)  # First
            b = np.array(b)  # Mid
            c = np.array(c)  # End

            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)

            if angle > 180.0:
                angle = 360 - angle
            return angle

            # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            #coordinates for each landmark in use
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            l_pinky = [landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value].x, landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value].y]
            r_pinky = [landmarks[mp_pose.PoseLandmark.RIGHT_PINKY.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_PINKY.value].y]

            #Get angles of joints
            angle_left_elbow = calculate_angle(l_shoulder,l_elbow,l_wrist)
            angle_right_elbow = calculate_angle(r_shoulder,r_elbow,r_wrist)
            angle_rhip_rshoulder_rwrist = calculate_angle(r_hip,r_shoulder,r_wrist)
            angle_lhip_lshoulder_lwrist = calculate_angle(l_hip,l_shoulder,l_wrist)


            #Display angle of joint
            def display_angle (joint_angle, landmark_for_location ):   
                cv2.putText(image, str(joint_angle),
                            tuple(np.multiply(landmark_for_location, [video_width,video_height]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (255,255,255), 2, cv2.LINE_AA)
            # display_angle(angle_left_elbow, l_elbow)
            display_angle(left_wrist_to_elbow, l_wrist)
            display_angle(left_elbow_to_shoulder, l_shoulder)
        except:
            pass


        try:
            #left punch logic 
            if angle_left_elbow < 60:
                if l_pinky[1] < l_shoulder [1]:
                    jab_stage = "Defense"
            if angle_left_elbow > 110 and jab_stage == "Defense":
                if angle_lhip_lshoulder_lwrist > 70:
                    if angle_right_elbow < 40:
                        if stance == "Orthodox":
                            jab_stage = "Offense"
                            jab_counter +=1
                            jab_counter_for_game +=1
                        elif stance == "Southpaw":
                            jab_stage = "Offense"
                            straight_counter +=1
                            straight_counter_for_game +=1
                            
            #right punch logic
            if angle_right_elbow < 60:
                if l_pinky[1] < l_shoulder [1]:
                    straight_stage = "Defense"
            if angle_right_elbow > 110 and straight_stage == "Defense":
                if angle_rhip_rshoulder_rwrist > 70:
                    if angle_left_elbow < 40:
                        if stance == "Orthodox":
                            straight_stage = "Offense"
                            straight_counter +=1
                            straight_counter_for_game +=1
                        elif stance == "Southpaw":
                            straight_stage = "Offense"
                            jab_counter +=1
                            jab_counter_for_game +=1

            def create_box (x1,x2,y1,y2,colorBGR):   
                cv2.rectangle(image, (x1,x2), (y1,y2), (colorBGR), -1)
            def display_text (text_to_display,x,y,colorBGR,size=.6,thickness=1):
                cv2.putText(image, text_to_display, (x,y), cv2.FONT_HERSHEY_COMPLEX, size, (colorBGR), thickness, cv2.LINE_AA)
            
            if display_info == True:
                #display punch count on screen
                create_box (0,0,250,75,(0,0,0))
                display_text(f"Total Jabs: {str(jab_counter)}",10,15,(255,255,255))
                display_text(f"Total Straights: {str(straight_counter)}",10,40,(255,255,255))
                display_text(f"Total Lead Hooks: {str(lead_hook_counter)}",10,65,(255,255,255))

                # Show offense vs defense 
                create_box(video_width - 150,0,video_width,50,off_vs_def_box)
                display_text(off_vs_def_text,video_width - 110,30,(255,255,255))

                #Display stance
                create_box(video_width - 150,(50),video_width,100,(255,255,255))
                display_text(stance, video_width-130, 80, (0,0,0))

                #Display Timer
                create_box(0,video_height-50,(150),video_height,[255,255,255])
                display_text(str(timeForCombo), 10,video_height-25,(0,0,0),1)

                # Display Combo
                create_box(270,0,(400),60,[255,255,255])
                display_text(combo,(280),50,[0,0,255],1.8,2)

                 # display correct or incorrect
                create_box(video_width - 150,(video_height-50),video_width,video_height,(255,255,255))
                display_text("Correct: ", (video_width-140), (video_height-30), (0,0,0))
                display_text(str(numberOfCorrect), (video_width-50), (video_height-30), (0,0,0))
                display_text("Incorrect: ", (video_width-140), (video_height-10), (0,0,0))
                display_text(str(numberOfTooSlow), (video_width-35), (video_height-10), (0,0,0))

            if jab_stage and straight_stage == "Defense":
                off_vs_def_box = [255,0,0]
                off_vs_def_text = "Defense"
            if jab_stage == "Offense":
                off_vs_def_box = [0,0,139]    
                off_vs_def_text = "Offense"
            if straight_stage == "Offense":
                off_vs_def_box = [0,0,139]    
                off_vs_def_text = "Offense"


            #get length of arm
            left_wrist_to_elbow = int(math.sqrt(((l_elbow[0] - l_wrist[0]) * (l_elbow[0] - l_wrist[0])) + ((l_elbow[1] - l_wrist[1]) * (l_elbow[1] - l_wrist[1]))) * 100)

            left_elbow_to_shoulder = int(math.sqrt(((l_elbow[0] - l_shoulder[0]) * (l_elbow[0] - l_shoulder[0])) + ((l_elbow[1] - l_shoulder[1]) * (l_elbow[1] - l_shoulder[1]))) * 100)

            left_shoulder_to_wrist = int(math.sqrt(((l_wrist[0] - l_shoulder[0]) * (l_wrist[0] - l_shoulder[0])) + ((l_wrist[1] - l_shoulder[1]) * (l_wrist[1] - l_shoulder[1]))) * 100)
            
            length_of_arm = left_wrist_to_elbow + left_elbow_to_shoulder
            
            # distance testing
            right_hand_distance = int((math.sqrt(r_pinky[1] - nose[1]) ** 2 + (r_pinky[0] - nose[0]) ** 2) * 100)
            left_hand_distance = int((math.sqrt(l_pinky[1] - nose[1]) ** 2 + (l_pinky[0] - nose[0]) ** 2) * 100)
            
            #Postive number is Southpaw, negative is Orthodox
            if right_hand_distance > left_hand_distance:
                if stance_num < 15:
                    stance_num += 1
            elif right_hand_distance < left_hand_distance:
                if stance_num > -15:
                    stance_num -= 1
            else:
                pass

            if jab_stage and straight_stage == "Defense":
                if stance_num >= 10:
                    stance = "Southpaw"
                elif stance_num <= -10:
                    stance = "Orthodox"
                elif stance_num < 10 and stance_num > 10:
                    stance = ''

            
        except:
            pass


        def timingGame(diffulty=1):
            import playsound
            global frameCounter,combo,startTime,endTime,jab_counter_for_game,timeForCombo
            global numberOfTooSlow,numberOfCorrect,randomFrameNumber,straight_counter_for_game
            

            def comboToLogic(argument):
                global jab_counter_for_game
                global straight_counter_for_game

                match argument:
                    case "1":
                        if jab_counter_for_game == 1 and endTime =='':
                            return True
                    case "2":
                        if straight_counter_for_game == 1 and endTime =='':
                            return True
                    case "1,2":
                        if jab_counter_for_game == 1 and straight_counter_for_game == 1 and endTime =='':
                            return True
                        if jab_counter_for_game >= 2:
                            jab_counter_for_game = 0
                        if straight_counter_for_game >= 2:
                            straight_counter_for_game = 0                       
                    case default:
                        return False

            if frameCounter > randomFrameNumber:

                #provide a combo
                if combo == '':
                    combo = combos[random.randint(1,len(combos))]

                # set start timer for the combo
                if combo != '' and startTime == '':
                    startTime = time.time()


                #if combo is thrown then end and reset stats
                if comboToLogic(combo) == True:
                    endTime = time.time();
                    timeForCombo = round((endTime - startTime),2)
                    if timeForCombo < diffulty:
                        # playsound.playsound("correct.mp3")
                        numberOfCorrect += 1
                    if timeForCombo > diffulty:
                        # playsound.playsound("incorrect.mp3")
                        numberOfTooSlow +=1   
                    frameCounter = 0
                    combo = ''
                    startTime = ''
                    endTime = ''
                    jab_counter_for_game = 0
                    straight_counter_for_game = 0
                    randomFrameNumber = random.randint(30,90)
                    
                    

        # timingGame(1.5)
        # if frameCounter % 30 == 0:
        #     print(f" length of arm: {length_of_arm}\n distance from shoulder to wrist: {left_shoulder_to_wrist}")
        frameCounter += 1
        cv2.imshow('Mediapipe Feed', image)




# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()


