import cv2 as cv
import numpy as np

capture = cv.VideoCapture('inputs/challenge.mp4') #create an instance of VideoCapture class and store it in a variable

# Make video of output
video  = cv.VideoWriter('question3_output_video.avi', cv.VideoWriter_fourcc(*'XVID'), 10,(1216,576))

while True: #enter while loop to read video frame by frame
    isTrue, frame = capture.read() #reading frame by frame and storing in a variable
    if not isTrue:
        break
    my_image = frame.copy() #making a copy of frame to perform operation on
    gray_image = cv.cvtColor(my_image, cv.COLOR_BGR2GRAY)

    # this thresholded image is used to show along with other videos in output
    ret, thresh = cv.threshold(gray_image, 180, 255, cv.THRESH_BINARY)
    #since other videos will have three channels and a thresholded image only one, we make into three channels
    #replicating the single channel into all channels
    three_channel_thresh_original = np.zeros((thresh.shape[0], thresh.shape[1],3), dtype = 'uint8')
    three_channel_thresh_original[:,:,0] = thresh #same image in all channels
    three_channel_thresh_original[:,:,1] = thresh
    three_channel_thresh_original[:,:,2] = thresh

    #select a region of interest and warp it to perform operations on lane
    #create a blank image to store the warped image
    blank_image = np.zeros((600, 400, 3), dtype = 'uint8')
    src_points = np.array([[150,680],[540,440],[735,440],[1230,680]]) #choosing four points as source
    dst_points = np.array([[0,blank_image.shape[0]],[0,0],[blank_image.shape[1],0],[blank_image.shape[1],blank_image.shape[0]]])
    H_Matrix, mask = cv.findHomography(src_points, dst_points) #perform homography between the source and destination points
    warped_image = cv.warpPerspective(frame, H_Matrix, (blank_image.shape[1], blank_image.shape[0]))

    #we need to show this warped image in final output and show it as binary image
    gray_warped_image = cv.cvtColor(warped_image, cv.COLOR_BGR2GRAY) #first convert to grayscale
    ret, thresh_warped_image = cv.threshold(gray_warped_image, 180, 255, cv.THRESH_BINARY)
    #since other videos will have three channels and a thresholded image only one, we make into three channels
    #replicating the single channel into all channels
    three_channel_thresh_warped = np.zeros((thresh_warped_image.shape[0], thresh_warped_image.shape[1], 3), dtype = 'uint8')
    three_channel_thresh_warped[:,:,0] = thresh_warped_image #same image in all channels
    three_channel_thresh_warped[:,:,1] = thresh_warped_image
    three_channel_thresh_warped[:,:,2] = thresh_warped_image

    #since the three channel thresholded warped image will be needed to perform other operation as well, we make a copy
    three_channel_thresh_warped_copy = three_channel_thresh_warped.copy()

    #to make line, make blank image to be overlapped on given image
    blank_image = np.zeros_like(warped_image)


    ##### Now lets first detect the lane with white colour #####

    #we work on the warped image again as we need to do thresholding again to detect only white lines
    gray_warped_image_white_line = cv.cvtColor(warped_image, cv.COLOR_BGR2GRAY)
    ret, thresh_warped_image_white_line = cv.threshold(gray_warped_image_white_line, 225, 255, cv.THRESH_BINARY)

    #now that we have an image with only white line, we need to find the coordiantes of the white pixels
    white_line_coordinates = np.where(thresh_warped_image_white_line == 255) #where ever pixel value is 255 is white 

    #new we fit a curve of degree two over these points
    polynomial_coeffs = np.polyfit(white_line_coordinates[0][:], white_line_coordinates[1][:], 2)

    #now lets find extrapolated coordinate values for the curve itself so that we can draw a line along the lane
    y_coordinates = np.linspace(0, warped_image.shape[0], 40) #40 values for y
    x_coordinates = np.polyval(polynomial_coeffs, y_coordinates)

    #lets convert these coordinates into an array
    white_lane_coordinates = np.asarray([x_coordinates, y_coordinates])
    white_lane_coordinates = white_lane_coordinates.T #taking their transpose
    white_lane_coordinates = white_lane_coordinates.astype(np.int32) #cast it to int type

    #now lets plot the lines on the images
    cv.polylines(blank_image, [white_lane_coordinates], False, (0,0,255), thickness = 10) #plot it on blank image
    cv.polylines(three_channel_thresh_warped_copy, [white_lane_coordinates], False, (0,0,255), thickness = 2) #plot it on warped thresholded image


    
    # draw detected white line coordinates on three channel warped threshold image
    for points in white_lane_coordinates:
        points = tuple(points) #converting points into tuple
        if points[1] == 600:
            continue
        if thresh_warped_image_white_line[points[1],points[0]] == 0:
            continue
        cv.circle(three_channel_thresh_warped_copy,points, 10, (0,255,255),thickness = 2) #draw circle around these points

    # now lets calculate the radius of curvature of the white lane
    radius_curvature_white_lane = np.abs(float((1 + (2*polynomial_coeffs[0]*y_coordinates[20] + polynomial_coeffs[1])**2)**(3.0/2.0))/float(2*polynomial_coeffs[0]))


    ##### Now lets next detect the lane with yellow colour #####
    #Here we convert the image into HSV domain and apply a filter for getting only yellow lines
    hsv_image = cv.cvtColor(warped_image, cv.COLOR_BGR2HSV)
    low_level = np.array([10,100,160])
    up_level = np.array([35,255,255])
    yellow_filter_image = cv.inRange(hsv_image, low_level, up_level)

    #now that we have an image with only yellow line, we need to find the coordiantes of the yellow pixels
    yellow_line_coordinates = np.where(yellow_filter_image == 255) #wherever pixel value is 255 is yellow

    #new we fit a curve of degree two over these points
    polynomial_coeffs = np.polyfit(yellow_line_coordinates[0][:], yellow_line_coordinates[1][:], 2)

    #now lets find extrapolated coordinate values for the curve itself so that we can draw a line along the lane
    y_coordinates = np.linspace(0, warped_image.shape[0], 40) #40 values for y
    x_coordinates = np.polyval(polynomial_coeffs, y_coordinates)

    #lets convert these coordinates into an array
    yellow_lane_coordinates = np.asarray([x_coordinates, y_coordinates])
    yellow_lane_coordinates = yellow_lane_coordinates.T #taking their transpose
    yellow_lane_coordinates = yellow_lane_coordinates.astype(np.int32) #cast it to int type

    #now lets plot the lines on the images
    cv.polylines(blank_image, [yellow_lane_coordinates], False, (0,0,255), thickness = 10) #plot it on blank image
    cv.polylines(three_channel_thresh_warped_copy, [yellow_lane_coordinates], False, (0,0,255), thickness = 2) #plot it on warped thresholded image

    # draw detected yellow line coordinates on three channel warped threshold image
    for points in yellow_lane_coordinates:
        points = tuple(points) #converting points into tuple
        if points[1] == 600:
            continue
        if yellow_filter_image[points[1],points[0]] == 0:
            continue
        cv.circle(three_channel_thresh_warped_copy, points, 10, (0,255,255), thickness = 2) #draw circle around these points

    # now lets calculate the radius of curvature of the yellow lane
    radius_curvature_yellow_lane = np.abs(float((1 + (2*polynomial_coeffs[0]*y_coordinates[20] + polynomial_coeffs[1])**2)**(3.0/2.0))/float(2*polynomial_coeffs[0]))


    #now lets calculate the radius of curvature of road
    #we just average out the radius of the both the lanes
    radius_curvature_road = round((radius_curvature_white_lane + radius_curvature_yellow_lane)/2.0, 2) #round upto two decimals

    #lets make the road to appear in red colour
    # fill the lane with the red color using fillpoly function
    yellow_lane_coordinates = np.flipud(yellow_lane_coordinates)
    road_fill_coordinates = np.concatenate((white_lane_coordinates, yellow_lane_coordinates))
    cv.fillPoly(blank_image, [road_fill_coordinates], color=[0,0,255])

    #now lets invert the homography onto the actual frame
    H_Matrix, mask = cv.findHomography(dst_points, src_points) #perform homography between the source and destination points
    inverse_warped_image = cv.warpPerspective(blank_image, H_Matrix, (my_image.shape[1], my_image.shape[0]))
    
    # Overlay the image with lanes detected on the frame
    lane_detected_image = cv.add(my_image, inverse_warped_image)

    #since we need to show multiple outputs in single frame in the final output, we need to resize our lane detected image
    lane_detected_image = cv.resize(lane_detected_image, (int(my_image.shape[1] * 0.7), int(my_image.shape[0] * 0.25) + int(my_image.shape[0] * 0.45)))

    #now we need to estimate the direction of turn based on the curvature, We use the polynomial of the highest degree for this
    if polynomial_coeffs[0] > 0:
        cv.putText(lane_detected_image,'Make Right Turn',(50,50),cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0,255) , 2)
    elif polynomial_coeffs[0] < 0:
        cv.putText(lane_detected_image,'Make Left Turn',(50,50),cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0,255) , 2)
    else:
        cv.putText(lane_detected_image,'Straight Ahead',(50,50),cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0,255) , 2)
    
    #now lets put all different types of images together to be shown in the final output
    #In the main wndow we have the image with lanes detected
    #now in smaller windows, we need to show the following
    #small window 1: Original Image frame
    #small window 2: Frame with the lines detected (original images thresholded (3channel) )
    #small window 3: Frame with image perspective warped
    #small window 4: Frame with image perspective warped and plotted curves and detected points

    #small window 1 and 2 put together
    window_a = np.concatenate((my_image, three_channel_thresh_original), axis = 1)
    #lets resize this into a small window
    window_a = cv.resize(window_a, (int(my_image.shape[1]*0.25), int(my_image.shape[0]*0.25)))

    #annotate the small windows with respective numbers
    cv.putText(window_a, '(1)', (30,30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0,0) , 2)
    cv.putText(window_a, '(2)', (180,30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0,0) , 2)

    #small window 2 and 3 put together
    window_b = np.concatenate((three_channel_thresh_warped, three_channel_thresh_warped_copy), axis = 1)
    #lets resize this into a small window
    window_b = cv.resize(window_b, (int(my_image.shape[1]*0.25),int(my_image.shape[0]*0.45)))

    #annotate the small windows with respective numbers
    cv.putText(window_b,'(3)', (30,30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0,0) , 2)
    cv.putText(window_b,'(4)', (180,30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0,0) , 2)

    #windows a and b put together
    window_c = np.concatenate((window_a, window_b), axis = 0)

    #Now put the final image (lane detected) and the other smaller windows together
    window_all_outputs = np.concatenate((lane_detected_image, window_c), axis = 1)

    #create a white patch under the video to show the annotations of different windows
    window_d = np.zeros([int(my_image.shape[0]*0.10), int(my_image.shape[1]*0.70) + int(my_image.shape[1]*0.25), 3], dtype = np.uint8)
    window_d.fill(255)

    #include the annotated text
    cv.putText(window_d,'(1): Original frame, (2): Frame with lines detected, (3): Warped frame, (4): Warped frame with Detected points and curve fitting', (10,25), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0) , 1)
    cv.putText(window_d,'Radius of curvature: '+ str(radius_curvature_road) + " meters", (10,55), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0) , 1)

    #put together all outputs and the annotated text into final window
    window_final = np.concatenate((window_all_outputs, window_d), axis = 0)
    video.write(window_final) #save the video frame by frame
    cv.imshow('Lane detected with turn suggestion', window_final)

    if cv.waitKey(20) & 0xFF == ord('d'):
        break
capture.release()
cv.destroyAllWindows() #destroy all windows because we don't need it anymore
