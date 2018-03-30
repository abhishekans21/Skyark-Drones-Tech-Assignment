from __future__ import print_function
import piexif
from os import getcwd,chdir
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import glob
import pysubs2
from math import sin, cos, sqrt, asin, radians


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
		for filename in glob.iglob('*.JPG'):
			exif_data_output=exif_data(filename)
			all_gps_data.append(exif_data_output)
			#print(*all_gps_data, sep="\n")

		chdir(main_dir)

		print("Input the range in metres for which you want the nearby images")
		dist_vid=int(get_valid_input())

		print("Please select the srt file for the video")

		srt_file=Tk()
		srt_file.withdraw()
		srt_file.lift()
		srt_filename=tkFileDialog.askopenfilename(initialdir = image_dir_path, title = "Select the srt subtitle file",filetypes = (("SRT File","*.srt"),("all files","*.*")))
		srt_file.destroy()

		#Get the time and coordinate from srt file
		drone_pos_output=drone_pos(srt_filename)
		#print(drone_pos_output)

		#Get image data for all images which are within range for each second
		csv_data_all=distance_compare(drone_pos_output,all_gps_data,dist_vid)

def exif_data(image_name):
	gps_data_dms=[]
	
	try:
		exif_dict = piexif.load(image_name)
		for ifd in ("0th", "Exif", "GPS", "1st"):
			for tag in exif_dict[ifd]:
				if piexif.TAGS[ifd][tag]["name"]=="GPSLatitude":
					gps_data_dms.append(float((exif_dict[ifd][tag][0][0]*1.0)/exif_dict[ifd][tag][0][1]))
					gps_data_dms.append(float((exif_dict[ifd][tag][1][0]*1.0)/exif_dict[ifd][tag][1][1]))
					gps_data_dms.append(float((exif_dict[ifd][tag][2][0]*1.0)/exif_dict[ifd][tag][2][1]))
				elif piexif.TAGS[ifd][tag]["name"]=="GPSLongitude":
					gps_data_dms.append(float((exif_dict[ifd][tag][0][0]*1.0)/exif_dict[ifd][tag][0][1]))
					gps_data_dms.append(float((exif_dict[ifd][tag][1][0]*1.0)/exif_dict[ifd][tag][1][1]))
					gps_data_dms.append(float((exif_dict[ifd][tag][2][0]*1.0)/exif_dict[ifd][tag][2][1]))

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
	gps_data_dd.append(float(data[0] + data[1]/60.0 + data[2]/3600.0))
	gps_data_dd.append(float(data[3] + data[4]/60.0 + data[5]/3600.0))
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
		#print(text)
		drone_lat.append(float(text[1]))
		drone_long.append(float(text[0]))

	drone_position=[drone_time,drone_lat,drone_long]
	return drone_position
#This runs two lists against each other, getting all locations in the second within range of each location of the first.
def distance_compare(l1,l2,distance):
	location_list=[]
	image_list=[]

	for i in range(len(l1[0])):
		location_data_holder=[l1[1][i],l1[2][i]]
		image_holder=inside_range(location_data_holder,l2,distance)

		location_list.append(l1[0][i])
		image_list.append(str(image_holder))
	final_data=[location_list,image_list]

	return final_data


#Returns the images which are nearby the input distance
def inside_range(main_gps,gps,distance_to_check):

	inside_range=[]
	for i in range((len(gps[0][0]))):
		gps_distance_output=(get_gps_distance(main_gps[0],main_gps[1],gps[i][1],gps[i][2])*1000)

		if(gps_distance_output<distance_to_check):
			#print(gps_distance_output)
			inside_range.append(str(gps[i][0]))

	return inside_range

#Calculating distance between two points using Haversine formula
def get_gps_distance(lat1,long1,lat2,long2):

	radius_earth=6372.8
	lat_1=float(radians(lat1))
	lat_2=float(radians(lat2))
	diff_lat=float(radians(lat2-lat1))
	diff_long=float(radians(long2-long1))
	gps_distance=2*radius_earth*float(asin(sqrt(float(sin(diff_lat/2)**2 + cos(lat_1) * cos(lat_2) * sin(diff_long/2)**2))))
	#print(gps_distance)
	return gps_distance

main()