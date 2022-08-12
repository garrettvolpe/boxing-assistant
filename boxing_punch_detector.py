import cv2
import mediapipe as mp 
import numpy as np
import math
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

jab_counter = 0
straight_counter = 0
jab_stage = None
straight_stage = None
box_color = [255,255,255]
off_vs_def_box = [255,255,255]
off_vs_def_text = ''
stance_num = 0
stance = ""


# VIDEO FEED
cap = cv2.VideoCapture(0)

# Get capture info
video_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH )
video_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT )
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

        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
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

            angle_left_elbow = calculate_angle(l_shoulder,l_elbow,l_wrist)

            #get right elbow angle
            angle_right_elbow = calculate_angle(r_shoulder,r_elbow,r_wrist)

            #get right hip shoulder to wrist angle 
            angle_rhip_rshoulder_rwrist = calculate_angle(r_hip,r_shoulder,r_wrist)

            angle_lhip_lshoulder_lwrist = calculate_angle(l_hip,l_shoulder,l_wrist)

            cv2.putText(image, str(angle_left_elbow),
                        tuple(np.multiply(l_elbow, [int(video_width),int(video_height)]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (255,255,255), 2, cv2.LINE_AA)

            #Jab logic 
            if angle_left_elbow < 60:
                jab_stage = "Defense"
            if angle_left_elbow > 110 and jab_stage == "Defense":
                if angle_lhip_lshoulder_lwrist > 70:
                    if angle_right_elbow < 40:
                        jab_stage = "Offense"
                        jab_counter +=1

            #Straight punch logic
            if angle_right_elbow < 60:
                straight_stage = "Defense"
            if angle_right_elbow > 110 and straight_stage == "Defense":
                if angle_rhip_rshoulder_rwrist > 70:
                    if angle_left_elbow < 40:
                        straight_stage = "Offense"
                        straight_counter +=1

            #Create box for punch counter display   
            cv2.rectangle(image, (0,0), (240,70), (0,0,0), -1)

            #show jab counter on screen
            cv2.putText(image, "Jabs: ", (15,15), cv2.FONT_HERSHEY_COMPLEX, .6, (255,255,255), 1, cv2.LINE_AA) 
            cv2.putText(image, str(jab_counter), (85,15), cv2.FONT_HERSHEY_COMPLEX, .6, (255,255,255), 1, cv2.LINE_AA) 

            #show cross counter on screen
            cv2.putText(image, "Straights: ", (15,40), cv2.FONT_HERSHEY_COMPLEX, .6, (255,255,255), 1, cv2.LINE_AA) 
            cv2.putText(image, str(straight_counter), (125,40), cv2.FONT_HERSHEY_COMPLEX, .6, (255,255,255), 1, cv2.LINE_AA) 

            # Show offense vs defense 
            cv2.rectangle(image, ((int(video_width) - 200),0), (int(video_width),50), (off_vs_def_box), -1)
            cv2.putText(image, off_vs_def_text, ((int(video_width) - 180),30), cv2.FONT_HERSHEY_COMPLEX, .6, (255,255,255), 1, cv2.LINE_AA) 

            if jab_stage and straight_stage == "Defense":
                off_vs_def_box = [255,0,0]
                off_vs_def_text = "Defense"
            if jab_stage or straight_stage == "Offense":
                off_vs_def_box = [0,0,139]    
                off_vs_def_text = "Offense"
            if jab_stage and straight_stage == "Defense":
                off_vs_def_box = [255,0,0]
                off_vs_def_text = "Defense"

            #distance testing
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

            #Stance box
            cv2.rectangle(image, ((int(video_width) - 150),int(video_height - 50)), (int(video_width),int(video_height)), (255,255,255), -1)
            #Stance printed on screen
            cv2.putText(image, stance, ((int(video_width)-130),(int(video_height -30))), cv2.FONT_HERSHEY_COMPLEX, .5, (0,0,0), 1, cv2.LINE_AA) 

            print(stance_num)
            print (stance)

        except:
            pass

        
        # print(calculate_angle(l_shoulder, l_elbow, l_wrist))
        cv2.imshow('Mediapipe Feed', image)
                
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()


