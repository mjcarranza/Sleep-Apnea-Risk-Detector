# Use OpenCV to get images from the camera
import cv2

# Function to get an image and send it to the sleeping pose detection model
# Return true for a bad position or false for a good one.
# Return the actual sleeping position
def getSleepingPosition():

    # Usa la webcam externa (según tu salida está en /dev/video0)
    cap = cv2.VideoCapture("/dev/video0")

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara externa")
        exit()

    # Configura resolución 1080p
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo leer el frame")
        

    cv2.imshow("Webcam externa - 1080p", frame)

    # save this picture to the corresponding folder. (the one for the current reccording session)
    # data/raw/*Session Number*
    cv2.imwrite("captura_1080p.jpg", frame) 
    print("✅ Foto guardada como captura_1080p.jpg")

    cap.release()
    cv2.destroyAllWindows()

    ## use the Model here to get the position

    ## pass it to the trigger alarm in case it's a bad position

def triggerAlarm():
    # trigger alarm code here...
    pass

getSleepingPosition()