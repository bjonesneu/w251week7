import numpy as np
import cv2 as cv

# The argument 0 corresponds to /dev/video0, the first found camera.  In this case it is the USB camera.
cap = cv.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Remove color information to compact data
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Display the resulting frame
    #cv.imshow('frame',frame_gray)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

    # print('grayframe',frame_gray)
    if True:
        # face detection and other logic goes here
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(frame_gray, 1.3, 5)
        for (x,y,w,h) in faces:
            print('face detected at', x, y, w, h)
            cv.rectangle(frame_gray, (x, y), (x+w, y+h), (255, 255, 255), 2)
            face = frame_gray[y:y+h,x:x+w]
            #cv.imshow('frame',face)
            # cut out face from the frame... 
            rc,png = cv.imencode('.png', face)
            # msg = png.tobytes()
            # ...

    cv.imshow('frame',frame_gray)

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

