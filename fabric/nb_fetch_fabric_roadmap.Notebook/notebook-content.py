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

# ## Fetch Fabric roadmap data and save it to a table

# CELL ********************

import pandas as pd
import pyspark.sql.functions as F

# List from https://learn.microsoft.com/en-us/fabric/release-plan/overview
roadmap_pages = {
    "Admin and governance" : "https://learn.microsoft.com/en-us/fabric/release-plan/admin-governance",
    "Onelake": "https://learn.microsoft.com/en-us/fabric/release-plan/onelake",
    "Developer experiences": "https://learn.microsoft.com/en-us/fabric/release-plan/shared-experiences",
    "Data Warehouse" : "https://learn.microsoft.com/en-us/fabric/release-plan/data-warehouse",
    "Data Engineering" : "https://learn.microsoft.com/en-us/fabric/release-plan/data-engineering",
    "Data Science" : "https://learn.microsoft.com/en-us/fabric/release-plan/data-science",
    "RealTime Intelligence" : "https://learn.microsoft.com/en-us/fabric/release-plan/real-time-intelligence",
    "Data Factory" : "https://learn.microsoft.com/en-us/fabric/release-plan/data-factory",
    "Data Activator" : "https://learn.microsoft.com/en-us/fabric/release-plan/data-activator",
    "Power BI" : "https://learn.microsoft.com/en-us/fabric/release-plan/powerbi"
}

# An empty dataframe with correct headings and schema
df = spark.sql("SELECT '' AS title, '' AS deadline, '' AS fabric_area, current_timestamp() AS fetch_timestamp LIMIT 0")

# Fetch and parse data
for area, url in roadmap_pages.items():
    try:
        df_table = pd.read_html(url)[0]
        if(len(df_table.index) > 0):
            df = df.union(spark.createDataFrame(df_table)
                .withColumn("fabric_area", F.lit(area))
                .withColumn("fetch_timestamp", F.current_timestamp())
            )
    except:
        print("Error reading webpage")

df.write.mode("append").saveAsTable("fabric_roadmap_raw")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Table for changes
# 
# Same schema as the raw data plus change type and detection date.

# CELL ********************

# MAGIC %%sql
# MAGIC CREATE TABLE IF NOT EXISTS fabric_roadmap_changes
# MAGIC AS SELECT *, 'A' AS Change, CURRENT_DATE() AS Change_Date FROM fabric_roadmap_raw LIMIT 0;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Detect changes and save them to "fabric_roadmap_changes"-table
# 
# As we don't have a proper key, we need to combine title, fabric_area, and deadline

# CELL ********************

# MAGIC %%sql
# MAGIC CREATE OR REPLACE TEMPORARY VIEW today AS 
# MAGIC     SELECT *
# MAGIC     FROM fabric_roadmap_raw AS r
# MAGIC     WHERE r.fetch_timestamp > current_date()
# MAGIC ;
# MAGIC 
# MAGIC CREATE OR REPLACE TEMPORARY VIEW yesterday AS (
# MAGIC     SELECT *
# MAGIC     FROM fabric_roadmap_raw AS r
# MAGIC     WHERE r.fetch_timestamp < current_date()
# MAGIC     AND r.fetch_timestamp >= date_add(current_date(), -1)
# MAGIC ) ;
# MAGIC 
# MAGIC -- New rows
# MAGIC INSERT INTO fabric_roadmap_changes
# MAGIC SELECT *, 'NEW' AS Change, CURRENT_DATE() as Change_Date
# MAGIC FROM today LEFT ANTI JOIN yesterday ON today.title = yesterday.title
# MAGIC AND today.fabric_area = yesterday.fabric_area 
# MAGIC AND today.deadline = yesterday.deadline;
# MAGIC 
# MAGIC 
# MAGIC -- Deleted rows
# MAGIC INSERT INTO fabric_roadmap_changes
# MAGIC SELECT *, 'DELETED' AS Change, CURRENT_DATE() as Change_Date
# MAGIC FROM yesterday LEFT ANTI JOIN today ON today.title = yesterday.title
# MAGIC AND today.fabric_area = yesterday.fabric_area 
# MAGIC AND today.deadline = yesterday.deadline;
# MAGIC 
# MAGIC -- Changed rows
# MAGIC INSERT INTO fabric_roadmap_changes
# MAGIC SELECT *, 'CHANGED' AS CHANGE, CURRENT_DATE() as Change_Date 
# MAGIC FROM today
# MAGIC LEFT ANTI JOIN fabric_roadmap_changes ON today.title = fabric_roadmap_changes.title -- to take away today's NEW rows
# MAGIC     AND today.fabric_area = fabric_roadmap_changes.fabric_area 
# MAGIC     AND fabric_roadmap_changes.Change_Date = CURRENT_DATE()
# MAGIC LEFT ANTI JOIN yesterday 
# MAGIC     ON today.title = yesterday.title 
# MAGIC     AND today.deadline = yesterday.deadline 
# MAGIC     AND today.fabric_area = yesterday.fabric_area 

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
