# Description
This is a repo for tracking and getting alerts when [Microsoft Fabric]() [Roadmap]() and [Known Issues]() are modified. Both of the lists are updated from time to time but Microsoft doesn't provide notification of the changes and there is no history of the lists, so staying up-to-date is a laborious process.

The notebooks in this workspace can be configured to fetch the Fabric roadmap and known issues list daily, detect changes, and alert using email or Teams.

# How it works
It scrapes the webpage of the roadmap, parses the data using a Panda's read_table. The known issues list on the webpage is an embedded Power BI report. The Power BI report dataset is read from the API, parsed, and saved.

All the data is stored from every run to *_raw-tables, changes are detected and written *_changes-tables. If there are any changes row, a trigger blob is written to lh_fabric_items-lakehouse. An Activator can be configured to listen to the trigger blob location and an Activator rule can do something based on the trigger, for example send an email to Teams message.

## How to view the changes?

When you get a notification, how to view the changes? 

Open up the nb_browse_issues_and_roadmap-notebook and run wanted cells, for example 'Fabric Known Issue Changes' or 'Fabric Roadmap Changes'.

## Note about the Power BI data parsing

The Power BI report fetching and parsing code is fairly complex. Most is done by [svavassori](https://gist.github.com/svavassori/3319ff9d7e16a8788665ca59a5a04889), kudos to the author. The code is not documented as well as it should. It basically works as follows:
* Data is fetched from the Power BI API using some magic values, such as X-PowerBI-ResourceKey, DatasetID, ReportID, and ModelID. The query is hard coded as we need only one query here.
* Power BI API response data is packed according to their custom scheme, resembling a bit of the VertiPaq. In essence, it uses a variant of RLE, meaning that if value is not present, the previous value is used with a special code for a missing value.

# Install
## Fabric Git sync
1. Sync the repo to a Fabric workspace.
2. Change the notebook default lakehouse to 'ln_fabric_data' for all notebooks.

    ![](/assets/ws.png)

    *The workspace after sync.*

## Manually create objects
After the sync has completed, create an Activator ('act_fabric_events'), and Activator rules.

### Create an Activator
1. Get Data
    1. Select 'Get Data'
    2. Select Fabric events > OneLake Events
    
        ![](/assets/OneLake_events.png)

    
    3. Event types: Only Microsoft.Fabric.OneLake.FileCreated
    4. Add a OneLake Source
        1. Select lh_fabric_data
        2. Select Files/trigger_blobs
            
            ![](/assets/choose_folder.png)

        3. Approve/OK


    5. Set Filter (NOTE: this option might require scrolling the page)
        1. Field: 'data.api', Operation: 'String contains', Value: CreateFile

            ![](/assets/connect_details.png) 
    6. Next & Connect

2. Change the names
    1. Change the Activator name to 'act_fabric_events'
    
        ![](/assets/rename_activator.png)
    
    2. Change the stream name to 'Fabric event triggers'
    
        ![](/assets/rename_stream.png)

### Create Activator Rules
1. Roadmap
    1. Select 'New Rule'
    2. Condition 1
    3. Operation: 'Textstate/Contains', Column: __subject, Value: 'roadmap', Default Type: None
        * *NOTE: if there is no column field, you need to write a blob to the trigger store location, in order to get Fabric to see schema. You can do it by opening the nb_browse_issues_and_roadmap-notebook and executing the cell under the heading 'Write a test blob to a trigger store'.*

            ![](/assets/write_test_blob.png)
                
    4. Action 
        1. Email
        2. Subject: 'Fabric Roadmap change detected'
        3. Headline: 'Fabric Roadmap change detected'
        4. Message: ​___subject System.IngestionTime
            * *NOTE: you can add these fields by writing an '@' sign and selecting the field.*
        5. Change the name to 'Roadmap_changed'
        
            ![](/assets/rename_rule.png)
        
        6. Save and Start
            
            ![](/assets/rule.png)

2. Known Issues
    1. New Rule
    2. Condition 1
    3. Operation: Contains, Column: __subject, Value: 'known' (this should be known_issues, as the folder name but it's not allowed), Default Type: None
    4. Action 
        1. Email
        2. Subject: 'Fabric Known issues change detected'
        3. Headline: 'Fabric Known issues change detected'
        4. Message: ​___subject System.IngestionTime
        5. Change the name to 'Known_issues_changed'
        6. Save and Start
3. Test triggering
    
    1. Open the nb_browse_issues_and_roadmap-notebook and execute a cell with heading 'Test alerting'.
      
        ![](/assets/test_alerting.png)
        
    2. Confirm the email was sent from the Activator
        * *NOTE: It may take a long time (up to 30 min.) that Activator actually starts to send alerts*

        ![](/assets/alert_works.png)
    
    3. Confirm you received the email

## Finished Workspace

![](/assets/ws_ready.png)

*Workspace with all resources.*

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