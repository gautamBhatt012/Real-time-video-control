# basically in this attempt we have solved the eye problem also , we scan eye using the mediapipe only and we are done 


import cv2
import mediapipe as mp      # to detect the landmarks
import pyautogui            # to connect keyboard and the gestures
import time                 # was unable to detect , it counted 1,2,3 before even 5 finger o multiple outcome were there 



def case_count_fingers(lst):     # landmark k hisab se finger count kr lenge fir uske hisab se play/pause vgera jo bhi krna h vo kr denge 
    cnt = 0

    thresh = (lst.landmark[0].y*100  - lst.landmark[9].y*100)/2       #landmark 0-9 ki value ki half value store kr lia thresh me or 100 se multiply sab jgh kra denge taki bada digit dikhe or calculation me asani ho 

    #for all five finger  :: play /pause
    if(lst.landmark[5].y*100  - lst.landmark[8].y*100 ) > thresh and (lst.landmark[9].y*100  - lst.landmark[12].y*100 ) > thresh and (lst.landmark[13].y*100  - lst.landmark[16].y*100 ) > thresh and (lst.landmark[17].y*100  - lst.landmark[20].y*100 ) > thresh and (lst.landmark[5].x*100  - lst.landmark[4].x*100 ) > 5:
        cnt=10
   

    # upar wale function se right hand k fist bnd or kholne k liye variable perfect h, left k liye humne thumb k variable ko alag se set kiya
    elif(lst.landmark[5].y*100  - lst.landmark[8].y*100 ) > thresh and (lst.landmark[9].y*100  - lst.landmark[12].y*100 ) > thresh and (lst.landmark[13].y*100  - lst.landmark[16].y*100 ) > thresh and (lst.landmark[17].y*100  - lst.landmark[20].y*100 ) > thresh and ( lst.landmark[4].x*100 -lst.landmark[5].x*100 ) > 5:
        cnt=10

    #for the first two finger :: increase volume
    elif(lst.landmark[5].y*100  - lst.landmark[8].y*100 ) > thresh and (lst.landmark[9].y*100  - lst.landmark[12].y*100 ) > thresh:
        cnt=2
    
    #for the first finger :: deecrease volume
    elif(lst.landmark[5].y*100  - lst.landmark[8].y*100 ) > thresh:
        cnt=1
    
    #for seek left 
    elif(lst.landmark[5].x*100  - lst.landmark[4].x*100 ) > 11:      # pehle 5 value dala tha to kai baar jb apn fist bana rhe the to thoda sa angutha bahar hone k karan seek position me chla ja rha tha ab 11 krne se uski limit badh gyi or system set ho gya  
        cnt=3

    #for seek right 
    elif(lst.landmark[4].x*100 - lst.landmark[5].x*100 ) > 11:
        cnt=4
    
    

    else:
        cnt=0

    return cnt
  

cap = cv2.VideoCapture(0)


#EYE FUNCTION
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# Function to detect eye closure
def is_eye_closed(face_landmarks):
    # Assuming the first two points are the eyes
    left_eye = face_landmarks.landmark[36:42]
    right_eye = face_landmarks.landmark[42:48]
    
    # Calculate the distance between the eyes
    eye_distance = abs(left_eye[0].x - right_eye[0].x)
    
    # Threshold for eye closure (you may need to adjust this)
    eye_closure_threshold = 0.05
    
    return eye_distance < eye_closure_threshold


drawing = mp.solutions.drawing_utils
hands = mp.solutions.hands
hand_obj = hands.Hands(max_num_hands=1)

prev = -1   #to limit the cnt else whatever it finds true ,will occur infinite number of time 
start_init = False        #no finger detected on screen 

# MAIN LOOP 
prev_eye_closed_time = 0
while True:
    end_time = time.time()      #end time 
    _, frm = cap.read()
    frm =cv2.flip(frm, 1)   #flip the camera outcome 

    res = hand_obj.process(cv2.cvtColor(frm,cv2.COLOR_BGR2RGB))    #Open cv2 reads in rgb format we have read in bgr format
   
    if res.multi_hand_landmarks:   #If number of hands> 0 
        
        hand_keyPoints = res.multi_hand_landmarks[0]
       
        cnt = case_count_fingers(hand_keyPoints)

        if not(prev == cnt):            # hand gesture is changing
            if not(start_init):
                start_time = time.time()        # start hone ka time note kiya, add krte gye 
                start_init = True
            elif (end_time-start_time) > 0.2:   # end k time or start time k bich ka antar , taaki multiple na count krle 
                if (cnt == 1):
                    pyautogui.press("down")
                elif (cnt == 2):
                    pyautogui.press("up")
                elif (cnt == 3):
                    pyautogui.press("left")                    
                elif (cnt == 4):
                    pyautogui.press("right")                    
                elif (cnt == 10):
                    pyautogui.press("space")    

                prev=cnt
                start_init=False
        # Adding else block for continuation in the seeking and volume thing 
        else:
            if not(start_init):
                start_time = time.time()        # start hone ka time note kiya, add krte gye 
                start_init = True
                #decresed the time a little bit as 0.2 was too large and made the scrolling slow
            elif (end_time-start_time) > 0.05:   #end k time or start time k bich ka antar , taaki multiple na count krle 
                if (cnt == 1):
                    pyautogui.press("down")
                elif (cnt == 2):
                    pyautogui.press("up")
                elif (cnt == 3):
                    pyautogui.press("left")                    
                elif (cnt == 4):
                    pyautogui.press("right")
                prev=cnt
                start_init=False
        drawing.draw_landmarks(frm, hand_keyPoints, hands.HAND_CONNECTIONS)     # isse basically red point aaega or vo connected rahega 
    
    
    

    # Check for eye closure
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_results = face_mesh.process(frame_rgb)
    if face_results.multi_face_landmarks:
        for face_landmarks in face_results.multi_face_landmarks:
            if is_eye_closed(face_landmarks):
                current_time = time.time()
                if prev_eye_closed_time == 0:
                    prev_eye_closed_time = current_time
                elif current_time - prev_eye_closed_time > 20:
                    pyautogui.press("space") # Pause the video
                    prev_eye_closed_time = 0 # Reset the timer
            else:
                prev_eye_closed_time = 0 # Reset the timer if eyes are open
    
    cv2.imshow("window", frm)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.release()
        break
