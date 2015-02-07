#!/usr/bin/python

import simplejson as json
import csv
import sys

from evrythng import * 
# 0 for displaying all data, 1 only for critical stuff, 2 for warning & errors, 3 for errors only
setLogLevel(0)

# Configure Server Connex
import environments # Gets the variables

setDomain(environments.my_account['domain'])
setOperator(environments.my_account['operatorApiKey'])

# Check if you can read your thngs
[response,end] = headThngs()
if response["status"]!=200:
	sys.exit("ERROR -- Problem getting thngs - check your API Key")


#### STEP 1 - Create Some Products

product=[]

p1 = {'fn':'Generic Whisky - UK','description':'Our basic whisky bottle (UK bottelling)','brand':'Spririts Inc.','url':'http://acme.org/spirits/whisky','categories':['drinks > whisky'] ,'photos': ['http://d10ka0m22z5ju5.cloudfront.net/53340bc9e4b00bf6903b8606/whisky~53394e7f73bbe672.png'],'identifiers':{'EAN8':'88808431','sap-id':'00001'},'customFields':{'size-ml':'770','market':'uk'},'tags':['acme','uk','whisky']}
[response,rt] = createProduct(p1,'all')
product = json.loads(str(response['body'])) # we parse the response
productId = product["id"] # and record the product id 

p2 = {'fn':'Generic Whisky - LATAM','description':'Our basic whisky bottle (LATAM bottelling)','brand':'Spririts Inc.','url':'http://acme.org/spirits/whisky','categories':['drinks > whisky'] ,'photos': ['http://d10ka0m22z5ju5.cloudfront.net/53340bc9e4b00bf6903b8606/whisky~53394e7f73bbe672.png'],'identifiers':{'EAN8':'88808432','sap-id':'00002'},'customFields':{'size-ml':'770','market':'latam'},'tags':['acme','uk','whisky']}
response = createProduct(p2,'all')

p3 = {'fn':'Generic Beer - UK','description':'Our basic beer (UK)','brand':'Spririts Inc.','url':'http://acme.org/spirits/beer','categories':['drinks > beer'] ,'photos': ['http://d10ka0m22z5ju5.cloudfront.net/530c7f23e4b0428ed37f7c23/beer~53456cb7d03c7bcc.png'],'identifiers':{'EAN8':'88808433','sap-id':'00003'},'customFields':{'size-ml':'330','market':'uk'},'tags':['acme','uk','beer']}
response = createProduct(p3,'all')

p4 = {'fn':'Savoury Snack - DE','description':'Our simple snack','brand':'Food Inc.','url':'http://acme.org/food/snack','categories':['drinks > beer'] ,'photos': ['http://cdn.evrythng.com/530c7f23e4b0428ed37f7c23/bag-of-chips_530c8270c5768553.png'],'identifiers':{'EAN8':'88808443','sap-id':'00004'},'customFields':{'size-g':'150','market':'Germany'},'tags':['acme','food','Germany','snack']}
response = createProduct(p4,'all')


## Create a few more...


### STEP 2 - Create thngs (5 of each)

# Either do it manually, 1 by 1
#thng = {'name':'Generic Whisky','description':'Our basic whisky bottle (UK bottelling)','product':productId,'identifiers':{'EAN8':'88808430','sap-id':'00001'},'customFields':{'bottelling-date':'16 June 2014 @ 13:35','market':'uk'},'tags':['acme','uk','generic','whisky']}
#response = createthng(thng,'all')

# Or use a loop
for x in range(1,5):
	thng={'name':product['fn']+"-"+str(x),'product':productId,'tags':['uk','whisky']}
	[response,rt]=createThng(thng,'all')
	respy = json.loads(str(response['body']))
	thngId = respy["id"]
	


#### STEP 3 - Create a few Application(apps)
app1={'name': 'Loyalty Program UK', 'description': 'A loyalty program .', 'socialNetworks':{}, 'defaultUrl':'http://acme.com/offers.php?thng={evrythngId}&apiKey=XXX', 'tags':['python','test','testingApp','UK']}	
[response,rt] = createApplication(app1)
app = json.loads(str(response['body']))
appId = app["id"] 




