

discardedframes=0
RSLookingFCount=0
LSLookingFCount=0
CorrectFCount=0
FartherFrames = 0
totalframes = 0

#Thresholds
#lowdepth/highdepth ratios
# between 0.95 and 1.2 for normal
MINDEPTH_NORMAL = 0.95
MAXDEPTH_NORMAL = 1.2
# lowdsize/highsize ratios
# between 0.95 and 1.2 for normal
MINSIZE_NORMAL = 0.95
MAXSIZE_NORMAL = 1.2

#distance delta thresholds
DELTA_DIST_NORMAL_THRESHOLD = 1.40 


STATSTHRESHOLD = 100


HORIZ_LINE_DISTANCE = 300

#list of important global variables
# iris centers

def init():
     global licenter
     global ricenter
     global lisize
     global risize
     global ldp
     global rdp
     global vp1
     global vp2
     global hp2
     global hp1
     global ebminp1
     global ebminp2
     global ebmaxp1
     global ebmaxp2
     global deltax
     global deltay
     global hdistance
     global strabismuspresent
     global framecount
     global distdelta
     global iszminthreshold
     global iszmaxthreshold
     global sampledict

    
     iszminthreshold=0.75
     iszmaxthreshold=1.20
     distdelta = 10 
     framecount = 0
     strabismuspresent = False
     sampledict={}

