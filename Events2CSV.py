
# coding: utf-8

# In[17]:

import requests
import json
import pandas as pd
import datetime


# In[18]:

# Getting the match timeline as a JSON. G2 vs UOL game 1
r = requests.get(url="https://acs.leagueoflegends.com/v1/stats/game/TRLH3/1001970008/timeline?gameHash=7aa4a96045584cfe")
response = json.loads(r.content)


# In[19]:

# Creating vars with the info we need (wards)

## Getting the frames
frames = response["frames"]

## Mapping all events into a list
events = list(map(lambda y: y["events"], frames)) 

## Mapping the participant frames into a list
participants = list(map(lambda y: y["participantFrames"], frames)) 

## Grouping al vision related events into a single list
vision_events = list(map(lambda x: list(filter(lambda y: (y["type"] == "WARD_PLACED" or y["type"] == "WARD_KILL"), x)), events))    


# In[20]:

# Merging both vision events with the info of the participant of the event

## Creating a list that we will poblate later with all the data
result = []

##Iterating through events frames with the index information
for index, events in enumerate(vision_events):
    ### For every event in that event frame do:
    for event in events:
        #### Check whether if is a placement or a kill to get the participant ID to get the participant info
        if event["type"] == "WARD_PLACED": pid = event["creatorId"]
        else: pid = event["killerId"]
        #### Getting the participant info
        participant = participants[index].get(str(pid))
        #### Merging that info
        merged = dict(list(event.items()) + list(participant.items()))
        #### Adding the frame number
        merged["nFrame"] = index
        #### Appending the data as a new item to the list previously created
        result.append(merged)

## Transforming the list into a Pandas DataFrame 
resultdf = pd.DataFrame.from_dict(result)


# In[21]:

# Transforming position field into two new rows
resultdf['x_pos'] = resultdf['position'].apply(lambda d: d['x'])
resultdf['y_pos'] = resultdf['position'].apply(lambda d: d['y'])

# Transforming timestamp into readable time as minutes and seconds (mm:ss) format
resultdf['timestamp'] = resultdf['timestamp'].apply(lambda d: '{:02d}:{:02d}'.format(int(divmod(d/1000, 60)[0]), int(divmod(d/1000, 60)[1])))


# In[22]:

# Some corrections over the data

## Removing the creatorId and killerId column since the data is redundant because we already have the ID in the participantId field
del resultdf["creatorId"]
del resultdf["killerId"]

## Removing as well the position since we previously added two new columns with that data
del resultdf["position"]


# In[23]:

# And finally we export the dataframe into a CSV
resultdf.to_csv("vision_events.csv")


# In[ ]:



