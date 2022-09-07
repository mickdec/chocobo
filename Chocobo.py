import sys
import requests
import re
import json
import time
import xmltodict

patterns = ["windows","word","sentinel"]

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


def send_API(cves):
    err = 0
    for cve in cves:
        try:
            cve_data = """{\""""+cve.title+"""\":
            {
                "title": \""""+cve.title+"""\",
                "link": \""""+cve.link+"""\",
                "desc": \""""+cve.description+"""\",
                "datetime": \""""+cve.date+"""\"
            }
        }"""
            head = {"Content-Type": "application/json"}
            requests.post("http://127.0.0.1:80/add_exploit",
                        headers=head, data=json.dumps(json.loads(cve_data.replace("\\","/"))))
        except:
            err+=1
            print(cve_data)

        print("ERR > " + str(err))

def menu():
    fil = []
    i = 0
    if len(sys.argv) > 1:
        for a in sys.argv:
            if i > 0:
                fil.append(a)
            i += 1

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
        o = xmltodict.parse(response)
        o = json.loads(json.dumps(o))
        p = 0
        for e in o:
            for item in o[e]:
                p+=1
                if p > 4:
                    for x in o[e][item]:
                        brut = x["title"]+x["link"]+x["description"]+x["dc:date"]
                        for pattern in patterns:
                            if pattern in brut:
                                cves.append(CVE(x["title"],x["link"],x["description"],x["dc:date"]))

    i = 0
    print("Sending..")
    send_API(cves)
    time.sleep(30)
    menu()

menu()
