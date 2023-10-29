from tkinter import *
from tkinter import messagebox 
import pdb
import argparse

import cv2
import mediapipe as mp
import numpy as np
import math

import settings
sampledict = {}


def isaprxequal(pt1,pt2):
    if((abs(pt1[0]- pt2[0]) <= settings.deltax) and (abs(pt1[1]-pt2[1]) <= settings.deltay)):
       print("Pass",pt1,pt2, settings.deltax, settings.deltay)
       return True
    else:
       print("Fail", pt1,pt2, settings.deltax, settings.deltay)
       return False

def comparedist(d1,d2):
    if(abs(abs(d1)- abs(d2)) <= settings.distdelta):
       print("PassD",d1,d2)
       return 0
    else:
       print("FAILD",d1,d2,settings.distdelta)
       #pdb.set_trace()
       return(d1 - d2)

def compareirissizes(s1,s2):
    if((s1/s2) <= settings.iszminthreshold):
       print("small",s1,s2)
       return s1/s2
    else:
       if(s1/s2 >= settings.iszmaxthreshold):
         print("big",s1,s2)
         return s1/s2
       else:
           return 1
     
def findmode(list):
   status = False
   if(len(list) == 0):
     return status, 0 
   vals,counts = np.unique(list, return_counts=True)
   index = np.argmax(counts)
   print("Mode:",vals[index])
   status = True
   return  status, vals[index]

def calchorizdistance():
    return 0

def ishdistancevalid(lid,rid,hdistnace):
     mkey=formkey(lid,rid)
     if(mkey in sampledict):
          framedata = sampledict[mkey]
          if(len(framedata[0]) < 10):
             return False
          else:
             return True
              

def calccirclecenter(image_size, pts):
    cp= []
    ccp= []
    ymin=xmin=100000
    xmax=ymax=0
    for landmark in pts:
      pos = (np.array(image_size) * landmark[:2]).astype(np.int32)
      if(len(cp)):
        if(pos[0] < xmin):
           xmin=pos[0]
        if(pos[1] < ymin):
           ymin=pos[1]
        if(pos[0] > xmax):
           xmax=pos[0]
        if(pos[1] > ymax):
           ymax=pos[1]
      else:
           cp.append(pos[0])
           cp.append(pos[1])
    ccp.append((xmin + xmax)/2)
    ccp.append((ymin + ymax)/2)
    #if(ccp != cp):
    #print("reported Center calc center   ", cp, ccp)
    return cp;


def checkforstrabismus(image_sz, landmarks, ldp, rdp, lis, ris):
     #settings.strabismuspresent = False
     temp1  = (np.array(image_sz) * landmarks[:2, 221]).astype(np.int32)
     temp2  = (np.array(image_sz) * landmarks[:2, 55]).astype(np.int32)
     settings.deltax = abs((temp2[0] - temp1[0])/2.0)
     settings.deltay = abs((temp2[1] - temp1[1])/1.0)
     distance = math.dist(settings.licenter,settings.ricenter)

     if((isaprxequal(settings.hp1,settings.ricenter)== True) and (isaprxequal(settings.hp2, settings.licenter) == True)):
        print ("Both eyes are straight: Nothing to do")
        print("temp1, temp2", temp1, temp2)
        addtodictonary(ldp,rdp, lis, ris, distance)
     else:
       dresult=comparedist(distance, settings.hdistance)
       szresult = compareirissizes(lis,ris) 
       if(dresult < 0):
         print("DRESULT is < 0")
         if(szresult == 1):
             print("szresult ==1 ")
             if(ishdistancevalid(lid,rid,hdistance)):
                  print("Looking inwards both eyes ")
                  settings.strabismuspresent = True
                  print("temp1, temp2", temp1, temp2)
                  #nothing to do
                  return 0 
             else:
                  if(szresult < 1):
                     print("Looking Left Side ")
                  else:
                     print("Looking Right Side")
                     #pdb.set_trace()
       else:
         if(dresult == 0):
           print (" DRESULT is == 0")
         else:
            if(dresult > 0):
              print (" DRESULT is > 0")

          
     
def formkey(ldp,rdp):
      depval = int((ldp)*100)
      ldepth = ((int((depval % 10)/2))*2) + (int(depval - (depval %10)))
      depval = int((rdp)*100)
      rdepth = ((int((depval % 10)/2))*2) + (int(depval - (depval %10)))
      mkey=str(ldepth)+str(rdepth)
      return mkey
    
def addtodictonary(ldp,rdp, lis, ris, dist):
      distlist=[]
      ldplist=[]
      rdplist=[]
      lislist=[]
      rislist=[]
      mkey=formkey(ldp,rdp)
      #print("Calcdepth", depth)
      if(mkey in sampledict):
         framedata = sampledict[mkey]
         framedata[0].append(dist)
         framedata[1].append(ldp)
         framedata[2].append(rdp)
         framedata[3].append(lis)
         framedata[4].append(ris)
         #print("appended to list at ", mkey)
      else:
         #print("newlist  added at ", mkey)
         distlist.append(dist) 
         ldplist.append(ldp) 
         rdplist.append(rdp) 
         lislist.append(lis) 
         rislist.append(ris) 
         framedata = [distlist, ldplist, rdplist, lislist, rislist]
         sampledict[mkey] = framedata

def calcdistance(ldp,rdp,cdist):
     mkey=formkey(ldp,rdp)
     distlist = []
     if(mkey in sampledict):     
        valrec = sampledict[mkey]
        distlist = valrec[0]
     (modestatus, mode) = findmode(distlist) 
     print("Mode: mkey",mode,mkey)
     if(modestatus == True):
          dist=mode
     else:
          dist = cdist 
          print("Mode not taken from list")
     return (-1*dist)

def processnewframe(image_sz, landmarks, lec, rec, ldp, rdp, lis, ris, lpts, rpts, p1, p2):
     print("Frame # is:", (settings.framecount+1))
     settings.framecount = settings.framecount + 1;
     settings.licenter = calccirclecenter(image_sz, lpts)
     settings.ricenter = calccirclecenter(image_sz, rpts)
     settings.lisize = lis
     settings.risize = ris
     settings.ldp = ldp
     settings.rdp = rdp
     settings.vp1=p1
     settings.vp2=p2
     settings.hp1=settings.ricenter
     settings.ebminp1  = (np.array(image_sz) * landmarks[:2, 222]).astype(np.int32)
     settings.ebminp2  = (np.array(image_sz) * landmarks[:2, 442]).astype(np.int32)
     settings.ebmaxp1  = (np.array(image_sz) * landmarks[:2, 223]).astype(np.int32)
     settings.ebmaxp2  = (np.array(image_sz) * landmarks[:2, 443]).astype(np.int32)
     temp1 = (settings.ebmaxp1 + settings.ebminp1)/2
     #temp1[0] = temp1[0]-5
     temp2 = (settings.ebmaxp2 + settings.ebminp2)/2
     dist = math.dist(temp1,temp2)
     #addtodictonary(ldp,rdp, lis, ris, dist)
     settings.hdistance = calcdistance(ldp,rdp, dist)
     settings.hp2=calc_hpt2(settings.vp1, settings.vp2, settings.hp1, settings.hdistance)    
     print("temp1, temp2, maxpt1, minpt1,ebmaxpt2, minpt2, dist",temp1, temp2, settings.ebmaxp1, settings.ebminp1, settings.ebmaxp2, settings.ebminp2, settings.hdistance)
     checkforstrabismus(image_sz, landmarks,ldp,rdp,lis,ris)

     return 0




def  PopUpMessage(wintitle, msg):
   messagebox.showinfo(wintitle, msg)


def equationroots( a, b, c): 
  
    # calculating discriminant using formula
    dis = b * b - 4 * a * c 
    sqrt_val = math.sqrt(abs(dis)) 
      
    # checking condition for discriminant
    if dis > 0: 
        print(" real and different roots ") 
        print((-b + sqrt_val)/(2 * a)) 
        print((-b - sqrt_val)/(2 * a)) 
        return ((-1*b + sqrt_val)/(2*a)), ((-1*b - sqrt_val)/(2*a))

    elif dis == 0: 
        print(" real and same roots") 
        #print(-b / (2 * a)) 
        #pdb.set_trace()
        return ((-1*b)/(2*a)), ((-1*b)/(2*a))
      
    # when discriminant is less than 0
    else:
        print("Complex Roots") 
        print(- b / (2 * a), " + i", sqrt_val) 
        print(- b / (2 * a), " - i", sqrt_val) 
        return (-1,-1)

#if distance = -1, draw left of hpt1, distance =1 right of hpt1 
def calc_hpt2(vpt1, vpt2, hpt1, d): 
        a=b=c=x2=0.0
        hpt2 = []
        #pdb.set_trace()
        if((vpt2[0] - vpt1[0]) != 0):
           m=(vpt2[1]-vpt1[1])/(vpt2[0]-vpt1[0])
           newm = (-1/m)
        else:
           newm=0
        if(newm == 0):
           x2 = hpt1[0] + d
           y2 = hpt1[1]
        else:
           ycept = hpt1[1] - (newm*hpt1[0])
           x= hpt1[0] + int(d)
           y = newm*x + ycept 
           print(x)
           a = newm*newm
           b = (2*newm*ycept - 2*newm*hpt1[1])
           c = hpt1[1]*hpt1[1] - 2 * ycept *hpt1[1] + ycept*ycept
           print(a,b,c)
           #pdb.set_trace()
           x21, x22 = equationroots(a,b,c) 
           print("HEY", x21, x22)
           if(x21 == -1):
             print("error")
             x2= hpt1[0] + int(d)
             y2 = newm*x + c 
             #print(x2,y2)
           else:
             if(x21 < 0):
                x2 = x22
             else:
                x2 = x21
           y2 = newm*x2 + ycept 

        #pdb.set_trace()
        print(x2,y2)
        hpt2.append((x2.astype(np.int32)))
        hpt2.append((y2.astype(np.int32)))
        print(hpt1, hpt2) 
        return hpt2

#if distance = -1, draw left of hpt1, distance =1 right of hpt1 
#def calc_hpt2(vpt1, vpt2, hpt1, d): 
#        hpt2 = []
#        #pdb.set_trace()
#        if((vpt2[0] - vpt1[0]) != 0):
#           m=(vpt2[1]-vpt1[1])/(vpt2[0]-vpt1[0])
#           newm = (-1/m)
#        else:
#           newm=0
#        c = hpt1[1] - (newm*hpt1[0])
#        x= hpt1[0] + int(d)
#        y = newm*x + c 
#        print(x)
#        hpt2.append(int(x))
#        hpt2.append(int(y))
#        print(hpt1, hpt2) 
#        return hpt2
    

def printframestats():
    print("\n***************************************")
    print("Total Frames    : ", settings.framecount)
    print("Left Iris Center: ", settings.licenter)
    print("Left Iris EP    : ", settings.hp2)
    print("Rght Iris Center: ", settings.ricenter)
    print("Rght Iris EP    : ", settings.hp1)
    print("Left Iris Size  : ", settings.lisize)
    print("Rght Iris Size  : ", settings.risize)
    print("Horizdistance   : ", settings.hdistance)
    print("Left Iris Depth : ", settings.ldp)
    print("Rght Iris Depth : ", settings.rdp)

    print("\nDebugStats    : ")
    print("Vert Top Point  : ", settings.vp1)
    print("Vert Bottom Pt  : ", settings.vp2)
    print("EyeBrow Min Pt1 : ", settings.ebminp1)
    print("EyeBrow Min Pt2 : ", settings.ebminp2)
    print("EyeBrow Max Pt1 : ", settings.ebmaxp1)
    print("EyeBrow Max Pt2 : ", settings.ebmaxp2)
    print("***************************************\n")







