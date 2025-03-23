# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "5b89a532-a8cf-4ce7-a4e4-b655b86d8ce0",
# META       "default_lakehouse_name": "lh_fabric_data",
# META       "default_lakehouse_workspace_id": "f430fe2a-5ad8-433a-a3d0-686ad70831be"
# META     },
# META     "environment": {}
# META   }
# META }

# MARKDOWN ********************

# # Fetch and save Fabric Known Issues 
# 
# https://support.fabric.microsoft.com/en-US/known-issues/

# CELL ********************

import requests
import datetime
import json
import json_repair
from uuid import uuid4

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Functions to parse Power BI data

# CELL ********************

# Most of the Power BI data parsing code comes from:
# https://gist.github.com/svavassori/3319ff9d7e16a8788665ca59a5a04889

def reconstruct_arrays(columns_types, dm0):
    # fixes array index by applying
    # "R" bitset to copy previous values
    # "Ø" bitset to set null values
    lenght = len(columns_types)
    for item in dm0:
        currentItem = item["C"]
        if "R" in item or "Ø" in item:
            copyBitset = item.get("R", 0)
            deleteBitSet = item.get("Ø", 0)
            for i in range(lenght):
                if is_bit_set_for_index(i, copyBitset):
                    currentItem.insert(i, prevItem[i])
                elif is_bit_set_for_index(i, deleteBitSet):
                    currentItem.insert(i, None)
        prevItem = currentItem

def is_bit_set_for_index(index, bitset):
    return (bitset >> index) & 1 == 1

# substitute indexes with actual values
def expand_values(columns_types, dm0, value_dicts):
    for (idx, col) in enumerate(columns_types):
        #print(col)
        if "DN" in col:
            for item in dm0:
                dataItem = item["C"]
                if isinstance(dataItem[idx], int):
                    valDict = value_dicts[col["DN"]]
                    dataItem[idx] = valDict[dataItem[idx]]
        elif col.get('T',0) == 7:
            for item in dm0:
                dataCell = item["C"][idx]
                if dataCell != None:
                    item["C"][idx] = str(datetime.datetime.fromtimestamp(dataCell/1000))
                    #print(dataCell)

def parse_data(input_json : dict) -> list:

    data = input_json["results"][0]["result"]["data"]
    dm0 = data["dsr"]["DS"][0]["PH"][0]["DM0"]
    columns_types = dm0[0]["S"]
    value_dicts = data["dsr"]["DS"][0].get("ValueDicts", {})
    reconstruct_arrays(columns_types, dm0)
    expand_values(columns_types, dm0, value_dicts)

    resp = []
    headers = []
    for c in columns_types:
        for col in data["descriptor"]["Select"]:
            if col["Value"] == c["N"]:
                if (col["Kind"] != 1):
                    headers.append((col["Name"].split(".")[1][:-1]))
                else:
                    headers.append(col["GroupKeys"][0]["Source"]["Property"])
    
    for item in dm0:
        resp.append(item['C'])
    
    return resp


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Our data and functions

# CELL ********************


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'application/json, text/plain, */*,',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd,',
    'ActivityId': str(uuid4()), 
    'RequestId': str(uuid4()), 
    'X-PowerBI-ResourceKey': 'f1ba5f74-559d-4602-a3a1-285a425a0de6',
    'Content-Type': 'application/json;charset=UTF-8',    
    'Origin': 'https://msit.powerbi.com',
    'DNT': '1',
    'Sec-GPC': '1',
    'Referer': 'https://msit.powerbi.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}

url = "https://df-msit-scus-api.analysis.windows.net/public/reports/querydata"

query = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"p","Entity":"Fabric KIs","Type":0},{"Name":"p1","Entity":"Products","Type":0}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Issue Publish Date"}},"Function":3},"Name":"Min(Power BI Known issues.Issue Publish Date)","NativeReferenceName":"Issue publish date"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Status"}},"Function":3},"Name":"Min(Power BI Known issues.Status)","NativeReferenceName":"Status"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Fixed Date"}},"Function":3},"Name":"Min(Power BI Known issues.Fixed Date)","NativeReferenceName":"Fixed date"},{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Issue ID"},"Name":"Fabric KIs.Issue ID","NativeReferenceName":"Issue ID"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Title"}},"Function":3},"Name":"Min(Fabric KIs.Title_)","NativeReferenceName":"Title"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"title_"}},"Function":3},"Name":"Min(Fabric KIs.Description)","NativeReferenceName":"title_"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"URL"}},"Function":3},"Name":"Min(Fabric KIs.URL)","NativeReferenceName":"First URL"},{"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "p"}},"Property": "ProductName"}},"Function": 3},"Name": "Min(Fabric KIs.ProductName)","NativeReferenceName": "ProductName"},{"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "p"}},"Property": "Index"}},"Function": 3},"Name": "Min(Fabric KIs.Index)","NativeReferenceName": "Index"}],"Where":[],"OrderBy":[{"Direction":2,"Expression":{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":"Issue Publish Date"}},"Function":3}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2,3,4,5,6,7,8]}]},"DataReduction":{"DataVolume":3,"Primary":{"Window":{"Count":500}}},"Version":1},"ExecutionMetricsKind":1}}]},"QueryId":"","ApplicationContext":{"DatasetId":"ac74e77f-0241-44a0-a6f4-4a4ef1c9e906","Sources":[{"ReportId":"d741d2e1-b4aa-4821-882b-70f5ea05e2f9","VisualId":"6ea949f7520808400249"}]}}],"cancelQueries":[],"modelId":4135743}


def query_data(url : str, headers : dict, query : str) -> tuple[str, str]:
    """
    """

    print(url)
    resp = requests.post(url, headers=headers, json=query)
    print(resp.status_code)
    return resp.text, resp.status_code


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Fetch the data

# CELL ********************

resp_body, status = query_data(url, headers, query)

if (status != 200):
    print(f"Error fetching data - {status} : {resp_body}")
    exit(-1)

# the response json is broken beyond comprehension, single&double quotes, newlines, etc
# repair it first
input_json = json.loads(json_repair.repair_json(resp_body))

d = parse_data(input_json) # TODO: save the raw file if parsing fails

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Save it to a table

# CELL ********************

from pyspark.sql.functions import current_date, current_timestamp, lit

schema = spark.sql("""
    SELECT 1 AS Issue_ID, current_date() AS Issue_Published_Date, 
        "Status" AS Status, current_date() AS Fixed_Date, "Title" AS Title, "Description" AS Description,
        "URL" AS Url, "Product Name" AS Product_Name, 1 AS Index, current_timestamp() AS Fetch_Timestamp
    LIMIT 0;
    """)
df = (spark.createDataFrame(d)
    .withColumn("Fetch_Timestamp", lit(current_timestamp()))
)
data = schema.union(df) # TODO: union loses the schema

data.write.mode('append').saveAsTable('fabric_known_issues_raw')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Detect changes

# CELL ********************

# MAGIC %%sql 
# MAGIC 
# MAGIC CREATE TABLE IF NOT EXISTS fabric_known_issues_changes AS 
# MAGIC     SELECT *, 'A' AS Change, CURRENT_DATE() AS Change_Date 
# MAGIC     FROM fabric_known_issues_raw 
# MAGIC     LIMIT 0;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC CREATE OR REPLACE TEMPORARY VIEW today AS 
# MAGIC     SELECT *
# MAGIC     FROM fabric_known_issues_raw AS r
# MAGIC     WHERE r.Fetch_Timestamp >= current_date()
# MAGIC ;
# MAGIC 
# MAGIC CREATE OR REPLACE TEMPORARY VIEW yesterday AS (
# MAGIC     SELECT *
# MAGIC     FROM fabric_known_issues_raw AS r
# MAGIC     WHERE r.Fetch_Timestamp >= date_add(current_date(), -7) AND r.fetch_timestamp < current_date()
# MAGIC ) ;
# MAGIC 
# MAGIC -- New rows
# MAGIC INSERT INTO fabric_known_issues_changes
# MAGIC     SELECT *, 'NEW' AS Change, CURRENT_DATE() as Change_Date
# MAGIC     FROM today
# MAGIC     WHERE today.Issue_ID NOT IN (SELECT Issue_ID FROM yesterday WHERE Issue_ID IS NOT NULL);
# MAGIC 
# MAGIC 
# MAGIC -- Deleted rows
# MAGIC INSERT INTO fabric_known_issues_changes
# MAGIC     SELECT *, 'DELETED' AS Change, CURRENT_DATE() as Change_Date
# MAGIC     FROM yesterday 
# MAGIC     WHERE yesterday.Issue_ID NOT IN (SELECT Issue_ID FROM today WHERE Issue_ID IS NOT NULL);
# MAGIC 
# MAGIC -- Changed rows
# MAGIC INSERT INTO fabric_known_issues_changes
# MAGIC     SELECT *, 'CHANGED' AS CHANGE, CURRENT_DATE() as Change_Date
# MAGIC     FROM today
# MAGIC     LEFT ANTI JOIN fabric_known_issues_changes -- prevent NEW changes to come up again
# MAGIC         ON today.Issue_ID = fabric_known_issues_changes.Issue_ID 
# MAGIC         AND fabric_known_issues_changes.Change_Date = CURRENT_DATE()
# MAGIC     LEFT ANTI JOIN yesterday 
# MAGIC         ON today.Issue_ID = yesterday.Issue_ID 
# MAGIC         AND today.Issue_Published_Date = yesterday.Issue_Published_Date 
# MAGIC         AND today.Status = yesterday.Status 
# MAGIC         --AND today.Fixed_Date = yesterday.Fixed_Date -- Nulls cause always to show row as if it has changed, status should pick the change anyway
# MAGIC         AND today.Title = yesterday.Title 
# MAGIC         AND today.Description = yesterday.Description 
# MAGIC         AND today.Url = yesterday.Url 
# MAGIC         AND today.Product_Name = yesterday.Product_Name 
# MAGIC     WHERE today.Issue_ID IS NOT NULL
# MAGIC         AND today.Url IS NOT NULL


# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Send notifications

# CELL ********************

def detect_changes_and_notify(known_issues_or_roadmap : str):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ki_change_count = (spark.table(f"fabric_{known_issues_or_roadmap}_changes")
        .where(f"change_date == '{today}'")
    ).count()

    if (ki_change_count > 0):
        notebookutils.fs.put(f"Files/trigger_blobs/{known_issues_or_roadmap}/{today}", '')
        print("Wrote triggering blob")

detect_changes_and_notify('known_issues')
detect_changes_and_notify('roadmap')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
