import cv2
import numpy as np
from classes import BatchDeColorize, BatchColorize
import matplotlib.pyplot as plt
from skimage import measure

def polygons_from_segmented_image(path):
    segmented_image = cv2.imread(path)

    pixels = segmented_image.reshape(-1, 3)

    unique_colors = np.unique(pixels, axis=0)
    num_colors = unique_colors.shape[0]
    
    black = np.where((unique_colors == np.array([0,0,0])).all(axis=1))[0]

    # if black.size > 0:
    #     num_colors -= 1
        
    h,w,_ = segmented_image.shape
    ditto = np.zeros(h*w)

    for i, px in enumerate(pixels):
        indx = np.where((unique_colors == px).all(axis=1))[0]
        ditto[i] = indx[0]
    ditto = ditto.reshape(h,w)

    final = np.zeros((h,w,num_colors))

    island_polygons = []
    color_class_map = {}
    count = 0
    for color in range(num_colors):
        final[:,:,color][ditto==color] = 1

        labeled_image, num_labels = measure.label(final[:,:,color], connectivity=2, return_num=True)
        
        for label in range(1, num_labels + 1):
            island_mask = np.where(labeled_image == label, 1, 0)
            contours, _ = cv2.findContours(island_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                island_polygons.append(contours[0][:,0,:])
                color_class_map[count] = unique_colors[color]
                count += 1

    return island_polygons, color_class_map