from pymongo import MongoClient
from sqlite3 import Date
from urllib.request import urlopen
import datetime
import json
import os
url = "https://data.ntpc.gov.tw/api/datasets/308dcd75-6434-45bc-a95f-584da4fed251/json?page={}&size=300"

stillHasContent = True
pageIndex = 0
holidays = []

check_duplicate = {}


def transform(opendataItem):
    if (opendataItem['isholiday'] != '是' and opendataItem["holidaycategory"] != '特定節日'):
        return None
    opendataItem.pop('isholiday', None)
    if (opendataItem["date"] in check_duplicate):
        return None
    else:
        check_duplicate[opendataItem["date"]] = opendataItem
    if ("date" in opendataItem):
        opendataItem["_id"] = opendataItem["date"]
        opendataItem["date"] = datetime.datetime.strptime(
            opendataItem["date"], "%Y/%m/%d")
        opendataItem["year"] = opendataItem["date"].year
        opendataItem["month"] = opendataItem["date"].month
    if ("name" not in opendataItem or opendataItem["name"] == ""):
        if opendataItem["holidaycategory"] == "星期六、星期日":
            if(opendataItem["date"].weekday() == 5):
                opendataItem['name'] = "週六"
            else:
                opendataItem['name'] = "週日"
        else:
            opendataItem['name'] = opendataItem["holidaycategory"]
    if ("description" in opendataItem and opendataItem["description"] == ""):
        opendataItem.pop('description', None)
    if ("holidaycategory" in opendataItem):
        opendataItem["category"] = (
            "週末" if opendataItem["holidaycategory"] == "星期六、星期日" else opendataItem["holidaycategory"])
        opendataItem.pop('holidaycategory', None)
    return opendataItem


def isConsecutive(opendataItem):
    if ("consecutive" in opendataItem):
        return opendataItem["consecutive"]
    return False


# store the response of URL
while stillHasContent:
    response = urlopen(url.format(pageIndex))
    pageIndex += 1
    data_json: list = json.loads(response.read())
    holidays.extend([x for x in map(transform, data_json) if x is not None])
    stillHasContent = (len(data_json) == 300)

previous_holiday = holidays[0]["date"]
holiday_count = 1
for i in range(1, len(holidays)):
    delta = holidays[i]["date"] - previous_holiday
    if (delta.days == 1):
        holiday_count += 1
        previous_holiday = holidays[i]["date"]
    elif (holiday_count >= 3):
        for j in range(0, holiday_count):
            holidays[i-j-1]["consecutive"] = True
        holiday_count = 1
        previous_holiday = holidays[i]["date"]
    else:
        holiday_count = 1
        previous_holiday = holidays[i]["date"]

if (holiday_count >= 3):
    for j in range(0, holiday_count):
        holidays[-j-1]["consecutive"] = True

print(holidays)
client = MongoClient("mongodb+srv://{}@public.vovmgbr.mongodb.net/?retryWrites=true&w=majority".format(os.getenv('MONGODB_CREDENTIAL')))
collection = client["public"]["taiwan-holidays"]
collection.delete_many({})
collection.insert_many(holidays, ordered=True, bypass_document_validation=False, session=None)