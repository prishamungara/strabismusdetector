
# !/usr/bin/python3
from tkinter import *

from tkinter import messagebox

from calclib import * 
import pdb 
import settings 

#top = Tk()
#top.geometry("100x100")
#def hello():
#   messagebox.showinfo("Say Hello", "Hello World")

#B1 = Button(top, text = "Say Hello", command = hello)
#B1.place(x = 35,y = 50)


#top.mainloop()
import argparse

import cv2
import mediapipe as mp
import numpy as np

from custom.iris_lm_depth import from_landmarks_to_depth
from videosource import FileSource, WebcamSource

mp_face_mesh = mp.solutions.face_mesh


vertidx = [10,151,9,8,168,100,199,175,152]

points_idx = [33, 133, 362, 263, 61, 291, 199]
points_idx = list(set(points_idx))
points_idx.sort()

left_eye_landmarks_id = np.array([33, 133])
right_eye_landmarks_id = np.array([362, 263])

dist_coeff = np.zeros((4, 1))

YELLOW = (0, 255, 255)
GREEN = (0, 255, 0)
LGREEN = (0, 100, 0)
MGREEN = (0, 150, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)
SMALL_CIRCLE_SIZE = 1
LARGE_CIRCLE_SIZE = 2

def drawiriscenter(iris_landmarks, image_size, frame):
      for landmark in iris_landmarks:
          pos = (np.array(image_size) * landmark[:2]).astype(np.int32)
          frame = cv2.circle(frame, tuple(pos), SMALL_CIRCLE_SIZE, YELLOW, -1)
          break;

def drawaboveeyebrowlines(frame):
        frame = cv2.line(frame, settings.ebminp1,settings.ebminp2, LGREEN,2)
        frame = cv2.line(frame, settings.ebmaxp1,settings.ebmaxp2, MGREEN,2)
        return frame


def drawhorizandverticallines(frame):
        #pdb.set_trace()
        frame = cv2.line(frame, settings.vp1,settings.vp2, GREEN,2)
        frame = cv2.line(frame, settings.hp1,settings.hp2, GREEN,2)
        return frame

def main(inp):
    framecount=0
    settings.init()
    if inp is None:
        frame_height, frame_width = (720, 1280)
        #frame_height, frame_width = (1080, 1920)
        source = WebcamSource(width=frame_width, height=frame_height)
        readfromfile=0
    else:
        source = FileSource(inp)
        frame_width, frame_height = (int(i) for i in source.get_image_size())
        readfromfile=1
    #cv2.namedWindow("Display",cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Display",900, 900)

    image_size = (frame_width, frame_height)
    print(image_size)

    # pseudo camera internals
    focal_length = frame_width

    landmarks = None
    smooth_left_depth = -1
    smooth_right_depth = -1
    smooth_factor = 0.1
    if(readfromfile == 0):
        messagebox.showinfo("PREPARE FOR THE POSE ", "Stand 20-75cm away from the camera and look straight into the camera.")

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        for idx, (frame, frame_rgb) in enumerate(source):
            results = face_mesh.process(frame_rgb)
            multi_face_landmarks = results.multi_face_landmarks

            if multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                #print("number of points", len(face_landmarks.landmark))
                #printpoints(face_landmarks.landmark,ptidx)
                #mesh_points = np.array(np.multiply([p.x,p.y], [frame_width,frame_height]).astype(int) for p in face_landmarks.landmark) 
                #print(mesh_points)
                #drawvertical(mesh_points,ptidx)
               # print("\nlandmarks", face_landmarks.landmark)
                landmarks = np.array(
                    [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]
                )
                landmarks = landmarks.T
                #print(landmarks)
                #for ii in vertidx:
                #    pos = (np.array(image_size) * landmarks[:2, ii]).astype(np.int32)
                #    print (pos) 
                p1  = (np.array(image_size) * landmarks[:2, 10]).astype(np.int32)
                p2  = (np.array(image_size) * landmarks[:2, 200]).astype(np.int32)
                #frame = cv2.line(frame, p1,p2, GREEN,2)

                (
                    left_depth,
                    left_iris_size,
                    left_iris_landmarks,
                    left_eye_contours,
                ) = from_landmarks_to_depth(
                    frame_rgb,
                    landmarks[:, left_eye_landmarks_id],
                    image_size,
                    is_right_eye=False,
                    focal_length=focal_length,
                )

                (
                    right_depth,
                    right_iris_size,
                    right_iris_landmarks,
                    right_eye_contours,
                ) = from_landmarks_to_depth(
                    frame_rgb,
                    landmarks[:, right_eye_landmarks_id],
                    image_size,
                    is_right_eye=True,
                    focal_length=focal_length,
                )
                #print("Number of landmarks returned ", len(landmarks))

                if smooth_right_depth < 0:
                    smooth_right_depth = right_depth
                else:
                    smooth_right_depth = (
                        smooth_right_depth * (1 - smooth_factor)
                        + right_depth * smooth_factor
                    )

                if smooth_left_depth < 0:
                    smooth_left_depth = left_depth
                else:
                    smooth_left_depth = (
                        smooth_left_depth * (1 - smooth_factor)
                        + left_depth * smooth_factor
                    )

                # print(
                #    f"depth in cm: {smooth_left_depth / (10*2.54):.2f}, {smooth_right_depth / (10*2.54):.2f}"
                #)
                ldp = (smooth_left_depth/(10*2.54))
                rdp = (smooth_right_depth/(10*2.54))
             #   print("ldp", ldp, "rdp", rdp)
             #   print(f"size: {left_iris_size:.2f}, {right_iris_size:.2f}")

            if landmarks is not None:

                # draw subset of facemesh
                for ii in points_idx:
                    pos = (np.array(image_size) * landmarks[:2, ii]).astype(np.int32)
                  #  frame = cv2.circle(frame, tuple(pos), LARGE_CIRCLE_SIZE, GREEN, -1)

                # draw eye contours
                eye_landmarks = np.concatenate(
                    [
                        right_eye_contours,
                        left_eye_contours,
                    ]
                )
                for landmark in eye_landmarks:
                    pos = (np.array(image_size) * landmark[:2]).astype(np.int32)
                    frame = cv2.circle(frame, tuple(pos), SMALL_CIRCLE_SIZE, RED, -1)

                # draw iris landmarks
                iris_landmarks = np.concatenate(
                    [
                        right_iris_landmarks,
                        left_iris_landmarks,
                    ]
                )
                #print(len(right_iris_landmarks), len(left_iris_landmarks))
              #  print("\n****RIRIS Points are ")
    #            for landmark in right_iris_landmarks:
    #                pos = (np.array(image_size) * landmark[:2]).astype(np.int32)
                #    frame = cv2.circle(frame, tuple(pos), SMALL_CIRCLE_SIZE, YELLOW, -1)
                #    print(pos)
    #                print("x", pos[0], "y", pos[1])
    #                print("  ")
                drawiriscenter(right_iris_landmarks, image_size, frame)
                drawiriscenter(left_iris_landmarks, image_size, frame)
                framecount = framecount+1
                movefarther=0
                movecloser=0

                sldp= smooth_left_depth / 10
                srdp= smooth_right_depth / 10
                if((sldp < 20) and (srdp < 20)):
                   print("PRPR",sldp, srdp)
                   movefarther=1
                else:
                   if((sldp > 85) and (srdp >85)):
                     movecloser=1
                if(movecloser== 0 and movefarther==0):
                  processnewframe(image_size, landmarks, left_eye_contours, right_eye_contours, ldp, rdp, left_iris_size, right_iris_size, left_iris_landmarks, right_iris_landmarks,p1,p2)
                  printframestats()
                  frame=drawhorizandverticallines(frame)
                #frame=drawaboveeyebrowlines(frame)

                #if(framecount % 60):
                #   PopUpMessage("Pausing","Pausing") 
                #printdictionary()
               # print("\n****LIRIS Points are ")
                #for landmark in left_iris_landmarks:
                #    pos = (np.array(image_size) * landmark[:2]).astype(np.int32)
                #    frame = cv2.circle(frame, tuple(pos), SMALL_CIRCLE_SIZE, YELLOW, -1)
                   # print(pos)
                   # print("  ")
               #     kk = kk+1
               # kk=0
               # for landmark in iris_landmarks:
               #     pos = (np.array(image_size) * landmark[:2]).astype(np.int32)
                #    frame = cv2.circle(frame, tuple(pos), SMALL_CIRCLE_SIZE, YELLOW, -1)
               #     print("****LIRIS Points are")
               #     print(pos)
               #     print("\n")
               #     kk = kk+1

                # write depth values into frame
                depth_string = "{:.2f}cm, {:.2f}cm".format(
                    smooth_left_depth / 10, smooth_right_depth / 10
                )
                frame = cv2.putText(
                    frame,
                    depth_string,
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    GREEN,
                    2,
                    cv2.LINE_AA,
                )
                if(movefarther != 0):
                  frame = cv2.putText(
                    frame,
                    "MOVEFARTHER",
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    GREEN,
                    2,
                    cv2.LINE_AA,)
                else:
                 if(movecloser != 0):
                  frame = cv2.putText(
                    frame,
                    "MOVECLOSER",
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    GREEN,
                    2,
                    cv2.LINE_AA,)
                 else:
                   if(settings.strabismuspresent):
                     strabismus_status = "STRABISMUS DETECTED"
                   else:
                     strabismus_status = "Strabismus Not Present"

                   frame = cv2.putText(
                    frame,
                    strabismus_status,
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    GREEN,
                    2,
                    cv2.LINE_AA,)

            source.show(frame)
            if(settings.strabismuspresent):
                 #PopUpMessage("Strabismus status", "Strabismus Detected Please See Opthomologist");
                 print("Strabismus status is present")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Choose video file otherwise webcam is used."
    )
    parser.add_argument(
        "-i", metavar="path-to-file", type=str, help="Path to video file"
    )

    args = parser.parse_args()
    main(args.i)
