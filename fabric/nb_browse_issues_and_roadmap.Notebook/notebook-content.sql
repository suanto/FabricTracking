-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "synapse_pyspark"
-- META   },
-- META   "dependencies": {
-- META     "lakehouse": {
-- META       "default_lakehouse": "5b89a532-a8cf-4ce7-a4e4-b655b86d8ce0",
-- META       "default_lakehouse_name": "lh_fabric_data",
-- META       "default_lakehouse_workspace_id": "f430fe2a-5ad8-433a-a3d0-686ad70831be"
-- META     }
-- META   }
-- META }

-- MARKDOWN ********************

-- # Ad-hoc browsing notebook
-- 
-- This notebook contains ad-hoc queries to browse Fabric Roadma and Known Issues

-- MARKDOWN ********************

-- ## Fabric Known Issue Changes

-- CELL ********************

SELECT *
FROM fabric_known_issues_changes
ORDER BY Change_Date DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- MARKDOWN ********************

-- ## Compare Known Issue to yesterday

-- CELL ********************

WITH latest_changes AS (
SELECT *
FROM fabric_known_issues_changes
WHERE Change_Date = (SELECT MAX(Change_Date) FROM fabric_known_issues_changes)
)

SELECT c.issue_id, r.issue_id, c.issue_published_date, r.issue_published_date, c.status, r.status, c.fixed_date, r.fixed_date, c.title, r.title, c.description, r.description, c.url, r.url, c.product_name, r.product_name, c.index, r.index
FROM latest_changes AS c
LEFT JOIN fabric_known_issues_raw AS r ON c.Issue_ID = r.Issue_ID AND date_add(c.Change_Date, -1) = to_date(r.Fetch_Timestamp)
ORDER BY r.Issue_id

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- MARKDOWN ********************

-- ## Latest raw list of known issues

-- CELL ********************

SELECT *
FROM fabric_known_issues_raw
WHERE Fetch_Timestamp = (SELECT MAX(Fetch_Timestamp) FROM fabric_known_issues_raw)
ORDER BY Issue_ID DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- MARKDOWN ********************

-- ## Fabric Roadmap Changes

-- CELL ********************

SELECT *
FROM fabric_roadmap_changes
ORDER BY Change_Date DESC, title ASC, change DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- MARKDOWN ********************

-- ## Write a test blob to a trigger store

-- CELL ********************

-- MAGIC %%pyspark
-- MAGIC notebookutils.fs.put('Files/trigger_blobs/roadmap/testblob_can_be_removed', '')


-- METADATA ********************

-- META {
-- META   "language": "python",
-- META   "language_group": "synapse_pyspark"
-- META }

-- MARKDOWN ********************

-- ## Test alerting

-- CELL ********************

-- MAGIC %%pyspark
-- MAGIC import uuid
-- MAGIC uuid = uuid.uuid4()
-- MAGIC 
-- MAGIC notebookutils.fs.put(f"Files/trigger_blobs/roadmap/roadmap_alert_test_can_be_removed_{uuid}", '')
-- MAGIC notebookutils.fs.put(f"Files/trigger_blobs/known_issues/known_issues_alert_test_can_be_removed_{uuid}", '')

-- METADATA ********************

-- META {
-- META   "language": "python",
-- META   "language_group": "synapse_pyspark"
-- META }
