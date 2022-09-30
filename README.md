# taiwan-holidays-mongodb
台灣節日的MongoDB和 Restful Data API，可以使用mongodb或 Restful API 進行查詢/篩選

由於現有的 Public Opendata API (台北市/新北市)都是分頁格式，必須把所有資料都拉下來才能處理。 如果只是想要查詢特定的節假日，或是想要找「連續假日」都很麻煩。所以把資料整理了一下放到MongoDB方便查詢。 目前從2013到2023的資料都已經更新了，預計每季會跑一次data update。

## 連線資訊
  - **cluster url** `public.vovmgbr.mongodb.net`
  - **db** `public`
  - **collection**: `taiwan-holidays`
  - **username:** `taiwan`
  - **password:** `public`

  - **DataAPI endpoint:** `https://southeastasia.azure.data.mongodb-api.com/app/data-pjagx/endpoint/data/v1`
  - **dataSource** `public`
  - **api-key:** `YsM3npR5ipSE052zu9h1epaa4Vo3OB0AFvlPL7mTH0Gw8yzU4hI02p2xsZa6zMqB`
  
  
##  資料說明範例
  
```json
{
  "_id": "2023/1/1", 
  "date": "2023-01-01T00:00:00.000+00:00",
  "description": "全國各機關學校放假一日。",
  "year": 2023,
  "month": 1,
  "category": "放假之紀念日及節日",
  "consecutive": true //是否為連續假日(三天以上)
}
```

## 查詢範例
1. 使用 python MongoDB driver: 查詢今年和明年的所有假日
```python
from pymongo import MongoClient
import datetime
client = MongoClient("mongodb+srv://taiwan:public@public.vovmgbr.mongodb.net")
collection = client["public"]["taiwan-holidays"]
cursor = collection.find({ "year": {"$gte": datetime.datetime.now().year}})
for document in cursor:
     print(document)
```

2. 使用curl 查詢2022年的所有「連續假日」
```shell
curl --location --request POST 'https://southeastasia.azure.data.mongodb-api.com/app/data-pjagx/endpoint/data/v1/action/find' \
--header 'Content-Type: application/json' \
--header 'Access-Control-Request-Headers: *' \
--header 'api-key: YsM3npR5ipSE052zu9h1epaa4Vo3OB0AFvlPL7mTH0Gw8yzU4hI02p2xsZa6zMqB' \
--data-raw '{
    "collection":"taiwan-holidays",
    "database":"public",
    "dataSource":"public",
    "filter": { "year": 2022, "consecutive": true}
}'
```

### 其他MongoDB查詢範例
檢查該日(yyyy/m/d)是否為已知假日
```json
{ "_id": "2017/1/1" }
```

查詢中秋節
```json
{ "name":"中秋節" }
```

查詢 2022年，所有假日排除週末
```json
{ "year": 2022, "category": { "$ne": "週末"} }
```

## 免責聲明
Cluster是使用MongoDB Altas的免費空間@GCP Taiwan datacenter，所以用MongoDB driver 連線速度比較快。而DataAPI在新加坡，所以用RESTful API會比較慢。
但這都是用free shared resource，所以不保證多穩定就是了...



