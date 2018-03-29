from __future__ import print_function
import piexif
from os import getcwd,chdir
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import glob
import pysubs2

#Helper function to get valid input
def get_valid_input():
	valid_input=False
	while(valid_input!=True):
		try:
			variable=input()
			if(variable>0):
				valid_input=True
				return variable
		except:
			print("Only integers allowed")

#Main function
def main():

	main_dir=getcwd()
	print("Input the number of videos")
	num_vids=int(get_valid_input())
	#Iterations depending on the number of videos
	for i in range(num_vids):

		print ("Please select the folder of images for video %s"%((i+1)))

		image_dir = Tk()

		#Used to put the window in background (or hidden)
		image_dir.withdraw()
		image_dir.lift()

		#This is used to find the directory which contains the pictures
		image_dir_path = tkFileDialog.askdirectory()
		image_dir.destroy()

		#Move into image directory so that glob can work easily
		chdir(image_dir_path)

		#List for storing gps data
		all_gps_data=[]

		#Iterate for all the images
		for filename in glob.iglob('./*.JPG'):
			exif_data_output=exif_data(filename)
			all_gps_data.append(exif_data_output)
			#print(*all_gps_data, sep="\n")

		chdir(main_dir)

		print("Please select the srt file for the video")

		srt_file=Tk()
		srt_file.withdraw()
		srt_file.lift()
		srt_filename=tkFileDialog.askopenfilename(initialdir = image_dir_path, title = "Select the srt subtitle file",filetypes = (("SRT File","*.srt"),("all files","*.*")))
		srt_file.destroy()

		#Get the time and coordinate from srt file
		drone_pos_output=drone_pos(srt_filename)
		#print(drone_pos_output)

def exif_data(image_name):
	exif_dict = piexif.load(image_name)
	gps_data = exif_dict.pop("GPS")
	try:
		gps_data_dms=[]
		latitude=[gps_data[2][0],gps_data[2][1],gps_data[2][2]]
		longitude=[gps_data[4][0],gps_data[4][1],gps_data[4][2]]

		#Latitude follows
		gps_data_dms.append(float(latitude[0][0]))
		gps_data_dms.append(float(latitude[1][0]))
		gps_data_dms.append(float(latitude[2][0]))

		#Longitude follows
		gps_data_dms.append(float(longitude[0][0]))
		gps_data_dms.append(float(longitude[1][0]))
		gps_data_dms.append(float(longitude[2][0]))
		gps_data_dd=dms_to_dd(gps_data_dms)

	except:
		print("End of file :(")
		gps_data_dd=0

	if(gps_data_dd==0):
		return [] 

	return image_name,gps_data_dd[0],gps_data_dd[1]

#Converting dms format data to dd
def dms_to_dd(data): #this function converts gps co ordinates from dms to dd format

	gps_data_dd=[]
	gps_data_dd.append(float(data[0] + float(float(data[1] + data[2]/60)/60)))
	gps_data_dd.append(float(data[3] + float(float(data[4] + data[5]/60)/60)))
	return gps_data_dd[0],gps_data_dd[1]

#Using pysubs2 to get time and coordinates of the drone
def drone_pos(file):
	subs_file=pysubs2.load(file)
	drone_lat=[]
	drone_long=[]
	drone_time=[]

	for line in subs_file:
		#Convert milliseconds to seconds
		drone_time.append((int(line.start))/1000)
		
		#Comma seperated data
		text=(line.text).split(',')
		drone_lat.append(float(text[0]))
		drone_long.append(float(text[1]))

	drone_position=[drone_time,drone_lat,drone_long]

	return drone_position


main()