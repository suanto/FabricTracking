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

-- CELL ********************

SELECT Fetch_Timestamp, count(*)
FROM fabric_known_issues_raw
GROUP BY Fetch_Timestamp
ORDER BY Fetch_Timestamp DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

SELECT *
FROM fabric_known_issues_changes
ORDER BY Change_Date DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

CREATE OR REPLACE TEMPORARY VIEW latest_changes AS
SELECT *
FROM fabric_known_issues_changes
WHERE Change_Date = (SELECT MAX(Change_Date) FROM fabric_known_issues_changes)
;

SELECT c.issue_id, r.issue_id, c.issue_published_date, r.issue_published_date, c.status, r.status, c.fixed_date, r.fixed_date, c.title, r.title, c.description, r.description, c.url, r.url, c.product_name, r.product_name, c.index, r.index
FROM latest_changes AS c
LEFT JOIN fabric_known_issues_raw AS r ON c.Issue_ID = r.Issue_ID AND date_add(c.Change_Date, -1) = to_date(r.Fetch_Timestamp)
ORDER BY r.Issue_id

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

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

-- CELL ********************

SELECT Fetch_Timestamp, count(*)
FROM fabric_roadmap_raw
GROUP BY Fetch_Timestamp
ORDER BY Fetch_Timestamp DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

SELECT *
FROM fabric_roadmap_changes
ORDER BY Change_Date DESC, title ASC, change DESC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

SELECT DISTINCT fetch_timestamp
FROM fabric_roadmap_raw;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

SELECT *
FROM fabric_roadmap_raw
WHERE Fetch_Timestamp > '2025-03-08'
    AND Fetch_Timestamp < '2025-03-09'
ORDER BY title ASC

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

CREATE OR REPLACE TEMPORARY VIEW current_roadmap AS
    SELECT *
    FROM fabric_roadmap_raw
    WHERE Fetch_Timestamp = (SELECT MAX(Fetch_Timestamp) FROM fabric_roadmap_raw);

SELECT COUNT(*) AS count, fabric_area
FROM current_roadmap
WHERE deadline LIKE 'Q4%'
GROUP BY fabric_area
ORDER BY fabric_area

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
