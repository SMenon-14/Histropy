from tabulate import tabulate
import PIL
import numpy as np
import math
from collections import defaultdict

class ImageCalculator:
    def __init__(self, file_path, bin_range):
        self.bin_range=bin_range
        self.filename = file_path.rsplit('/', 1)[-1]
        self.image = PIL.Image.open(file_path)
        self.mode = 8
        if(self.image.mode == "I;16"):
            image_transformed = self.image
            self.mode = 16
        else:
            image_transformed = self.__preprocessing()
        self.pixels = image_transformed.load()
        self.height, self.width = image_transformed.size
        self.__get_histogram_data(self.height, self.width, self.mode)
        self.y_limit = max(self.pixel_dict.values())

    # Method to convert image file into grayscale if the image is not already grayscale
    def __preprocessing(self):
        img = self.image
        if img.mode != 'L':
            img = PIL.ImageOps.grayscale(img)
        return img
    
    # Return the number of pixels on a given range
    def pixels_on_range(self, range_to_calculate):
        new_pix = {k: self.pixel_dict[k] for k in self.pixel_dict.keys() & list(range_to_calculate)}
        total_pixels = sum(new_pix.values())
        return new_pix, total_pixels
    
    #Create histogram dictionary from image pixel data for 16 bit
    def __bin_hist_data(self, bin_size):
        # Initialize a dictionary for the bins
        binned_dict = defaultdict(int)
        # Iterate through the original dictionary
        for key, value in self.pixel_dict.items():
            # Determine the bin for the current key
            bin_key = (key // bin_size) * bin_size
            # Add the value to the appropriate bin
            binned_dict[bin_key] += value

        # Convert the defaultdict to a regular dictionary
        self.display_dict = dict(binned_dict)

    #Create histogram dictionary from image pixel data for 8 bit
    def __get_histogram_data(self, h, w, mode):
        pixel_vals = {}
        sum = 0
        maximum = -1*pow(2, mode)
        minimum = pow(2, mode)
        pix = self.pixels
        for i in range(0, h):
            for j in range(0, w):
                value = round(pix[i, j])
                if(value > maximum):
                    maximum = value
                if(value < minimum):
                    minimum = value
                sum+= value
                if value in pixel_vals:
                    pixel_vals[value] = pixel_vals[value]+1
                else:
                    pixel_vals[value] = 1
        #Sort the dictionary by key value
        myKeys = list(pixel_vals.keys())
        myKeys.sort()
        sorted_pixel_vals = {i: pixel_vals[i] for i in myKeys}
        self.min = minimum
        self.max = maximum
        self.pixel_dict = sorted_pixel_vals
        self.display_dict = sorted_pixel_vals
        self.mean = sum/(h*w)
        if(mode==16):
            self.__bin_hist_data(self.bin_range)

    #Method to calculate intensity on a range
    def calculate_total_intensity(self, calculation_range=None):
        if calculation_range is None:
            calculation_range = (self.min, self.max+1)
        newpix, ct = self.pixels_on_range(calculation_range)
        if(ct==0):
            return 0
        intensity_total = sum(intensity*count for intensity,count in newpix.items())
        return intensity_total
        
    # Method to calculate mean on a range
    def calculate_mean(self, calculation_range=None):
        if calculation_range is None:
            return self.mean
        else:
            intensity_total = self.calculate_total_intensity(calculation_range)
            pix, ct = self.pixels_on_range(calculation_range)
            if(ct==0):
                return 0
            return intensity_total/ct
        
    # Method to calculate entropy values using the above equation by taking in the calculations of the find_pi method
    def calculate_entropy_value(self, calculation_range=None):
        sum=0
        if calculation_range is None:
            num_pixels = self.height*self.width
            pi_vals = self.pixel_dict
        else:
            pi_vals, num_pixels = self.pixels_on_range(calculation_range)
        for key in pi_vals.keys():
            value = pi_vals[key]/num_pixels
            if value != 0:
                sum+= (value*np.log2(value))
        if(sum == 0):
            return 0
        return sum*-1
    
    # Method to calculate the standard deviation of a range of pixels
    def __get_std_dev(self, calculation_range=None):
        mean = self.calculate_mean(calculation_range)
        num_pix = -1
        sum = 0
        for i in range(0, self.height):
            for j in range(0, self.width):
                if calculation_range == None or self.pixels[i, j] in calculation_range:
                    sum += pow(self.pixels[i, j]-mean, 2)
                    num_pix+=1
        return math.sqrt(sum/(num_pix))

    def get_maximum(self, calculation_range):
        if calculation_range is None:
            return self.max
        else:
            newpix, total = self.pixels_on_range(calculation_range)
            return max(newpix.keys())
        
    
    # Method to calculate the rms contrast of a range of pixels
    def get_rms_contrast(self, calculation_range=None):
        stddev = self.__get_std_dev(calculation_range)
        return stddev/255
    