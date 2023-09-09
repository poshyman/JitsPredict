# Importing all necessary libraries 
import cv2 
import os 

# Where all the videos you want to extract images are in
image_directory = 'E:\\Personal\\BJJ\\Events\\IBJJF Rio International Open 2021\\'
# Where you want to save all of the extracted images
save_directory = 'C:\\Users\\61498\\Documents\\Python\\data\\'
#The rate in which to save images from the video. 
#Example: If every 30th frame is desired, enter 30
frame_number = 30
#Removing directory names from save directory folder
#Enter number of digits to remove from the beginning of the filename string
directory_num = 16

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

def frameExtract(filename,rootsavefolder,directorynum,framenumber):
    #filename is the full directory path of the video file to be extracted
    #rootsavefolder is the directory where you want data to be saved
    #directorynum is the string slice of where you want to add sub-directories
    #to the root save folder
    #framenumber is the rate in which to save frames (e.g. 1  in 30)
    
    # Read the video from specified path 
    cam = cv2.VideoCapture(filename) 
    savefolder = rootsavefolder + filename[directorynum:-4] + "\\"
    try: 
      
        # creating a folder named data 
        if not os.path.exists(savefolder): 
            os.makedirs(savefolder) 
            print(savefolder)
  
# if not created then raise error 
    except OSError: 
        print ('Error: Creating directory of data') 
  
# frame 
    currentframe = 0
  
    while(True): 
      
    # reading from frame 
        ret,frame = cam.read() 
  
        if ret: 
            if currentframe % framenumber ==0:
                # if video is still left continue creating images 
                name = savefolder + str(currentframe) + '.jpg'
                print ('Creating...' + name) 
  
                # writing the extracted images 
                cv2.imwrite(name, frame) 
                # increasing counter so that it will 
                # show how many frames are created 
                currentframe += 1
            else:
                currentframe += 1
        else: 
            break
  
    # Release all space and windows once done 
    cam.release() 
    cv2.destroyAllWindows() 


filenames = getListOfFiles(image_directory)

for file in filenames:
    frameExtract(file, save_directory,directory_num, frame_number)