"""
Created on Thu Feb 17 2022
@author: armin.adeli
"""
import requests
import sys
import json




def GetServices_list(url, token , fromDate, toDate):
    api = url + "/api/v2/entities"
    parameters = {

        "Authorization": "Api-Token " + token
    }
    entityType = 'type("service")'
    genericTime = "T00%3A00%3A00"
    pageSize = "500"
    #fromDate = "2022-03-29" + genericTime
    #toDate = "2022-04-03" + genericTime 

    url = api + '?' + 'pageSize=' + pageSize + '&entitySelector=' + entityType + "&from=" + fromDate + genericTime + "&to=" + toDate + genericTime
    #print(url)
    get_list = requests.get(url, headers=parameters)
    if(get_list.status_code >= 400):
        return({"status_code": get_list.status_code, "status_message": [get_list.json()]})
    else:
        content_list = get_list.json()
        
        serviceID_list = content_list["entities"]
        
    return serviceID_list

def GetSettings_objects(s_list , url, token):
    totalKeyRequests = 0
    content_list = []
    api = url + "/api/v2/settings/objects"
    parameters = {
        "Authorization": "Api-Token " + token
    }
    schemaIds = "builtin%3Asettings.subscriptions.service"
    
    fields = "objectId%2Cvalue"
       
    for sid in s_list:
        scope = sid["entityId"]
        print("Service ID: ", scope)
        url = api + "?schemaIds=" + schemaIds + "&scopes=" + scope + "&fields=" + fields 
        get_list = requests.get(url, headers=parameters)
        if(get_list.status_code >= 400):
            return({"status_code" : get_list.status_code, "status_message": [get_list.json()]})
        else:
            content_list.append(get_list.json())
            response = get_list.json()
            if response ['items']:
                print("Get list: ", response['items'][0]['value']['keyRequestNames'])
        print("************************************************************************************")
   
    for sid in content_list:
        if sid['items']:
            for i in sid['items'][0]['value']['keyRequestNames']:
                print(i)
                totalKeyRequests += 1 
            
    
    return content_list
           
def GetUpdateToken(objId , url,  token):
    content_list = []
    api = url +"/api/v2/settings/objects"
    parameters = {
        "Authorization": "Api-Token " + token
    }
   
    url = api + "/" + objId 
    
    get_list = requests.get(url, headers=parameters)
    if(get_list.status_code >= 400):
        return({"status_code" : get_list.status_code, "status_message": [get_list.json()]})
    else:
        content_list = get_list.json()
    return content_list
            

def Clear_keyRequest(updateToken, objectId , url, token):
    
    api = url + "/api/v2/settings/objects"
    parameters = {
        "Authorization": "Api-Token " + token,
        'content-type':'application/json',
        'accept': 'application/json',
        'chartset':'charset=utf-8'
    }
 
    url = api + "/" + objectId
    value = {} 
    payload = {'updateToken': updateToken, 'value': value}  

    clear_service_keyRequests = requests.put(url, headers=parameters, data=json.dumps(payload))
    if(clear_service_keyRequests.status_code >= 400):
        return({"status_code" : clear_service_keyRequests.status_code, "status_message": [clear_service_keyRequests.json()]})
    else:
        print("Presented Key Requests deleted")
    
  
            
if __name__ == "__main__":
   
    print("Add your environment URL")
    print("SaaS example: http://xxxxxx.live.dynatrace.com")
    print("Managed example: https://au.dynatrace.com/e/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx")
    url = input("Enter URL: ")
    token = input("Enter your token key: ")
    fromDate = input("Enter your from date in xxxx-xx-xx format: ")
    toDate = input("Enter your to date in xxxx-xx-xx format: ")

    serviceID_list = GetServices_list(url, token, fromDate, toDate)
    settingObject_list = GetSettings_objects(serviceID_list , url, token)
    keyRequestObject = []
    print("Are you sure you want to delete presented key requests? ")
    confirmation = input("y/n: ")
    if confirmation.lower() == 'y':    
        for sid in settingObject_list:
            if sid['items'][0]['objectId']:
                print(sid['items'][0])
                keyRequestObject = GetUpdateToken(sid['items'][0]['objectId'], url , token)
                objectID = keyRequestObject['objectId']
                updateToken = keyRequestObject['updateToken']
                output = Clear_keyRequest(updateToken, objectID, url, token)
        print(output)
    