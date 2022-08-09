import cv2
import mediapipe as mp 
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

jab_counter = 0
straight_counter = 0
jab_stage = None
straight_stage = None

# VIDEO FEED
cap = cv2.VideoCapture(0)
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

            #get elbow angle
            angle_left_elbow = calculate_angle(l_shoulder,l_elbow,l_wrist)

            #get elbow angle
            angle_right_elbow = calculate_angle(r_shoulder,r_elbow,r_wrist)

            #display angle
            cv2.putText(image, str(angle_left_elbow),
                        tuple(np.multiply(l_elbow, [640,480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (255,255,255), 2, cv2.LINE_AA)
            # print(np.multiply(l_elbow, [640,480]).astype(int))    

            #Jab logic 
            if angle_left_elbow < 30:
                jab_stage = "Defense"
            if angle_left_elbow > 140 and jab_stage == "Defense":
                jab_stage = "Offense"
                jab_counter +=1
                print(jab_counter)

            #Cross logic
            if angle_right_elbow < 30:
                straight_stage = "Defense"
            if angle_right_elbow > 140 and straight_stage == "Defense":
                straight_stage = "Offense"
                straight_counter +=1
                print("Cross is: " + str(straight_counter))


            #Create box for punch counter display   
            cv2.rectangle(image, (0,0), (255,73), (0,0,255), -1)

            #show jab counter on screen
            cv2.putText(image, "Jabs: ", (15,15), cv2.FONT_HERSHEY_COMPLEX, .5, (255,255,255), 1, cv2.LINE_AA) 
            cv2.putText(image, str(jab_counter), (85,15), cv2.FONT_HERSHEY_COMPLEX, .5, (255,255,255), 1, cv2.LINE_AA) 

            #show cross counter on screen
            cv2.putText(image, "Straights: ", (15,40), cv2.FONT_HERSHEY_COMPLEX, .5, (255,255,255), 1, cv2.LINE_AA) 
            cv2.putText(image, str(straight_counter), (125,40), cv2.FONT_HERSHEY_COMPLEX, .6, (255,255,255), 1, cv2.LINE_AA) 


        except:
            pass

        
        # print(calculate_angle(l_shoulder, l_elbow, l_wrist))
        cv2.imshow('Mediapipe Feed', image)
                
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()


