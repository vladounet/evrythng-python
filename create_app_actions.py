#!/usr/bin/python

import simplejson as json
import csv
import sys
import random
import time

from evrythng import * 

# 0 for displaying all data, 1 only for critical stuff, 2 for warning & errors, 3 for errors only
setLogLevel(0)


#### STEP 0 -  Setup the Prerequisites: create operator account, FB app, etc. and set those values
# This is the Operator API key from your account (here: https://dashboard.evrythng.com/account)


# Configure Server Connex
import environments # Gets the variables
setDomain(environments.my_account['domain'])
setOperator(environments.my_account['operatorApiKey'])


# Check if you can read your thngs (in the app)
[response,end] = getAllThngs(appId)
if response["status"]!=200:
	sys.exit("ERROR -- Problem getting thngs - check your API Key")

thngs = json.loads(str(response['body']))
print thngs

# We fix the period when actions should occur
endTimestamp=int(time.time()*1000) # like, now
startTimestamp=endTimestamp-2592000000 # like 30 days ago
#timeRange=endTimestamp-startTimestamp


# Now we're ready to populate the account



# Load Users/create users
# Check if you can read your thngs
[response,end] = getUsers(appId)
if response["status"]!=200:
	sys.exit("ERROR -- Problem getting users in the APP - check your API Key")

# Change to app scope
setApp(appApiKey,appId)


# The list of actions that can be done by users in this app
# Fixme: ideally import this from the engine (from the app)
actionTypes=['scans','checkins','_InvitedFriend','_EarnPoints','_ReceivedReward','_InvitedFriend']

users = json.loads(str(response['body']))
print users

for user in users:
	
	# Log this user in
	loginDoc={'email': user['email'],'password':'IamNotReal'}
	[response,end] = loginEvtUser(loginDoc)
	respy = json.loads(str(response['body']))
	userApiKey = respy["evrythngApiKey"] 
	
	# Create X actions for this user on any thing
	setUser(userApiKey,user['id'])
	
	for x in range(1,10): 
		thngId=random.randint(0, len(thngs)-1) # pick a random thng
		timestamp=random.randint(startTimestamp, endTimestamp) # pick a random timestamp
		actionType=actionTypes[random.randint(0, len(actionTypes)-1)] # pick a random action type
		
		logging.info("Action %s by user %s on thng#%s @ %s" % (actionType,user['id'],thngs[thngId]['id'],timestamp))

		action= {'thng':str(thngs[thngId]['id']),'type':actionType,'timestamp':timestamp,'locationSource':'sensor','location':{'position':{'type':'Point','coordinates':[random.uniform(1, -1),random.uniform(50, 52)]}},'tags':['UK','Loyalty','SpecialCampaign']}
		createAction(actionType,action)

sys.exit("END OF CODE")







# We assume we get a list of thng & products


#
# STEP 1 -  Create a few products in the engine (from the CSV) 
#
# Import the list of products from a file
products=[]
data = csv.reader(open('products_list.csv', 'rb'), delimiter=',', quotechar='"')
fields = data.next()
for row in data:
	items = zip(fields, row)
	products.append(dict(zip(fields, row)))

logging.info("Imported " + str(len(products)) + " products from CSV file.")


# Arrays to record response times for various request types. 
create_products_rt=[]
update_properties_rt=[]
delete_products_rt=[]
product_ids=[]
prod_ids={}

# For each product imported from the file, create a thng in the engine
for product in products[0:len(products)]:
	print product
	
	sku=product['sku']
	
	# Create an object to hold the data	
	current = {'fn': product['product'], 'description': product['description'],'identifiers':{'EAN13': product['EAN13'],'UPCA': product['UPCA'],'sku': sku}}
		
	# Now create a PRODUCT in the EVRYTHNG engine
	[response,rt] = createProduct(current)
	create_products_rt.append(rt) # Record response times

	# Parse the response JSON Object to get the ID of the thing
	respy = json.loads(str(response['body']))
	productID = respy["id"] #or 'id'????
	
	# Add the list of the IDs created to a list
	prod_ids[sku] = productID

	# Then create the properties for that product (add all other properties)
	props = [{'key':'created','value':product['created']},{'key':'url','value':product['url']},{'key':'modified','value':product['modified']},{'key':'UPCA','value':product['UPCA']}]
	[response,rt] = updateProperties(productID,props,"/products")
	update_properties_rt.append(rt) # Record response time
		
	# Then we delete that product
	[response,rt] = deleteProduct(productID)
	delete_products_rt.append(rt) # Record response time

# Save the [sku,productID] mappings in a file
file = open("mapping_products.csv", "wb")
productWriter = csv.writer(file , delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
for sku in prod_ids.keys():
	productWriter.writerow([sku,prod_ids[sku]])	
file.close()


# Now display the stats for the various requests (ideally we should store the data poins in a CSV for futher analysis)
stats = corestats.Stats(create_products_rt)
logging.info("--- create_products_rt stats \n min/avg/max/stddev = %0.2f/%0.2f/%0.2f/%0.2f \n\n" % (stats.min(),stats.avg(),stats.max(),stats.stdev()) )

stats = corestats.Stats(update_properties_rt)
logging.info("--- update_properties_rt stats \n min/avg/max/stddev = %0.2f/%0.2f/%0.2f/%0.2f \n\n" % (stats.min(),stats.avg(),stats.max(),stats.stdev()) )

stats = corestats.Stats(delete_products_rt)
logging.info("--- delete_products_rt stats \n min/avg/max/stddev = %0.2f/%0.2f/%0.2f/%0.2f \n\n" % (stats.min(),stats.avg(),stats.max(),stats.stdev()) )





#
# STEP 2 - Now let's open a list of thngs, create an ADI for each unique product, generate a redirection, print a QR code
#
thngs=[]
data = csv.reader(open('unique_products_internal.csv', 'rb'), delimiter=',', quotechar='"')
fields = data.next()
for row in data:
	items = zip(fields, row)
	thngs.append(dict(zip(fields, row)))

logging.info("Imported " + str(len(thngs)) + " individual products from text file.")


# This is to test the response times for the requests. 
create_thngs_rt=[]
create_qr_rt=[]
thng_ids=[]

# Let's record the product mappings
file = open("mappings_thngs.csv", "wb")
productWriter = csv.writer(file , delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)

# For each product instance imported from the file, create an ADI in the engine
for thng in thngs[0:len(thngs)]:
	
	# get the (internal) SKU (used to map to product)
	sku = thng['sku']
		
	# Create an object to hold the data	
	current = {'name': thng['product_name'], 'description': thng['description'], 'product': prod_ids[sku], 'properties':{'sku':sku,'serialID':thng['serialID'],'default-url':thng['default-url'],'country':thng['country'],'created':thng['created'],'shipped':thng['shipped']} }
		
	# Now create an ADI in the EVRYTHNG engine
	[response,rt] = createThng(current)
	create_thngs_rt.append(rt) # Record response time

	# Parse the response JSON Object to get the ID of the ADI
	respy = json.loads(str(response['body']))
	thngID = respy["id"]
	
	# Add the list of the IDs created to a list
	thng_ids.append(thngID)
	productWriter.writerow([thng['serialID'],thngID])	

	# Now let's create a default redirection for the ADI
	redirection = {'defaultRedirectUrl':thng['default-url']+"?thng_id={thngId}"}
	[response,rt] = createRedirection(thngID,redirection)

	# Download and save the QR code 
	[response,rt] = getQr(thngID,800,"application/pdf")
	create_qr_rt.append(rt) # Record response time
	file_name = "tags/"+thng['serialID']+".pdf"
	logging.info("Saving file %s" % file_name)
	local_file = open(file_name, "wb")	
	local_file.write(response['body'])
	local_file.close()
		
file.close()

# Now let's create a collection with all those thngs
collection={'name': 'Test thngs set', 'description': 'A set of unique product instances ready to be attached to products', 'tags':['python','test','randomprintResponse']}
[response,end] = createCollection(collection)

# Get the collection ID of it
respy = json.loads(str(response['body']))
collID = respy["id"]

# Add the thngs to the collection
[response,end] = add_to_collection(collID,thng_ids)

# At the end just display the core stats, and ideally we should store the data poins in a CSV or something
stats = corestats.Stats(create_thngs_rt)
logging.info("--- createThng() stats \n min/avg/max/stddev = %0.2f/%0.2f/%0.2f/%0.2f \n\n" % (stats.min(),stats.avg(),stats.max(),stats.stdev()) )

stats = corestats.Stats(create_qr_rt)
logging.info("--- getQr() stats \n min/avg/max/stddev = %0.2f/%0.2f/%0.2f/%0.2f \n\n" % (stats.min(),stats.avg(),stats.max(),stats.stdev()) )
