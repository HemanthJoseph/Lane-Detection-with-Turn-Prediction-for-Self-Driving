import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

def func_calculate_histogram(rows, cols, gray):
    for i in range(rows):
        for j in range(cols):
            value = gray[i][j] #iterating through each pixel and finding out its value
            h[value] += 1 #adding it to the histogram tally

def func_equalization(rows, cols, gray, rounded_equalized):
    for i in range(rows):
        for j in range(cols):
            value = gray[i][j] #finding out the value at that pixel
            gray[i][j] = rounded_equalized[value] #assigning it a new value from the equalized list

def func_histogram_equalization(rows, cols, gray, h, no_pixels):
    func_calculate_histogram(rows, cols, gray)
    PDF = h/no_pixels #performing probability distribution
    CDF = np.cumsum(PDF) #calculating cumulative frequencies
    Equalized = CDF * 255 #equalizing
    rounded_equalized = np.round(Equalized) #rounding
    func_equalization(rows, cols, gray, rounded_equalized)
    return gray

for i in range(25):
    img = cv.imread('inputs/' + str(i) + '.png') #reading the image and storing it in a variable
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    rows = img.shape[0]
    cols = img.shape[1]
    no_pixels = rows*cols

    h = np.zeros((256,), dtype=int) #histogram variable to store values

    after_equalization = func_histogram_equalization(rows, cols, gray, h, no_pixels)

    cv.imshow('Post Image', after_equalization) #showing that image in a new window
    cv.waitKey(0) #waiting for a key to be pressed
cv.destroyAllWindows() #destroy all windows because we don't need it anymore

# plt.plot(h)
# plt.plot(CDF)
# plt.plot(rounded_equalized)


