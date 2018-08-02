import requests
import json
import timeit
from service import roomF, featF, waterF
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='.')

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/displayResults/', methods=['POST'])
def getId():
	propertyId = request.form ['idfield']
	message = ''
	if request.method == 'POST':
		if len(request.form.get('idfield')) <= 0:
			message = "This field may not be empty"
			return render_template('index.html', message=message)
		else:
			payload = {
			  'grant_type':'client_credentials',
			  'client_id':'419BA8A7-D770-4EB9-9248-01559A95C9F5',
			  'client_secret':'4F3D60AB-CF9A-4504-8DE6-512AF442F314'
			}

			# *******Grabbing new api_token********
			apiUrlBaseToken = "https://api.goiconnect.com/api/OAuth/GetToken"
			headersToken = {'Content-Type': 'application/x-www-form-urlencoded'}
			responseToken = requests.post(apiUrlBaseToken, headers=headersToken, data=payload)
			jsonResponseToken = responseToken.json()
			jsonApiToken = jsonResponseToken ["access_token"]

			# Sending GET Request to iList API
			apiUrlBase = "https://api.goiconnect.com/odata/Listings?$filter=MLSID eq '{0}'".format(propertyId)
			headers = {'Content-Type': 'application/json', 
			           'Authorization': 'Bearer {0}'.format(jsonApiToken),
			           'Accept-Language': 'ENU'}

			totalStartTime = timeit.default_timer()
			gtStartTime = timeit.default_timer()

			response = requests.get(apiUrlBase, headers=headers)
			jsonResponse = response.json()

			if not jsonResponse ["value"]:
				message = "MLS-ID not found, please enter a valid MLS-ID"
				return render_template('index.html', message=message)

			gtEndTime = timeit.default_timer()
			gtRunTime = "{0:.3f}".format(gtEndTime - gtStartTime)
	return display(propertyId, jsonResponse, totalStartTime, gtRunTime)

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@app.route('/display/', methods=['POST'])
def display(propertyId, jsonResponse, totalStartTime, gtRunTime):
	# Values from iList API

	region = jsonResponse["value"][0]["Region"]["RegionName"]
	propertyType = jsonResponse["value"][0]["PropertyType"]

	# Variables for address
	countryName = jsonResponse["value"][0]["Address"]["GeoData"]["Country"]
	regionName = jsonResponse["value"][0]["Address"]["GeoData"]["Region"]
	provinceName = jsonResponse["value"][0]["Address"]["GeoData"]["Province"]
	cityName = jsonResponse["value"][0]["Address"]["GeoData"]["City"]
	localZoneName = jsonResponse["value"][0]["Address"]["GeoData"]["LocalZone"]

	# Tested address, displays correctly (have not checked for a property with local zone)
	if (localZoneName): # Address with Local Zone if available
		address = "{}, {}, {}, {}, {}".format(localZoneName, cityName, provinceName, regionName, countryName)
	else: # Address without Local Zone if null
		address = "{}, {}, {}, {}".format(cityName, provinceName, regionName, countryName)

	description = jsonResponse["value"][0]["ListingDescription"]
	description = remove_html_tags (description)

	featuresList = []

	# Loops through all features in features list, verified that this is working
	for feat in jsonResponse["value"][0]["Features"]:
	# Only appends features that are non-null to features list
		if(feat["FeatureName"]):
			featuresList.append(feat["FeatureName"])

	numberOfFeatures = len(featuresList)
	roomTypeList = []

	# Loops through all room types in list, verified that this is working
	for room in jsonResponse["value"][0]["Rooms"]:
	# Only appends room types that are non-null to features list
		if(room["Type"]):
			roomTypeList.append(room["Type"])

	numberOfRoomTypes = len(roomTypeList)

	# Gathering all ImageURLs
	imageUrlList = []
	imageRoomTypeList = []

	for image in jsonResponse["value"][0]["Images"]:
		imageUrlList.append (image["WebImageURL"])
		imageRoomTypeList.append (image["RoomType"])

	numberOfImages = len(imageUrlList)	

	# Initializing all RestB lists to be populated after API Scripts are executed
	# Lists containing all unique features and room types from RestB Scripts
	featuresFull = []
	roomTypeFull = []

	# Lists containing all features and room types from RestB Scripts (including duplicates)
	fList = []
	rList = []
	wMarkList = []

	startTime = timeit.default_timer()

	roomF(imageUrlList, rList)
	featF(imageUrlList, fList)
	waterF(imageUrlList, wMarkList)

	stopTime = timeit.default_timer()
	runTime = "{0:.3f}".format(stopTime - startTime)

	# Stores all non-duplicate Room Types into a list
	for room in rList:
		if room not in roomTypeFull and room != 'non_related':
			roomTypeFull.append(room)

	# Stores all non-duplicate features into a list
	for feat in fList:
		if isinstance(feat, list):
			for item in feat:
				if item not in featuresFull:
					featuresFull.append(item)

	numOfRoom = len (roomTypeFull)
	room_ai = numOfRoom
	if (numOfRoom < numberOfRoomTypes):
		numOfRoom = numberOfRoomTypes

	numOfFeat = len (featuresFull)
	feat_gt = len(featuresList)
	feat_ai = numOfFeat
	if (numOfFeat < feat_gt):
		numOfFeat = feat_gt

	totalEndTime = timeit.default_timer()
	totalRunTime = "{0:.3f}".format(totalEndTime - totalStartTime)

	return render_template('display.html', listingid=propertyId, regionid=region, address=address,
		description=description, imageCount=numberOfImages, images=imageUrlList, fullRoom=rList, 
		fullFeat=fList, fullWatermark=wMarkList, allFeat=featuresFull, allRoom=roomTypeFull, 
		gtRoomTypes=roomTypeList, gtFeatures=featuresList, numOfRoom=numOfRoom, numOfFeat=numOfFeat,
		runTime = runTime, totalRunTime=totalRunTime, gtRunTime=gtRunTime, room_gt= numberOfRoomTypes, room_ai=room_ai,
		feat_gt=feat_gt, feat_ai= feat_ai)
	# Exports jsonResponse in a .json format

if __name__ == '__main__':
	 app.run(debug=True)