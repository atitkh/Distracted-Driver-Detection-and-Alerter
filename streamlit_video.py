from cProfile import label
import tempfile
import streamlit as st
import cv2
import numpy as np
from driver_prediction import predict_result
from PIL import Image as im
from matplotlib import pyplot as plt
import time
import csv
import openpyxl
from send_sms import sendSMS

image_row = 2

st.markdown("<h1 style='text-align: center; color: cyan; text-decoration: underline;'>Distracted Driver Detection</h1>", unsafe_allow_html=True)
fig = plt.figure()

OUTPUT_VIDEO_FILE = "output_video.mp4"
wrkb = openpyxl.Workbook()
ws = wrkb.worksheets[0]
ws.append(["Image", "Action", "Time"])

# define number of cameras to display
cam1, cam2, cam3= st.columns(3)


def main():
    setup(cam1, "Camera 1", "Ram Oli", "BA 1 Ja 2200",
          "null", image_row, alerted=False)
    setup(cam2, "Camera 2", "Hari G.C.", "BA 4 Ja 1002",
          "null", image_row, alerted=False)


def setup(camID, camName, driverName, numberPlate, label, image_row, alerted):

    camID.markdown("<h2 style='text-align: left; color: white; text-decoration: underline;'>" +
                   camName+"</h2>", unsafe_allow_html=True)
    stdriver = camID.empty()
    camID.markdown(
        "<h4 style='text-align: left; color: white;'> Driver Info : </h4>", unsafe_allow_html=True)
    camID.write("Name : " + driverName)
    camID.write("Number Plate : " + numberPlate)

    camID.write("#")
    camID.write("#")

    # initialize video output and text output frames
    stloading = camID.empty()
    stframe = camID.empty()
    sttext = camID.empty()

    f = camID.file_uploader("Upload file", key=camID)
    tfile = tempfile.NamedTemporaryFile(delete=False)
    if f is not None:
        tfile.write(f.read())

    vs = cv2.VideoCapture(tfile.name)

    camID.write("#")
    class_btn = camID.button("Classify", key=camID)
    stop_btn = camID.button("Stop", key=camID)

    # Show uploaded image on site
    # if file_uploaded is not None:
    #     image = Image.open(file_uploaded)
    #     st.image(image, caption='Uploaded Image', use_column_width=True)

    if class_btn:
        if f is None:
            camID.write(
                "Invalid command, please upload a video or live stream")
        else:
            with st.spinner("Classifying..."):
                writer = None
                (W, H) = (None, None)
                # loop over frames from the video file stream
                while True:
                    # read the next frame from the file
                    # vs = cv2.VideoCapture(0) for live feed from camera
                    (grabbed, frame) = vs.read()

                    # if the frame was not grabbed, then we have reached the end of the stream
                    if not grabbed:
                        stframe.empty()
                        sttext.write("Video Ended")
                        break

                    # if the frame dimensions are empty, grab them
                    if W is None or H is None:
                        (H, W) = frame.shape[:2]

                    # clone the output frame, then convert it from BGR to RGB ordering
                    output = frame.copy()
                    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
                    output2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # prepare video frame for model input
                    frame = cv2.flip(frame, 1)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (128, 128))
                    frame = np.expand_dims(frame, axis=0).astype(
                        'float32') / 255 - 0.5

                    # make predictions on the frame and then update the predictions queue
                    previous_label = label
                    label = predict_result(frame)

                    if label == "TEXTING_LEFT" or label == "TEXTING_RIGHT":
                        if alerted == False:
                            message = "Driver " + driverName + \
                                " is distracted and texting in car number " + numberPlate
                            sendSMS(message,'9860851205')
                            alerted = True

                    # draw the activity on the output frame
                    text = "activity: {}".format(label)
                    cv2.putText(output, text, (35, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                    if previous_label != label:
                        # create log
                        im.fromarray(output2).save(
                            "temp_images/" + camName+str(image_row)+".jpg")
                        img = im.open("temp_images/" + camName +
                                      str(image_row)+".jpg")
                        # img = img.resize((140, 92))
                        # img.save(camName+".jpg")

                        img = openpyxl.drawing.image.Image(
                            "temp_images/" + camName+str(image_row)+".jpg")
                        img.height = 150
                        img.width = 200
                        img.anchor = 'A' + str(image_row)
                        # ws.add_image(img)

                        # define time of action
                        seconds = time.time()
                        local_time = time.ctime(seconds)

                        # save log to excel file
                        data = ["", label, local_time]
                        ws.append(data)
                        ws.add_image(img)

                        # adjust cell height and width
                        ws.row_dimensions[image_row].height = 130
                        ws.column_dimensions['A'].width = 30
                        ws.column_dimensions['B'].width = 30
                        ws.column_dimensions['C'].width = 30
                        image_row += 1

                        # set output file name
                        wrkb.save("logs/"+camName+".xlsx")

                    # alert system

                    # check if the video writer is None
                    # if writer is None:
                    #     # initialize our video writer
                    #     fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    #     writer = cv2.VideoWriter(OUTPUT_VIDEO_FILE, fourcc, 30,
                    #                              (W, H), True)
                    # # write the output frame to disk
                    # writer.write(output)

                    # show the output image
                    # st.write(label)
                    sttext.write(label)
                    stframe.image(output)
                    key = cv2.waitKey(1) & 0xFF

                    # if the `q` key was pressed, break from the loop
                    if stop_btn:
                        break

                # release the file pointers
                print("[INFO] cleaning up...")
                # writer.release()
                vs.release()

# if __name__ == '__main__':
#     main()


main()
