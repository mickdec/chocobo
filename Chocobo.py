import sys
import requests
import re
import json
import time
import socketio
sys.path.insert(0, sys.path[0].replace("\\SRC\\Core\\Modules", "").replace("/SRC/Core/Modules",""))

from SRC.Core import Globals
from SRC.Libs import LibDebug

LibDebug.CheckChocoboReq()

selfContent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Alias": "Chocobot"
}

class CVE:
    def __init__(self, title, link, description, date):
        self.title = title
        self.link = link
        self.description = description
        self.date = date
    
    def toDict(self):
        content = dict()
        content['title'] = self.title
        content['link'] = self.link
        content['description'] = self.description
        content['date'] = self.date
        return content

def menu():
    print("Welcome to Chocobo")

    fil = []
    i = 0
    if len(sys.argv) > 1:
        for a in sys.argv:
            if i > 0:
                fil.append(a)
            i += 1

    LibDebug.Log("WORK", "Starting the flux")

    cves = list()
    if len(fil) > 0:
        fil = '+'.join(fil)
        response = json.loads(requests.get("https://services.nvd.nist.gov/rest/json/cves/1.0?keyword="+fil+"&resultsPerPage=2000&cvssV2Severity=HIGH", stream=True, headers=selfContent).text)
        for cve in response["result"]["CVE_Items"]:
            cves.append(CVE(
            cve["cve"]["CVE_data_meta"]["ID"],
            cve["cve"]["references"]["reference_data"][0]["url"],
            cve["cve"]["description"]["description_data"][0]["value"],
            cve["publishedDate"]))
    else:
        response = requests.get("https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss-analyzed.xml", stream=True, headers=selfContent).text
        titles = re.findall(r'<title>.*<\/title>', response)
        links = re.findall(r'<link>.*<\/link>', response)
        descriptions = re.findall(r'<description>.*<\/description>', response)
        dates = re.findall(r'<dc:date>.*<\/dc:date>', response)

        counter = len(titles)
        if counter == len(links) and counter == len(descriptions):
            for elem in range(0, counter):
                cves.append(CVE(titles[elem][7:-8], links[elem][6:-7], descriptions[elem][13:-14], dates[elem][9:-10]))

        cveTMP=dict()
        for cve in cves:
            cveTMP[cve.title + "CHOCOBO" + cve.link + "CHOCOBO" + cve.description + "CHOCOBO" + cve.date] = cve.date.replace('-','').replace('T','').replace('Z','').replace(':','')
        
        date_list = list()
        for v in cveTMP.values():
            date_list.append(int(v))

        date_list = list(dict.fromkeys(date_list))
        date_list.sort(reverse = True)

        for date in date_list:
            for k,v in cveTMP.items():
                if v == str(date):
                    values = k.split("CHOCOBO")
                    cves.append(CVE(values[0],values[1],values[2],values[3]))

    i = 0
    sio = socketio.Client()
    try:
        sio.connect('http://localhost:3000')
        LibDebug.Log("SUCCESS", "socket.io successfuly connected.")
        sio.sleep(1.0)
        LibDebug.Log("SUCCESS", "Sending " + str(len(cves)) + ".")
        for cve in cves:
            json_content = cve.toDict()
            if "National Vulnerability Database" not in json_content['title']:
                sio.emit('chocobo', json.dumps(json_content))
                LibDebug.Log("SUCCESS", "Send success for cve info.")
                i += 1
        sio.disconnect()

        LibDebug.Log("SUCCESS", "Flux sended. " + str(i) + " cves.")
    except:
        LibDebug.Log("ERROR", "Can't send the flux to server.")
        
    exit()

menu()
