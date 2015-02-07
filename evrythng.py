#!/usr/bin/python

# EVRYTHNG API Python Wrapper v0.92 - Vlad Trifa
# Engine 1.17

# Import all basic libs needed
import simplejson as json
import httplib, urllib
import csv
import logging

# Import some tools to measure execution time
import time
import corestats


# Set to 1 to force HTTPS 
SECURE=1

# Which API Endpoint
hostname="api.evrythng.com"

# The Various API Keys
apiKey="YOUR_OPERATOR_KEY_HERE"
appId="YOUR_APP_ID"
userId="YOUR_USER_ID"

inApp=0
logLevel=0


# FIXME: add other log levels here - 0 is debug, 1 is info, 2 is warning, 3 is errors
def setLogLevel(level):
	global logLevel
	if level:
		logging.basicConfig(level=logging.INFO,
    		format='%(levelname)-8s: %(message)s'
    		)
		logging.info("Simple Log mode")
	else:
		logging.basicConfig(level=logging.DEBUG,
    		format='%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s',
    		datefmt='%m-%d %H:%M',
    		)	
		logging.info("Full log mode")
	logLevel=level
	

### This is to setup the environments / app / user contexts

def setDomain(domain):
	global hostname 
	hostname = domain
	logging.info("API Endpoint: " + hostname)

def setOperator(key):
	global apiKey 
	apiKey = key
	logging.info("Scope: OPERATOR key: " + apiKey)
	headProducts()
	# FIXME: add testing right here if works, otherwise return error

def setApp(key,id):
	global apiKey,appId 
	apiKey = key
	appId = id
	logging.info("Scope: APP id "+ appId +" (APP API KEY: "  + apiKey +")")
	inApp=1
	headProducts()
	# FIXME: add testing right here if works, otherwise return error

def setUser(key,id):
	global apiKey,userId 
	apiKey = key
	userId = id
	logging.info("Scope: USER id "+ userId +" (APP API KEY: "  + apiKey +")")
	inApp=1
	# FIXME: add testing right here if works, otherwise return error


# Print the response of the API
def printResponse(response):
	logging.info(response['headers'])

	# pretty print response body, if any
	if response['body'] != '':		
		logging.info("Response Content Body: \n"+ json.dumps(json.loads(response['body']), indent=4))
	else:
		logging.info("No response body.")


# Validates if the API response is the one expected
def validateResponse(response,validCode,errorCode):
	# Check if successful
	if response[0]['status'] != validCode:
		logging.error(errorCode + ". Status code: " + str(response[0]['status']))
		logging.error(response[0]['headers'])
		logging.error(response[0]['body'])


# Sends a request to the EVRYTHNG Engine
def sendRequest(method, url, body='', headers=''):
	global hostname 

	# By default for all calls
	headers['Authorization'] = apiKey		
	 
	# Use HTTP or HTTPs Connection
	if SECURE:
		port=443
	else:
		port=80
		
	# We create a connection	
	conn = httplib.HTTPSConnection(
		host=hostname,
		port=port
	)

	json_body=json.dumps(body)


	# Build the HTTP request with the body, headers & co
	conn.request(
		method=method,
		url='%s' % url,
		body=json_body,
		headers=headers
	)

	# Send the request
	logging.info("-> ###  %s %s:%s%s " % (method,hostname,port,url))
	logging.info("-> Headers: " + json.dumps(headers))
	logging.info("-> Payload: " + json_body)

	# Send the request and time it
	start = time.time() 
	full_response = conn.getresponse()
	rt = float("%.2f" % ((time.time() - start)*1000)) # Response Time RT (milliseconds)

	# Parse the response
	response={} # Parse the HTTP response
	response['body']=full_response.read()
	response['headers']=full_response.getheaders()
	response['status']=full_response.status
	response['reason']=full_response.reason
	conn.close()

	# And confirm 
	logging.info("<- ###  %s %s  ###" % (response['status'],response['reason']))
	logging.info("<- ###  RT  %0.5f [ms] ###" % rt)
	
	if logLevel==0:
		printResponse(response)
	
	return [response, rt]


#---- Implementation of a few endpoints in the engine 	

def headThngs():
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="HEAD",
		url="/thngs",
		headers=headers
	)
	validateResponse(response,200,"Problem HEAD /thngs")
	return response	

# GET the list of all THNGS for a user
def getAllThngs(scope=''):
	headers = {"Accept": "application/json"}

	if scope=='all':
		scopedUrl="/thngs?app=all"
	elif scope=='':
		scopedUrl="/thngs"
	else:
		scopedUrl="/thngs/?app=%s" % scope

	response = sendRequest(
		method="GET",
		url=scopedUrl,
		headers=headers
	)
	return response	


# Gets list of thngs using a filter (filter should be human readable)
def getThngs(filterString):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url="/thngs/?filter=%s" % urllib.quote_plus(filterString),
		headers=headers
	)

	validateResponse(response,200,"Problem GET /thngs")
	return response	


# POST a new THNG
def createThng(thngDocument,scope=''):
	headers = {"Content-Type": "application/json"}
	
	if scope=='all':
		scopedUrl="/thngs?app=all"
	elif scope=='':
		scopedUrl="/thngs"
	else:
		scopedUrl="/thngs/?app=%s" % scope
	
	response = sendRequest(
		method="POST",
		url=scopedUrl,
		body=thngDocument,
		headers=headers
	)

	validateResponse(response,201,"Problem POST /thngs")
	return response	

# GET a THNG
def getThng(thngID):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url="/thngs/%s" % thngID,
		headers=headers
	)

	validateResponse(response,200,"Problem GET /thngs")
	return response	

# DELETE a THNG
def deleteThng(thngID):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="DELETE",
		url="/thngs/%s" % thngID,
		headers=headers
	)
	
	validateResponse(response,200,"Problem DELETE /products/{id}")
	return response	


# UPDATE a THNG
def updateThng(thngID,propDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="/thngs/%s" % thngID,
		body=thngDocument,
		headers=headers
	)	

	validateResponse(response,200,"Problem PUT /thngs/{id}")
	return response	


def headProducts():
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="HEAD",
		url="/products",
		headers=headers
	)
	validateResponse(response,200,"Problem HEAD /products")
	return response	


# POST a new PRODUCT
def createProduct(productDocument,scope='all'):
	headers = {"Content-Type": "application/json"}
	
	if scope=='all':
		scopedUrl="/products?app=all"
	elif scope=='':
		scopedUrl="/products"
	else:
		scopedUrl="/products/?app=%s" % scope
	
	response = sendRequest(
		method="POST",
		url=scopedUrl,
		body=productDocument,
		headers=headers
	)

	validateResponse(response,201,"Problem POST /products")
	return response	
	

# GET the list of all THNGS for a user
def getProducts(scope=''):
	headers = {"Accept": "application/json"}

	if scope=='all':
		scopedUrl="/products?app=all"
	elif scope=='':
		scopedUrl="/products"
	else:
		scopedUrl="/products/?app=%s" % scope

	response = sendRequest(
		method="GET",
		url=scopedUrl,
		headers=headers
	)

	validateResponse(response,200,"Problem GET /products")
	return response	

# GET a PRODUCT
def getProduct(productID):
	headers = {}
	response = sendRequest(
		method="GET",
		url="/products/%s" % productID,
		headers=headers
	)
	return response	


# DELETE a PRODUCT
def deleteProduct(productID):
	headers = {}
	response = sendRequest(
		method="DELETE",
		url="/products/%s" % productID,
		headers=headers
	)

	validateResponse(response,200,"Problem DELETE /products")

	return response	


# UPDATE a PRODUCT
def updateProduct(productID,productDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="/thngs/%s" % productID,
		body=productDocument,
		headers=headers
	)	

	return response	


# UPDATE PROPERTIES of an entity, by default a THNG
def updateProperties(entityID,propertyDocument,entityPath='/thngs'):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="%s/%s/properties" % (entityPath,entityID),
		body=propertyDocument,
		headers=headers
	)	

	return response	

# GET LIST of PROPERTIES of a THNG
# Returns array of form ...
def getProperties(entityID,entityPath='/thngs'):
	response = sendRequest(
		method="GET",
		url="%s/%s/properties" % (entityPath,entityID),
		headers=headers
	)	

	return response	


# GET HISTORY of a single PROPERTY of a THNG
# Returns array of form ...
def getProperty(entityID,propertyID,entityPath='/thngs'):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url="%s/%s/properties%s" % (entityPath,entityID,propertyID),
		headers=headers
	)	

	return response	


# GET list of LOCATIONS of a THNG
# Location *must* be an object: location={'latitude': 'some', 'longitude': 'stuff', 'timestamp': 234234}
def getLocations(thngID):
	call_url="/thngs/%s/location" % thngID

#	if from !=''
#		call_url += "?from=%s" % from
#	if to !=''
#		call_url += "to=%s" % from

	response = sendRequest(
		method="GET",
		url=call_url,
		headers=headers
	)	

	return response	


# UPDATE LOCATION of a THNG
# Location *must* be an object: location={'latitude': 'some', 'longitude': 'stuff', 'timestamp': 234234}
def updateLocation(thngID,location):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="/thngs/%s/location" % thngID,
		body=location,
		headers=headers
	)	

	return response	


# CREATE COLLECTION
def createCollection(collDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/collections",
		body=collDocument,
		headers=headers
	)
	
	validateResponse(response,201,"Problem POST /collections")
	return response

# UPDATE COLLECTION
def updateCollection(collId,collDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="/collections/%s" % collId,
		body=collDocument,
		headers=headers
	)	

	return response

# GET COLLECTION
def getCollection(collId,headers=''):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="GET",
		url="/collections/%s" % collId,
		headers=headers
	)	

	validateResponse(response,200,"Problem GET /collections")
	return response

# DELETE COLLECTION
def deleteCollection(collId,headers=''):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="DELETE",
		url="/collections/%s" % collId,
		headers=headers
	)	

	validateResponse(response,200,"Problem DELETE /collections")
	return response


# ADD THNGS to COLLECTION
def addToCollection(collID,thngList):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="/collections/%s/thngs" % collID,
		body=thngList,
		headers=headers
	)	
	validateResponse(response,200,"Problem PUT /collections/")
	return response
	
# POST a redirection
def createRedirection(thngID,redirectionDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/thngs/%s/redirector" % thngID,
		body=redirectionDocument,
		headers=headers
	)	

	validateResponse(response,201,"Problem POST /redirector")
	return response
	
# DELETE a redirection
def deleteRedirection(thngID):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="DELETE",
		url="/thngs/%s/redirector" % thngID,
		headers=headers
	)	

	validateResponse(response,200,"Problem DELETE /redirector")
	return response
	
# GET the QR code
def getQr(thngID,size,format):
	headers = {"Accept": format}
	response = sendRequest(
		method="GET",
		url="/thngs/%s/redirector/qr?h=%s&w=%s" % (thngID,size,size),
		headers=headers
	)	

	validateResponse(response,200,"Problem GET /redirector/qr")
	return response
	
# GET the QR code
def getQrTemplated(shortID,size,format,template):
	# The endpoint to generate QR codes with templates
	headers = {"Accept": format}
	response = sendRequest(
		method="GET",
		url="/redirections/%s.qr?h=%s&w=%s&tpl=%s" % (shortID,size,size,template),
		headers=headers,
		body='',
		domain="tn.gg"
	)	

	validateResponse(response,200,"Problem GET /redirector/qr")
	return response
	

def storeCollectionThngsinCSV(collectionID):
	# Do the stuff and let go
	return null


############## ACTIONS	

### Action types

# GET all action types
# FIXME Allow to give as param the projectId, the thng, the product, the tag(s) 
def getActionTypes(scope=''):
	
	if scope=='all':
		scopedUrl="/actions?app=all"
	elif scope=='':
		scopedUrl="/actions"
	else:
		scopedUrl="/actions?app=%s" % scope
	
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url=scopedUrl,
		headers=headers
	)
	
	validateResponse(response,200,"Problem GET /actions")
	return response

# POST a new action type
def createActionType(actionTypeDocument,scope=''):
	
	if scope=='all':
		scopedUrl="/actions?app=all"
	elif scope=='':
		scopedUrl="/actions"
	else:
		scopedUrl="/actions?app=%s" % scope
	
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url=scopedUrl,
		body=actionTypeDocument,
		headers=headers
	)
	
	validateResponse(response,201,"Problem POST /actions")
	return response


# DELETE an action type
def deleteActionType(actionType):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="DELETE",
		url="/actions/%s" % actionType,
		headers=headers
	)
	
	validateResponse(response,200,"Problem DELETE /actions/{Type}")
	return response




### Actions 
def createAction(actionType,actionDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/actions/%s" % actionType,
		body=actionDocument,
		headers=headers
	)

	validateResponse(response,201,"Problem POST /actions/{Type}")
	return response



# Attention this returns only 100 actions max
# Allow to give as param the projectId, the thng, the product, the tag(s) 
def getActions(actionType):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url="/actions/%s" % actionType,
		headers=headers
	)
	
	validateResponse(response,200,"Problem GET /actions/{Type}")
	return response





############## APPLICATIONS	

# GET /applications   --- Returns the list of all Applications
def getAllApplications():
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url="/applications",
		headers=headers
	)

	validateResponse(response,200,"Problem GET /applications")
	return response	

# GET /applications   --- Reads an existing application
def getApplication(appId):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="GET",
		url="/applications/%s" % appId,
		headers=headers
	)

	validateResponse(response,200,"Problem GET /applications/{id}")
	return response	

	
# POST /applications   --- Create a new application
def createApplication(appDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/applications",
		body=appDocument,
		headers=headers
	)

	validateResponse(response,201,"Problem POST /applications")
	return response	
	

# PUT /applications   --- Updates an existing application
def updateApplication(appId,appDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="PUT",
		url="/applications/%s" % appId,
		body=appDocument,
		headers=headers
	)

	validateResponse(response,200,"Problem PUT /applications/{id}")
	return response	


# POST /applications   --- DELETE a new application
def deleteApplication(appId):
	headers = {"Accept": "application/json"}
	response = sendRequest(
		method="DELETE",
		url="/applications/%s" % appId,
		headers=headers
	)

	validateResponse(response,200,"Problem DELETE /applications")
	return response	
	

############## USERS	

# POST /auth/evrythng/users   --- Create a new EVRYTHNG Anonymous user in an APP
def createAnonUser(userDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/auth/evrythng/users?anonymous=true",
		body=userDocument,
		headers=headers
	)
	# FIXME use correct API endpoint & signature
	validateResponse(response,201,"Problem POST /auth/evrythng/users")
	return response

# POST /auth/evrythng/users   --- Create a new EVRYTHNG user in an APP
def createEvtUser(userDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/auth/evrythng/users",
		body=userDocument,
		headers=headers
	)

	validateResponse(response,201,"Problem POST /auth/evrythng/users")
	return response


# POST /users/X/validate   --- Create a new EVRYTHNG user in an APP
def validateEvtUser(userId,validationDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/auth/evrythng/users/%s/validate" % userId,
		body=validationDocument,
		headers=headers
	)

	validateResponse(response,200,"Problem POST /auth/evrythng/users")
	return response


# POST /auth/evrythng/users   --- Create a new application
# loginDocument={"email":"XXX","password":"YYY"}
def loginEvtUser(loginDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/auth/evrythng",
		body=loginDocument,
		headers=headers
	)

	validateResponse(response,201,"Problem POST /auth/evrythng/")
	return response

# POST FB user 
# {"access": {"expires" : <Timestamp>,"token"": &lt;Facebook-Token&gt;}}
def createFbUser(userDocument):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/auth/facebook",
		headers=headers
	)

	validateResponse(response,201,"Problem POST /auth/evrythng/users")
	return response	


# POST /logout -- Logs out the user, done using the user api key
def logoutUser():
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="POST",
		url="/auth/all/logout",
		headers=headers
	)

	# FIXME PUT instead of POST, 200 instead of 201
	validateResponse(response,201,"Problem POST /auth/all/logout")
	return response	


# GET /users/X -- reads data about 1 user
def getUser(userId):
	headers = {"Content-Type": "application/json"}
	response = sendRequest(
		method="GET",
		url="/users/%s" % userId,
		headers=headers
	)

	validateResponse(response,200,"Problem GET /users/X")
	return response	

# GET /users/ -- reads all users in a given app (or all apps)
def getUsers(appId=0):
	headers = {"Accept": "application/json"}

	if appId == 0:
		userScope="/users"
	else:
		userScope="/users/?app="+str(appId)
		
	response = sendRequest(
		method="GET",
		url=userScope,
		headers=headers
	)

	validateResponse(response,200,"Problem GET /users")
	return response	

# TOOLS

# Reads a product file
def importProducts(filename):
	products=[]
	data = csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"')
	fields = data.next()
	for row in data:
		items = zip(fields, row)
		products.append(dict(zip(fields, row)))

	logging.info("Imported " + str(len(products)) + " products from:" + filename)

	return products	

# Not Done Not Tested
def importCsvData(filename):
	output=[]
	data = csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"')
	fields = data.next() # Gets the first column
	for row in data:
		output.append(dict(zip(fields, row)))

	logging.info("Imported " + str(len(output)) + " entities from:" + filename)

	return output	
