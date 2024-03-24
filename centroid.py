"""
Script to identify the centre of mass of an areal boundary projected
into a 2 dimensional plane.  Applications include identifying the 
centre point of a city or river catchment.

@author: robert-edwin-rouse
"""

import cv2 as cv
import matplotlib.pyplot as plt


class Centroid():
    def __init__(self, imfile):
        '''
        2D representation of a geographical area from a rasterised image,
        calculating its centroid in terms of the image's size dimensions.
        
        Parameters
        ----------
        imfile : String
            Filepath to raster image representing the geographical
            area of concern.
        '''
        super().__init__()
        self.imfile = imfile
        self.image = cv.imread(imfile, cv.IMREAD_GRAYSCALE)
        self.bounds = self.image.shape
        self.cache = cv.bitwise_not(self.image)
        self.ret, self.thresh = cv.threshold(self.cache,127,255,0)
        self.contours, self.hierarchy = cv.findContours(self.thresh, 1, 2)
        self.cnt = self.contours[0]
        self.area = cv.contourArea(self.cnt)
        self.M = cv.moments(self.cnt)
        self.cx = int(self.M['m10']/self.M['m00'])
        self.cy = int(self.M['m01']/self.M['m00'])
        self.cy = self.bounds[1] - self.cy
        
    def lat_lon(self, lon_min, lon_max, lat_min, lat_max):
        '''
        Function to calculate the centroid of a geographical area in
        longitude and latitude coordinates based on that calculated from
        the image raster.
        
        Parameters
        ----------
        lon_min : Float
            Image longitude minimum value.
        lon_max : Float
            Image longitude maximum value.
        lat_min : Float
            Image latitude minimum value.
        lat_max : Float
            Image latitude maximum value.

        Returns
        -------
        lon : Float
            Longitudinal centre of mass coordinate.
        lat : Float
            Latitudinal centre of mass coordinate.
        '''
        rel_x = self.cx/self.bounds[0]
        rel_y = self.cy/self.bounds[1]
        lon = (lon_max-lon_min)*rel_x + lon_min
        lat = (lat_max-lat_min)*rel_y + lat_min
        return lon, lat

    def plot(self, outlinefile):
        '''
        Function to return a plot of the boundary of the geographical area
        with that area's centroid included as point coordinates.
        
        Parameters
        ----------
        outlinefile : String
            Filepath to raster image representing the boundary of the
            geographical area of concern.

        Returns
        -------
        A plot of the boundary with centroid coordinates.
        '''
        boundary = cv.imread(outlinefile)
        n = 5
        xs = [self.bounds[0]/(n-1)*x for x in range(n)]
        ys = [self.bounds[1]/(n-1)*x for x in range(n)]
        yr = ys[::-1]
        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax1.imshow(boundary, alpha = 0.8)
        ax1.scatter(self.cx, self.bounds[1]-self.cy, c='darkseagreen',
                    marker='*', s=250, linewidths=2.5, label='Centroid')
        ax1.text(self.cx -80, self.cy +150,
                 '('+str(self.cx)+', '+str(self.cy)+')')
        ax1.set_xlim(0, self.bounds[0])
        ax1.set_xlabel('x Pixel')
        ax1.set_xticks(xs, labels=xs)
        ax1.set_ylim(self.bounds[1], 0)
        ax1.set_ylabel('y Pixel')
        ax1.set_yticks(ys, labels=yr)
        ax1.grid(c='black', ls='dotted', lw=0.5)
        lines, labels = ax1.get_legend_handles_labels()
        ax1.legend(lines, labels, ncol=2, loc='upper right')
        plt.show()