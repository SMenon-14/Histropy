from tabulate import tabulate
import numpy as np
import easygui
import PIL
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RadioButtons
from matplotlib.axes import Axes
from matplotlib.widgets import TextBox
from matplotlib.backend_bases import MouseButton
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from ImageCalculator import ImageCalculator
from matplotlib.widgets import Button
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
import matplotlib.image as image
from matplotlib.backend_tools import ToolBase, ToolToggleBase

class InterHist:
    def __init__(self, file_path):
        self.fpath = file_path
        self.image_calculator = ImageCalculator(file_path)
        #self.im = image.imread(file_path)
        #Creating subplot mosaic
        self.fig, self.ax = plt.subplot_mosaic(
            [
                ['main', 'scale', 'image1'],
                ['main', 'bounds', 'image2'],
                ['main', 'display', 'image3'],
                ['main', 'overlays', 'image4']
            ],
            width_ratios=[4, 1.25, 0.75],
            layout='constrained',
        )
        #imagebox = OffsetImage(self.im, zoom = 0.15)
        #a = int(self.image_calculator.max)
        #b = int(self.image_calculator.y_limit)-200
        #self.displayed_image = ab = AnnotationBbox(imagebox, (a, b), frameon = False)
        #self.ax['main'].add_artist(ab)
        self.__color_list = [(0.18, 0.451, 0.569), (0.569, 0.18, 0.275), (0.239, 0.569, 0.18), (0.769, 0.455, 0.102), (0.569, 0.361, 0.671), (0.761, 0.039, 0.039), (0.761, 0.627, 0.039), (0.027, 0.071, 0.329), (0.51, 0.729, 0.137), (0.91, 0.059, 0.835)]
        self.num_plots = 0
        self.extract_labels()
        self.create_main_hist()
        self.create_image_subplot()
        self.create_scale_subplot()
        self.create_range_subplot()
        self.create_calculation_subplot()
        self.create_overlay_subplot()
        self.submit_lower(self.left_bound)
        plt.ion()
        plt.show(block=True)

    def extract_labels(self):
        #Extracting Labels from Metadata
        self.left_bound = self.image_calculator.min
        self.right_bound = self.image_calculator.max
        self.last_clicked = self.right_bound
        self.intensity_sum = self.image_calculator.calculate_total_intensity(calculation_range=(0, 256))
        print(self.intensity_sum)
        self.size = self.image_calculator.height*self.image_calculator.width
        self.peak = self.image_calculator.y_limit
        self.radio_background = 'lightgoldenrodyellow'
    
    def create_image_subplot(self):
        self.ax['image1'].set_title('Image 1', fontdict={'fontsize': mpl.rcParams['axes.titlesize'], 'fontweight': mpl.rcParams['axes.titleweight'], 'color': 'tab:blue', 'verticalalignment': 'baseline', 'horizontalalignment': 'center'})
        self.ax['image1'].set_xticks([])
        self.ax['image1'].set_yticks([])
        img_arr = cv2.imread(self.fpath)
        self.ax['image1'].imshow(img_arr)
        image_ax_list = ['image2', 'image3', 'image4', "Image 2", "Image 3", "Image 4"]
        for i in range(0, 3):
            self.ax[image_ax_list[i]].set_title(image_ax_list[i+3])
            self.ax[image_ax_list[i]].set_xticks([])
            self.ax[image_ax_list[i]].set_yticks([])
            self.ax[image_ax_list[i]].set_visible(False)
        self.image_axs = image_ax_list
    
    def create_main_hist(self):
        #Creating Main Histogram
        data = self.image_calculator.pixel_dict
        color = (self.__color_list[0][0], # redness
         self.__color_list[0][1], # greenness
         self.__color_list[0][2], # blueness
         1 # transparency
         )
        l = self.ax['main'].bar(list(data.keys()), data.values(), color=color, width=1.1, label='main')
        self.ax['main'].set_xlim(-10, 255+10)
        xpos=np.arange(275)

        #Setting Plot Y-Axis Scale
        self.ax['main'].set_yscale('linear')

        #Making Plot Labels
        self.ax['main'].set_xlabel('Pixel Intensity Values')
        self.ax['main'].set_ylabel('Number of Pixels')
        self.ax['main'].set_title(self.image_calculator.filename)

    def create_scale_subplot(self):
        #Making scale switch buttons
        self.ax['scale'].set_facecolor(self.radio_background)
        self.ax['scale'].set_title('Scale')
        self.radio = RadioButtons(self.ax['scale'], ('linear', 'log base 10'))
        inset_axes_1 = inset_axes(self.ax['scale'], width="30%", height="15%", loc='lower right')
        self.text3 = TextBox(inset_axes_1, 'Y-Axis Limit', initial=self.image_calculator.y_limit, label_pad=0.09)
        self.text3.on_submit(self.submit_ylim)
        self.radio.on_clicked(self.reset_scale)

    def create_range_subplot(self):
        #Making Text Fields for Entering Bounds
        self.ax['bounds'].set_facecolor(self.radio_background)
        self.ax['bounds'].set_title('Intensity Range')
        self.ax['bounds'].set_xticks([])
        self.ax['bounds'].set_yticks([])
        #Creating individual fields
        inset_axes_1 = inset_axes(self.ax['bounds'], width="40%", height="25%", loc='center right')
        self.text1 = TextBox(inset_axes_1, 'Upper Bound', initial=self.right_bound, label_pad=0.09)
        inset_axes_2 = inset_axes(self.ax['bounds'], width="40%", height="25%", loc='upper right')
        self.text2 = TextBox(inset_axes_2, 'Lower Bound', initial=self.left_bound, label_pad=0.09)
        plt.connect('button_press_event', self.on_click)
        self.text2.on_submit(self.submit_lower)
        self.text1.on_submit(self.submit_higher)

    def create_calculation_subplot(self):
        #Making Text Display to show calculations
        self.ax['display'].set_facecolor(self.radio_background)
        self.ax['display'].set_title('Calculations on Intensity Range')
        self.ax['display'].set_xticks([])
        self.ax['display'].set_yticks([])
        #Making individual text displays
        self.t1 = self.ax['display'].text(0.055, .84, f'# pixels on range: {self.size}')
        self.t2 = self.ax['display'].text(0.055, .69, f'% of all pixels on range: {100}')
        self.t3 = self.ax['display'].text(0.055, .54, f'Entropy on range: {round(self.image_calculator.calculate_entropy_value(), 3)}')
        self.t4 = self.ax['display'].text(0.055, .39, f'Mean on range: {round(self.image_calculator.calculate_mean(), 3)}')
        self.t5 = self.ax['display'].text(0.055, .24, f'RMS contrast on range: {round(self.image_calculator.get_rms_contrast(), 3)}')
        self.t6 = self.ax['display'].text(0.055, .09, f'Total intensity on range: {self.intensity_sum}')
   
    def create_overlay_subplot(self):
        self.ax['overlays'].set_facecolor(self.radio_background)
        self.ax['overlays'].set_title('Histogram Overlays')
        self.ax['overlays'].set_xticks([])
        self.ax['overlays'].set_yticks([])
        add_image_axes = inset_axes(self.ax['overlays'], width="30%", height="15%", loc='upper left')
        self.baddimage = Button(add_image_axes, 'Add Image')
        self.baddimage.on_clicked(self.add_image)
        clear_overlays_axes = inset_axes(self.ax['overlays'], width="40%", height="15%", loc='upper right')
        self.bclearoverlays = Button(clear_overlays_axes, 'Clear Overlays')
        self.bclearoverlays.on_clicked(self.clear_images)
    
    def reset_scale(self, scl):
        if(scl=='log base 10'):
            scl = 'log'
        self.ax['main'].set_yscale(scl)
        plt.draw()

    def submit_lower(self, text):
        self.left_bound = int(text)
        calc_range = range(self.left_bound, self.right_bound+1)
        dict, ans = self.image_calculator.pixels_on_range(calc_range)
        self.t1.set_text(str(f'# pixels on range: {ans}'))
        self.t2.set_text(str(f'% of all pixels on range: {round(100*ans/self.size, 7)}'))
        self.t3.set_text(str(f'Entropy on range: {round(self.image_calculator.calculate_entropy_value(calc_range), 7)}'))
        self.t4.set_text(str(f'Mean on range: {round(self.image_calculator.calculate_mean(calc_range), 7)}'))
        self.t5.set_text(str(f'RMS contrast on range: {round(self.image_calculator.get_rms_contrast(calc_range), 7)}'))
        self.t6.set_text(str(f'Total intensity on range: {self.image_calculator.calculate_total_intensity(calc_range)}'))
        if self.num_plots > 0:
            self.update_plot_2(calc_range)
        plt.draw()

    def submit_higher(self, text):
        self.right_bound = int(text)
        calc_range = range(self.left_bound, self.right_bound+1)
        dict, ans = self.image_calculator.pixels_on_range(calc_range)
        self.t1.set_text(str(f'# pixels on range: {ans}'))
        self.t2.set_text(str(f'% of all pixels on range: {round(100*ans/self.size, 7)}'))
        self.t3.set_text(str(f'Entropy on range: {round(self.image_calculator.calculate_entropy_value(calc_range), 7)}'))
        self.t4.set_text(str(f'Mean on range: {round(self.image_calculator.calculate_mean(calc_range), 7)}'))
        self.t5.set_text(str(f'RMS contrast on range: {round(self.image_calculator.get_rms_contrast(calc_range), 7)}'))
        self.t6.set_text(str(f'Total intensity on range: {self.image_calculator.calculate_total_intensity(calc_range)}'))
        if self.num_plots > 0:
            self.update_plot_2(calc_range)
        plt.draw()

    def submit_ylim(self, text):
        if(text==''):
            self.ax['main'].autoscale()
            self.text3.set_val(self.image_calculator.y_limit)
        else:
            self.ax['main'].set_ylim(0, int(text))

    def on_click(self, event):
        if event.inaxes is self.ax['main']:
            x = event.xdata
            idx = int(x.round())
            if(idx > self.last_clicked):
                self.text1.set_val(idx)
                self.submit_higher(str(idx))
            else:
                self.text2.set_val(idx)
                self.submit_lower(str(idx))
            self.last_clicked = idx


    
    def add_image(self, event):
        self.num_plots+=1
        path = easygui.fileopenbox()
        filename = path.rsplit('/', 1)[-1]
        im = ImageCalculator(path)
        data = im.pixel_dict
        color = (self.__color_list[self.num_plots][0], # redness
         self.__color_list[self.num_plots][1], # greenness
         self.__color_list[self.num_plots][2], # blueness
         0.6 # transparency
         )
        color2 = (self.__color_list[self.num_plots][0], # redness
         self.__color_list[self.num_plots][1], # greenness
         self.__color_list[self.num_plots][2], # blueness
         1 # transparency
         )
        self.ax['main'].bar(list(data.keys()), data.values(), color=color, width=1.1)
        if(self.num_plots==1):
            self.calculator2 = ImageCalculator(path)
            newt = self.ax['overlays'].text(0.055, 0.72, filename[:34], color=color2)
            self.plots = [newt]
            self.nump2 = self.ax['overlays'].text(0.055, 0.6, "A", color=color2)
            self.percentp2 = self.ax['overlays'].text(0.055, 0.5, "B", color=color2)
            self.ep2 = self.ax['overlays'].text(0.055, 0.4, "C", color=color2)
            self.meap2 = self.ax['overlays'].text(0.055, 0.3, "D", color=color2)
            self.conp2 = self.ax['overlays'].text(0.055, 0.2, "E", color=color2)
            self.inp2 = self.ax['overlays'].text(0.055, 0.1, "F", color=color2)
            calc_range = range(self.left_bound, self.right_bound+1)
            self.update_plot_2(calc_range)
            plt.draw()
        else:
            self.nump2.set_visible(False)
            self.percentp2.set_visible(False)
            self.ep2.set_visible(False)
            self.meap2.set_visible(False)
            self.conp2.set_visible(False)
            self.inp2.set_visible(False)
            newt = self.ax['overlays'].text(0.055, 0.72-(self.num_plots-1)*.12, filename[:34], color=color2)
            self.plots.append(newt)
        for i in range(0, 3):
            if not self.ax[self.image_axs[i]].get_visible():
                self.ax[self.image_axs[i]].set_visible(True)
                self.ax[self.image_axs[i]].set_title(self.image_axs[i+3], fontdict={'fontsize': mpl.rcParams['axes.titlesize'], 'fontweight': mpl.rcParams['axes.titleweight'], 'color': color2, 'verticalalignment': 'baseline', 'horizontalalignment': 'center'})
                self.ax[self.image_axs[i]].set_xticks([])
                self.ax[self.image_axs[i]].set_yticks([])
                img_arr = cv2.imread(path)
                self.ax[self.image_axs[i]].imshow(img_arr)
                plt.draw()
                break


    def clear_images(self, event):
        self.num_plots = 0
        self.ax['main'].cla()
        for txt in self.plots:
            txt.set_visible(False)
        self.create_main_hist()
        for i in range(0, 3):
            self.ax[self.image_axs[i]].set_visible(False)

    def update_plot_2(self, calc_range):
        dict, ans = self.calculator2.pixels_on_range(calc_range)
        self.nump2.set_text(str(f'# pixels on range: {ans}'))
        self.percentp2.set_text(str(f'% of all pixels on range: {round(100*ans/self.size, 7)}'))
        self.ep2.set_text(str(f'Entropy on range: {round(self.calculator2.calculate_entropy_value(calc_range), 7)}'))
        self.meap2.set_text(str(f'Mean on range: {round(self.calculator2.calculate_mean(calc_range), 7)}'))
        self.conp2.set_text(str(f'RMS contrast on range: {round(self.calculator2.get_rms_contrast(calc_range), 7)}'))
        self.inp2.set_text(str(f'Total intensity on range: {self.calculator2.calculate_total_intensity(calc_range)}'))