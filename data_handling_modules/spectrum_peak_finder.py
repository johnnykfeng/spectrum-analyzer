import numpy as np


class PeakFinder:

    @staticmethod
    def crop_roi(array, crop_center, crop_halfwidth=40):
        bin_range = [crop_center - crop_halfwidth, crop_center + crop_halfwidth]
        cropped_array = array[bin_range[0]:bin_range[1]]
        return cropped_array

    @staticmethod
    def find_peak_bin(array, crop_center, crop_halfwidth=40):
        cropped_array = PeakFinder.crop_roi(array, crop_center, crop_halfwidth)
        bin_max = np.argmax(cropped_array) + crop_center - crop_halfwidth
        return bin_max

    @staticmethod
    def find_peak_height(array, crop_center, crop_halfwidth=40):
        cropped_array = PeakFinder.crop_roi(array, crop_center, crop_halfwidth)
        peak_height = np.max(cropped_array)
        return peak_height