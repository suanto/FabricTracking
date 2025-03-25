# Description
This is a repo for tracking and getting alerts when [Microsoft Fabric]() [Roadmap]() and [Known Issues]() are modified. Both of the lists are updated from time to time but Microsoft doesn't provide notification of the changes and there is no history of the lists, so staying up-to-date is a laborious process.

# How it works
It scrapes the webpage of the roadmap, parses the data using a Panda's read_table. The known issues list on the webpage is an embedded Power BI report. The Power BI report dataset is read from the API, parsed, and saved.

All the data is stored from every run to *_raw-tables, changes are detected and written *_changes-tables. If there are any changes row, a trigger blob is written to lh_fabric_items-lakehouse. An Activator can be configured to listen to the trigger blob location and an Activator rule can do something based on the trigger, for example send an email to Teams message.

**Note about the Power BI data parsing**

The Power BI report fetching and parsing code is fairly complex. Most is done by [svavassori](https://gist.github.com/svavassori/3319ff9d7e16a8788665ca59a5a04889), kudos to the author. The code is not documented as well as it should. It basically works as follows:
* Data is fetched from the Power BI API using some magic values, such as X-PowerBI-ResourceKey, DatasetID, ReportID, and ModelID. The query is hard coded as we need only one query here.
* Power BI API response data is packed according to their custom scheme, resembling a bit of the VertiPaq. In essence, it uses a variant of RLE, meaning that if value is not present, the previous value is used with a special code for a missing value.

# Install
## Fabric Git sync
* Sync the repo to a Fabric workspace.
* Change the notebook default lakehouse to 'ln_fabric_data'

## Manually create objects
After the sync has completed, create an Activator (act_fabric_events), and Activator rules.

* Create an Activator
    * Change name to act_fabric_events
* Get Data
    * Select 'Get Data'
    * Fabric events > OneLake Events
    * Event types: Only Microsoft.Fabric.OneLake.FileCreated
    * Add a OneLake Source
        * Select lh_fabric_data
        * Select Files/trigger_blobs
        * Approve/OK
    * Set Filter (this option might require scrolling the page)
        * Field: 'data.api', Operation: 'String begins with', Value: CreateFile
    * Next & Connect
* Create Rules
    * Roadmap
        * New Rule
        * Condition 1
            * Operation: Contains, Column: __subject, Value: 'roadmap', Default Type: None
        * Action 
            * Email
                * Subject: 'Fabric Roadmap change detected'
                * Headline: 'Fabric Roadmap change detected'
                * Message: ​___subject System.IngestionTime
        * Change the name to 'Roadmap_changed'
        * Save and Update

    * Known Issues
        * New Rule
        * Condition 1
            * Operation: Contains, Column: __subject, Value: 'known' (this should be known_issues, as the folder name but it's not allowed), Default Type: None
        * Action 
            * Email
                * Subject: 'Fabric Known issues change detected'
                * Headline: 'Fabric Known issues change detected'
                * Message: ​___subject System.IngestionTime
        * Change the name to 'Known_issues_changed'
        * Save and Update

## Schedule the notebooks
Schedule the fetch and change detection notebooks (nb_fetch_fabric_roadmap, nb_fetch_fabric_known_issues) to be run once a day. If they are scheduled to run less often, change detection logic needs to be updated.

# Data and Item Catalog
## nb_fetch_fabric_roadmap
Fetch data, detect changes, write trigger blobs for roadmap.

## nb_fetch_fabric_known_issues
Fetch data, detect changes, write trigger blobs for the known issues.

## nb_browse_issues_and_roadmap
For ad-hoc browsing.

## env_no_caching
nb_fetch_fabric_known_issues has to use this env as it contains the json_repair lib. 

The env also disables the Fabric Intelligent Caching. Makes no big difference it is disabled as it is not needed when fetching and writing data.

## lh_fabric_data
### Tables
|Table|Description|
|--|--|
|fabric_roadmap_raw|Fabric Roadmap items in raw format. Stored from every run.|
|fabric_roadmap_changes|Changed rows of the Fabric Roadmap. Change is compared to previous day.|
|fabric_known_issues_raw|Fabric Known Issues in raw format. Stored from every run.|
|fabric_known_issues_changes|Changed rows of Known Issues. Change is compared to previous day.|

### fabric_roadmap_raw

The table has no natural primary key. Change detection treats 'title', 'deadline', 'fabric_area' combination is a unique key.

Columns
* title, parsed from the webpage
* deadline, parsed from the webpage
* fabric_area, parsed from the webpage
* fetch_timestamp, timestamp of the fetch

### fabric_roadmap_changes
Columns
* All the columns of fabric_roadmap_raw and
* Change, the type of the change (NEW, CHANGED, DELETED)
* Change_date, the date when change was detected.

### fabric_known_issues_raw
* Issue_ID, primary key, parsed from the dataet.
* Issue_Published_Date, parsed from the dataset.
* Status, parsed from the dataset.
* Fixed_Date, parsed from the dataset.
* Title, parsed from the dataset.
* Description, parsed from the dataset.
* Url, parsed from the dataset.
* Product_Name, parsed from the dataset.
* Index,  parsed from the dataset.
* Fetch_Timestamp, timestamp of the fetch.

### fabric_known_issues_changed
Columns
* All the columns of fabric_known_issues_raw and
* Change, the type of the change (NEW, CHANGED, DELETED)
* Change_date, the date when change was detected.


### Files
* Files
    * trigger_blobs
        * roadmap
        * known_issues