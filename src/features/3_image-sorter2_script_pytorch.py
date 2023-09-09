

"""
 One-click image sorting/labelling script. Copies or moves images from a folder into subfolders. 
 This script launches a GUI which displays one image after the other and lets the user give different labels
 from a list provided as input to the script. In contrast to original version, version 2 allows for 
 relabelling and keeping track of the labels.
 Provides also short-cuts - press "1" to put into "label 1", press "2" to put into "label 2" a.s.o.

 USAGE:
 run 'python sort_folder_vers2.py' or copy the script in a jupyter notebook and run then

 you need also to provide your specific input (source folder, labels and other) in the preamble
 original Author: Christian Baumgartner (c.baumgartner@imperial.ac.uk)
 changes, version 2: Nestor Arsenov (nestorarsenov_AT_gmail_DOT_com)
 Date: 24. Dec 2018
"""


# Define global variables, which are to be changed by user:

# In[5]:


##### added in version 2

# the folder in which the pictures that are to be sorted are stored
# don't forget to end it with the sign '/' !
input_folder = 'C:\\Users\\61498\\Documents\\Github\\JitsPredict\\data\\raw\\EBI.14.The.Absolutes.720p.WEB.DL.H264-SF63\\'


output_folder = 'C:\\Users\\61498\\Documents\\GitHub\\JitsPredict\\data\\interim\\Tagged'
# the different folders into which you want to sort the images, e.g. ['cars', 'bikes', 'cats', 'horses', 'shoes']
labels_0 = ['BJJ', 'No BJJ','Redundant']
labels_1 = ['P1: White','P1: Blue','P1: Black','P1: Other Gi','P1:No Gi Black', 'P1:No Gi Other']
labels_2 = ['P2: White','P2: Blue','P2: Black','P2: Other Gi','P2:No Gi Black', 'P2:No Gi Other']
labels_3 = ['P1 Box: 0', '1', '2','3','4','5','6','7','8','9','10','11','12']
labels_4 = ['P2 Box: 0', '1', '2','3','4','5','6','7','8','9','10','11','12']
labels_5 = ["Guard", "Side Control", "Mount", "Back Mount", "KOB", "Turtle", "Standing"]

labels = [labels_0, labels_1, labels_2, labels_3, labels_4,labels_5]

# provide either 'copy' or 'move', depending how you want to sort the images into the new folders
# - 'move' starts where you left off last time sorting, no 'go to #pic', works with number-buttons for labeling, no txt-file for tracking after closing GUI, saves memory
# - 'copy' starts always at beginning, has 'go to #pic', doesn't work with number-buttons, has a txt-for tracking the labels after closing the GUI
copy_or_move = 'copy'

# Only relevant if copy_or_move = 'copy', else ignored
# A file-path to a txt-file, that WILL be created by the script. The results of the sorting wil be stored there.
# Don't provide a filepath to an empty file, provide to a non-existing one!
# If you provide a path to file that already exists, than this file will be used for keeping track of the storing.
# This means: 1st time you run this script and such a file doesn't exist the file will be created and populated,
# 2nd time you run the same script, and you use the same df_path, the script will use the file to continue the sorting.
df_path = 'C:\\Users\\61498\\Documents\\Github\\JitsPredict\\data\\interim\\001_Labeller_sorting_file_df.txt'

# a selection of what file-types to be sorted, anything else will be excluded
file_extensions = ['.jpg', '.png']

# set resize to True to resize image keeping same aspect ratio
# set resize to False to display original image
resize = True

#####


# In[8]:



import pandas as pd
import os
import numpy as np
import cv2
import torch

import argparse
import tkinter as tk
import os
from shutil import copyfile, move
from PIL import ImageTk, Image

class ImageGui:
    """
    GUI for iFind1 image sorting. This draws the GUI and handles all the events.
    Useful, for sorting views into sub views or for removing outliers from the data.
    """

    def __init__(self, master, labels, paths):
        """
        Initialise GUI
        :param master: The parent window
        :param labels: A list of labels that are associated with the images
        :param paths: A list of file paths to images
        :return:
        """

        # So we can quit the window from within the functions
        self.master = master

        # Extract the frame so we can draw stuff on it
        frame = tk.Frame(master)

        # Initialise grid
        frame.grid()


        # Start at the first file name
        self.index = 0
        self.paths = paths
        self.labels = labels
        self.df_labels = pd.DataFrame(index = paths, columns=range(len(labels)))
        self.df_labels["Flag"]=np.nan
        self.list_label = list(range(len(labels)))
        #### added in version 2
        self.sorting_label = 'unsorted'
        ####

        # Number of labels and paths
        self.n_labels = len(labels)
        self.n_paths = len(paths)

        # Set empty image container
        self.image_raw = None
        self.image = None
        self.image_panel = tk.Label(frame)

        # set image container to first image
        self.set_image(paths[self.index])

        # New Make buttons
        self.buttons = []
        for label_type in labels:
            button_sub=[]
            for label in label_type:
                button_sub.append(
                    tk.Button(frame, text=label, width=10, height=2, fg='blue', command=lambda l=label: self.vote_csv(l)))

            self.buttons.append(button_sub)

        # Make buttons - Original
        #self.buttons = []
        #for label in labels:
        #    self.buttons.append(
        #            tk.Button(frame, text=label, width=10, height=2, fg='blue', command=lambda l=label: self.vote(l))
        #    )
            
        ### added in version 2
        button_tools = []
        button_tools.append(tk.Button(frame, text="prev im", width=10, height=1, fg="green", command=lambda l=label: self.show_prev_image()))
        button_tools.append(tk.Button(frame, text="next im", width=10, height=1, fg='green', command=lambda l=label: self.show_next_image()))
        self.buttons.append(button_tools)
        ###
        
        # Add progress label
        progress_string = "%d/%d"% (self.index+1, self.n_paths)
        self.progress_label = tk.Label(frame, text=progress_string, width=10)
        
        #Filename label
        filename_string =  self.paths[self.index]
        #filename_list = filename_string.split('\')
        self.filename_label=tk.Label(frame,text=filename_string[-20:],width = 10)
        
        # Place buttons in grid
        for ll, button in enumerate(self.buttons):
            print(ll)
            for ll2, button2 in enumerate(button):
                #if ll <= 4:
                    button2.grid(row=ll, column=ll2, sticky='we')
                    
                #else:
                #    button2.grid(row=0,column=ll, sticky='we')
                    
            #frame.grid_columnconfigure(ll, weight=1)

        # Place progress label in grid
        self.progress_label.grid(row=0, column=3, sticky='we') # +2, since progress_label is placed after
                                                                            # and the additional 2 buttons "next im", "prev im"
        self.filename_label.grid(row=0, column=4,sticky='we',)   
        #### added in version 2
        # Add sorting label
        # sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2]
        # self.sorting_label = tk.Label(frame, text=("in folder: %s" % (sorting_string)), width=15)
        
        # Place typing input in grid, in case the mode is 'copy'
        # if copy_or_move == 'copy':
        #     tk.Label(frame, text="go to #pic:").grid(row=1, column=0)

        #     self.return_ = tk.IntVar() # return_-> self.index
        #     self.return_entry = tk.Entry(frame, width=6, textvariable=self.return_)
        #     self.return_entry.grid(row=1, column=1, sticky='we')
        #     master.bind('<Return>', self.num_pic_type)
        ####
        
        # Place sorting label in grid
        #self.sorting_label.grid(row=7, column=self.n_labels+1, sticky='we') # +2, since progress_label is placed after
        #                                                                     # and the additional 2 buttons "next im", "prev im"
        # # Place the image in grid
        self.image_panel.grid(row=7, column=0, columnspan=self.n_labels+1, sticky='we')

        # key bindings (so number pad can be used as shortcut)
        # make it not work for 'copy', so there is no conflict between typing a picture to go to and choosing a label with a number-key
        #if copy_or_move == 'move':
        #    for key in range(self.n_labels):
        #        master.bind(str(key+1), self.vote_key)

    def show_next_image(self):
        """
        Displays the next image in the paths list and updates the progress display
        """
        self.index += 1
        # Checking to see if image has already been labelled
        while df.labelled [self.index] == 1:
                self.index+=1

        # Setting up progress string
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        #Filename label
        root, filename_string = os.path.split(df.sorted_in_folder[self.index])
        #filename_list = filename_string.split('\')
        self.filename_label.configure(text=filename_string[-20:])
        ####
        # root_orig, filename_orig = os.path.split(df.im_path[self.index])
        if self.index < self.n_paths:
            self.set_image(df.sorted_in_folder[self.index])
        else:
            self.master.quit()
    def show_prev_image(self):
        """
        Displays the next image in the paths list and updates the progress display
        """
        self.index += -1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        if self.index < self.n_paths:
            self.set_image(df.sorted_in_folder[self.index])
        else:
            self.master.quit()
    ### added in version 2        
    def move_prev_image(self):
        """
        Displays the prev image in the paths list AFTER BUTTON CLICK,
        doesn't update the progress display
        """
        self.index -= 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        
        #sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2] #shows the last folder in the filepath before the file
        #self.sorting_label.configure(text=("in folder: %s" % (sorting_string)))
        
        if self.index < self.n_paths:
            self.set_image(df.sorted_in_folder[self.index]) # change path to be out of df
        else:
            self.master.quit()
    
    ### added in version 2
    def move_next_image(self):
        """
        Displays the next image in the paths list AFTER BUTTON CLICK,
        doesn't update the progress display
        """
        self.index += 1
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        if self.index < self.n_paths:
            #print(df.sorted_in_folder[self.index])
            self.set_image(df.sorted_in_folder[self.index])
        else:
            self.master.quit()

    def set_image(self, path):
        """
        Helper function which sets a new image in the image view
        :param path: path to that image
        """
        image = self._load_image(path)
        self.image_raw = image
        self.image = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=self.image)

    def vote(self, label):
        """
        Processes a vote for a label: Initiates the file copying and shows the next image
        :param label: The label that the user voted for
        """
        ##### added in version 2
        # check if image has already been sorted (sorted_in_folder != 0)
        if df.sorted_in_folder[self.index] != df.im_path[self.index]:
            # if yes, use as input_path the current location of the image
            input_path = df.sorted_in_folder[self.index]
            root_ext, file_name = os.path.split(input_path)
            root, _ = os.path.split(root_ext)
        else:
            # if image hasn't been sorted use initial location of image
            input_path = df.im_path[self.index]
            root, file_name = os.path.split(input_path)
        #####
        
        #input_path = self.paths[self.index]
        if copy_or_move == 'copy':
            self._copy_image(label, self.index)
        if copy_or_move == 'move':
            self._move_image(label, self.index)
            
        self.show_next_image()

    def vote_csv(self,label):
        """
        Processes a vote for a label: Initiates the CSV file creation
        and shows next image if all image classes are labelled
        :param label: The label that the user voted for
        """
        # for i,j in enumerate(self.labels):
        #     self.df_labels[self.index].iloc[i] = label
        #     print(self.df_labels[self.index].iloc[i])
        for i,j in enumerate(labels):
            for k,l in enumerate(labels[i]):
                if l == label:
                    self.df_labels[i].iloc[self.index] = label
                    #print(label, self.index, i)
        
        self.df_labels['Flag'].iloc[self.index] = self.df_labels[self.list_label].iloc[self.index].isnull().sum()
        root, file_name = os.path.split(df.im_path[self.index])
       # Creating a list of the directories for the input folder, except for the last
        directory_names = input_folder.split('\\')[:-1]
        # The last subfolder will be the first part of new filename
        new_name = input_folder.split('\\')[-2]
        # Creating a list of directories for the file location
        flist = root.split('\\')
        # Creating a new filename which is a concat of subdirectories of input folder
        new_filename = new_name
        for folder in flist:
            if not folder in directory_names:
                new_filename = new_filename + folder
            else:
                pass
        output_path = os.path.join(output_folder, new_filename + file_name[:-4] +".csv")
        box_path = os.path.join(output_folder, new_filename + file_name[:-4] +"_label_info_y5.csv")

        if self.df_labels['Flag'].iloc[self.index] == 0:
            self.df_labels.iloc[self.index].to_csv(output_path, index=True)
            df.labelled[self.index] = 1
            self._copy_image(self.index)
            self.show_next_image()
        elif self.df_labels[0].iloc[self.index] == "No BJJ":
            self.df_labels.iloc[self.index].to_csv(output_path, index=True)
            df.labelled[self.index] = 1
            self._copy_image(self.index)
            self.show_next_image()
        elif self.df_labels[0].iloc[self.index] == "Redundant":
            os.remove(box_path)
            df.labelled[self.index] = 1
            #df.to_csv(df_path)
            self.show_next_image()
        
    def vote_key(self, event):
        """
        Processes voting via the number key bindings.
        :param event: The event contains information about which key was pressed
        """
        pressed_key = int(event.char)
        label = self.labels[pressed_key-1]
        self.vote(label)
    
    #### added in version 2
    def num_pic_type(self, event):
        """Function that allows for typing to what picture the user wants to go.
        Works only in mode 'copy'."""
        # -1 in line below, because we want images bo be counted from 1 on, not from 0
        self.index = self.return_.get() - 1
        
        progress_string = "%d/%d" % (self.index+1, self.n_paths)
        self.progress_label.configure(text=progress_string)
        sorting_string = os.path.split(df.sorted_in_folder[self.index])[-2]
        #shows the last folder in the filepath before the file
        self.sorting_label.configure(text=("in folder: %s" % (sorting_string)))
        
        self.set_image(df.sorted_in_folder[self.index])
    @staticmethod
    def _copy_filename(input_path, output_folder, suffix):
        root, file_name = os.path.split(input_path)
        # Creating a list of the directories for the input folder, except for the last
        directory_names = input_path.split('\\')[:-1]
        # The last subfolder will be the first part of new filename
        new_name = input_path.split('\\')[-2]
        # Creating a list of directories for the file location
        flist = root.split('\\')
        # Creating a new filename which is a concat of subdirectories of input folder
        new_filename = new_name
        for folder in flist:
            if not folder in directory_names:
                new_filename = new_filename + folder
            else:
                pass
        output_path = os.path.join(output_folder, new_filename + file_name[:-4] + suffix)
    @staticmethod
    def _load_image(path):
        """
        Loads and resizes an image from a given path using the Pillow library
        :param path: Path to image
        :return: Resized or original image 
        """
        #image = Image.open(path)
        image = cv2.imread(path)
        #print(path)
        results = model(image)
        #df = pd.read_csv(path[:-4] + '_label_info.csv', )
        df = results.pandas().xyxy[0]
        root, file_name = os.path.split(path)
        # Creating a list of the directories for the input folder, except for the last
        directory_names = input_folder.split('\\')[:-1]
        # The last subfolder will be the first part of new filename
        new_name = input_folder.split('\\')[-2]
        # Creating a list of directories for the file location
        flist = root.split('\\')
        # Creating a new filename which is a concat of subdirectories of input folder
        new_filename = new_name
        for folder in flist:
            if not folder in directory_names:
                new_filename = new_filename + folder
            else:
                pass
        new_filename = new_filename + file_name[:-4] + '_label_info_y5.csv'
        output_path = os.path.join(output_folder, new_filename)
        df.to_csv(output_path)
        for i in range(len(df)):
            # get coordinates
            y1, x1, y2, x2 = int(df['ymin'].iloc[i]), int(df['xmin'].iloc[i]), int(df['ymax'].iloc[i]), int(df['xmax'].iloc[i])
            # Blue color in BGR
            color = (255, 0, 0)
            # Line thickness of 2 px
            thickness = 2
            # Draw rectangle on image
            image = cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
            #print(x1, y1)
            #print(x2, y2)
            # Define text to write on image
            text = "P" + str(i) + " " + str(df['confidence'].iloc[i])[:4]
            # Define font
            font = cv2.FONT_HERSHEY_SIMPLEX
            # Put Text on image
            cv2.putText(image, text, (x1, y1), font, 1, color, 2, cv2.LINE_AA)
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)
        if(resize):
            max_height = 640
            img = im_pil 
            s = img.size
            ratio = max_height / s[1]
            im_pil = img.resize((int(s[0]*ratio), int(s[1]*ratio)), Image.ANTIALIAS)
        return im_pil

    #@staticmethod
    def _copy_image(label,ind):
        """
        Copies a file to a new label folder using the shutil library. The file will be copied into a
        subdirectory called label in the input folder.
        :param input_path: Path of the original image
        :param label: The label
        """
        root, file_name = os.path.split(df.im_path[ind])
        #print(df.im_path[ind])
        # Creating a list of the directories for the input folder, except for the last
        directory_names = input_folder.split('\\')[:-1]
        # The last subfolder will be the first part of new filename
        new_name = input_folder.split('\\')[-2]

        # Creating a list of directories for the file location
        flist = root.split('\\')

        # Creating a new filename which is a concat of subdirectories of input folder
        new_filename = new_name
        for folder in flist:
            if not folder in directory_names:
                new_filename = new_filename + folder
            else:
                pass
        new_filename = new_filename + file_name[:-4] + '.jpg'
        output_path = os.path.join(output_folder, new_filename)
        print("file_name =",new_filename)
        print(" %s --> %s" % (new_filename, 'Tagged'))
        copyfile(df.im_path[ind], output_path)
        
        # keep track that the image location has been changed by putting the new location-path in sorted_in_folder    
        df.loc[ind,'sorted_in_folder'] = output_path
        #####
        
        df.to_csv(df_path)

    @staticmethod
    def _move_image(label, ind):
        """
        Moves a file to a new label folder using the shutil library. The file will be moved into a
        subdirectory called label in the input folder. This is an alternative to _copy_image, which is not
        yet used, function would need to be replaced above.
        :param input_path: Path of the original image
        :param label: The label
        """
        root, file_name = os.path.split(df.sorted_in_folder[ind])
        # two lines below check if the filepath contains as an ending a folder with the name of one of the labels
        # if so, this folder is being cut out of the path
        # if os.path.split(root)[1] in labels:
        #     root = os.path.split(root)[0]
        output_path = os.path.join(root, 'Tagged', file_name)
        print("file_name =",file_name)
        print(" %s --> %s" % (file_name, 'Moved to Tagged'))
        move(df.sorted_in_folder[ind], output_path)
        input_label_file = df.sorted_in_folder[ind][:-4]+'_label_info_y5.csv'
        output_label_file = output_path[:-4]+'_label_info_y5.csv'
        move(input_label_file,output_label_file)
        # keep track that the image location has been changed by putting the new location-path in sorted_in_folder    
        df.loc[ind,'sorted_in_folder'] = output_path
        #####

class BoundBox:
	def __init__(self, xmin, ymin, xmax, ymax, objness = None, classes = None):
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.objness = objness
		self.classes = classes
		self.label = -1
		self.score = -1

	def get_label(self):
		if self.label == -1:
			self.label = np.argmax(self.classes)

		return self.label

	def get_score(self):
		if self.score == -1:
			self.score = self.classes[self.get_label()]

		return self.score
def call_boxes(filename1, filename2):
	# load the image
    data = pyplot.imread(filename1)
	# plot the image
    pyplot.imshow(data)
    headers =['Label', 'Score', 'xmin', 'ymin','xmax', 'ymax' ]
    df = pd.read_csv(filename2)
    
    # get the context for drawing boxes
    ax = pyplot.gca()
	# plot each box
    for i in range(len(v_boxes)):
        box = v_boxes[i]
		# get coordinates
        y1, x1, y2, x2 = box.ymin, box.xmin, box.ymax, box.xmax
		# calculate width and height of the box
        width, height = x2 - x1, y2 - y1
		# create the shape
        rect = Rectangle((x1, y1), width, height, fill=False, color='white')
		# draw the box
        ax.add_patch(rect)
		# draw text and score in top left corner
        label = "%s (%.3f)" % (v_labels[i], v_scores[i])
        pyplot.text(x1, y1, label, color='white')
	# show the plot
    ax.set_axis_off()
    #pyplot.show()
    # save the plot
    pyplot.savefig(filename[:-4]+"_predict.jpg",bbox_inches='tight', dpi=300)
# def make_folder(directory):
#     """
#     Make folder if it doesn't already exist
#     :param directory: The folder destination path
#     """
#     if not os.path.exists(directory):
#         os.makedirs(directory)

# The main bit of the script only gets exectured if it is directly called
if __name__ == "__main__":

###### Commenting out the initial input and puting input into preamble
#     # Make input arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-f', '--folder', help='Input folder where the *tif images should be', required=True)
#     parser.add_argument('-l', '--labels', nargs='+', help='Possible labels in the images', required=True)
#     args = parser.parse_args()

#     # grab input arguments from args structure
#     input_folder = args.folder
#     labels = args.labels
    
    # Make folder for the new labels
    # for label in labels:
    #make_folder(os.path.join(input_folder, 'Tagged')

    # Put all image file paths into a list
    paths = []
#     for file in os.listdir(input_folder):
#         if file.endswith(".tif") or file.endswith(".tiff"):

#             path = os.path.join(input_folder, file)
#             paths.append(path).

    ######## added in version 2
    #file_names = [fn for fn in sorted(os.listdir(input_folder))
    #              if any(fn.endswith(ext) for ext in file_extensions)]
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            for ext in file_extensions:
                if file.endswith(ext):
                    # append the file name to the list
                    paths.append(os.path.join(root, file))
    # Loading the YOLOv5 model for inference on images
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    
    if copy_or_move == 'copy':
        try:
            df = pd.read_csv(df_path, header=0)
            # Store configuration file values
        except FileNotFoundError:
            df = pd.DataFrame(columns=["im_path", 'sorted_in_folder','labelled'])
            df.im_path = paths
            df.sorted_in_folder = paths
            df.labelled = 0

    if copy_or_move == 'move':
        df = pd.DataFrame(columns=["im_path", 'sorted_in_folder','labelled'])
        df.im_path = paths
        df.sorted_in_folder = paths
    #######
    
# Start the GUI
root = tk.Tk()
app = ImageGui(root, labels, paths)
root.mainloop()

