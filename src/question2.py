import cv2 as cv
import numpy as np

def func_Region_of_Interest_Mask(image):
    height = image.shape[0]
    width = image.shape[1]
    mask = np.zeros((height, width), dtype='uint8') #making a mask of that size
    triangular_area_of_interest = np.array([[(90, height), (width/2, height/2), (920, height),]], np.int32) #creating a triangular area
    cv.fillPoly(mask, triangular_area_of_interest, 255) #filling the triangular area of the mask
    image_with_ROI = cv.bitwise_and(image, mask) #it dies bit wise and operation all over the image to give region of interest
    return image_with_ROI


capture = cv.VideoCapture('inputs/whiteline.mp4') #create an instance of VideoCapture class and store it in a variable
# # Make video of output
# video  = cv.VideoWriter('question2_output_video.avi', cv.VideoWriter_fourcc(*'XVID'), 10, (540, 960))
while True: #enter while loop to read video frame by frame
    isTrue, frame = capture.read() #reading frame by frame and storing in a variable
    if not isTrue:
        break
    gray_image = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    smoothed_image = cv.GaussianBlur(gray_image,(9, 9),0)
    edge_detected = cv.Canny(gray_image, 50, 160) #applying canny edge detector
    image_with_ROI = func_Region_of_Interest_Mask(edge_detected)
    
    
    ###### detect the solid line first #####
    lines = cv.HoughLinesP(image_with_ROI, 1, np.pi/180, 200, np.array([]), minLineLength=160, maxLineGap=5)
    #the parameters are tuned so as to elimate the dashed lines and detect only solid line

    #now we take an average of starting and ending coordinates of the multiple line in each frame so that we can represent them as single one

    # Take the average(mean) of each of the beginning and ending coordinates in the lines
    x1 = int(np.mean(lines[:,:,0]))                              
    y1 = int(np.mean(lines[:,:,1]))  
    x2 = int(np.mean(lines[:,:,2]))             
    y2 = int(np.mean(lines[:,:,3]))

    # now we need to put a solid line (non flickering) to represent the solid lane
    # for that we need the lowest point and highest point on the line
    # for that we first find the slope and intercept of the mean line using the slope-intercept form
    slope = float(y2 - y1)/float(x2 - x1)
    intercept = y1 - slope * x1

    #now we find out the lowest and highest points on the line using our slope and intercept
    y_start = 303 #this value has been calculated so as to show that line starts from the vanishing point of lane
    x_start = int((y_start-intercept)/slope)
    y_end = int(frame.shape[0])
    x_end = int((y_end-intercept)/slope)

    cv.line(frame, (x_start,y_start), (x_end,y_end), (0,255,0),10) #Green for solid line

    ####### Now we detect only the dashed line ######
    
    #The idea here is to take the slope from the previous solid lines compare if its positive or negative
    #perform hough transform again to get the new lines, this time making sure we get dashed lines too
    #calculate the calculate its slope
    #if slope of solid lines are +ve then take only the lines (new ones) whose slope are -ve which represent the dashed lines in this case
    #if slope of solid lines are -ve then take only the lines (new ones) whose slope are +ve which represent the dashed lines in this case

    lines = cv.HoughLinesP(image_with_ROI, 1, np.pi/180, threshold = 10, minLineLength = 20, maxLineGap = 30)
    #find all lines in image

    dashed_list = []
    if slope > 0: #checking slope from previous solid lines
        if lines is not None:
            for i in range (0, len(lines)):
                l = lines[i][0]
                other_slope = float(l[3]-l[1])/float(l[2]-l[0])
                if other_slope < 0:
                    dashed_list.append([l[0],l[1],l[2],l[3]])
    
    if slope < 0: #checking slope from previous solid lines
        if lines is not None:
            for i in range(0, len(lines)):
                l  = lines[i][0]
                other_slope = float(l[3]-l[1])/float(l[2]-l[0])
                if other_slope > 0:
                    dashed_list.append([l[0], l[1], l[2], l[3]])

    dashed_lines_array = np.array(dashed_list)

    # Take the average(mean) of each of the beginning and ending coordinates in the lines
    x1 = int(np.mean(dashed_lines_array[:,0]))                              
    y1 = int(np.mean(dashed_lines_array[:,1]))  
    x2 = int(np.mean(dashed_lines_array[:,2]))             
    y2 = int(np.mean(dashed_lines_array[:,3]))

    # now we need to put a solid line (non flickering) to represent the dashed lane
    # for that we need the lowest point and highest point on the line
    # for that we first find the slope and intercept of the mean line using the slope-intercept form
    slope = float(y2 - y1)/float(x2 - x1)
    intercept = y1 - slope * x1

    #now we find out the lowest and highest points on the line using our slope and intercept
    y_start = 303 #this value has been calculated so as to show that line starts from the vanishing point of lane
    x_start = int((y_start-intercept)/slope)
    y_end = int(frame.shape[0])
    x_end = int((y_end-intercept)/slope)    

    cv.line(frame, (x1,y1),(x2,y2), (0,0,255),10) #red for dashed line

    cv.imshow('Lanes', frame) #display the video frame by frame
    # video.write(frame)  #save the video frame by frame
    if cv.waitKey(20) & 0xFF==ord('d'): #breakout when key d is pressed
        break

capture.release() #release the capture device
cv.destroyAllWindows() #destroy all windows because we don't need it anymore