import numpy as np
import cv2 as cv

# The argument 0 corresponds to /dev/video0, the first found camera.  In this case it is the USB camera.
cap = cv.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Remove color information to compact data
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Display the resulting frame
    #cv.imshow('frame',gray)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

    # print('gray',gray)
    if True:
        # face detection and other logic goes here
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            print('face detected at', x, y, w, h)
            # your logic goes here; for instance
            # cut out face from the frame.. 
            # rc,png = cv.imencode('.png', face)
            # msg = png.tobytes()
            # ...
        
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
