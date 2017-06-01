import csv
import json
import sys
import math
import numpy
from sklearn.ensemble import RandomForestClassifier
TMAX_INDEX = 11
TMIN_INDEX = 12
MONTHS = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
INCREMENT = 20
DAYS_AHEAD = 7
#['STATION', 'STATION_NAME', 'ELEVATION', 'LATITUDE', 'LONGITUDE', 'DATE', 'MDPR', 'DAPR', 'PRCP', 'SNWD', 'SNOW', 'TMAX', 'TMIN', 'TOBS', 'WT01', 'WT06', 'WT05', 'WT11', 'WT04', 'WT03']

#List of dicts with keys
 #2-dimensional list (CSV)
def CSV_to_2DList(inputFile):
    with open(inputFile) as csvfile:
        data = list(csv.reader(csvfile))
        csvfile.close()
        return data
def _2DList_to_DICT(data):
    parsed_data = []
    fields = data[0]
    for rowindex, row in enumerate(data):
        rowDict = {}
        for index, element in enumerate(row):
            if(element=='-9999'):continue
            rowDict[fields[index]] = element
        parsed_data.insert(0, rowDict)
    return parsed_data
def DICT_to_JSON(outFile,dict):
    with open(outFile, 'w') as outfile:
            json.dump(dict, outfile, indent=4)
            outfile.close()

raw_data = CSV_to_2DList('974946.csv')
print(raw_data[0])
DICT_to_JSON('data.json',_2DList_to_DICT(raw_data))

clean_data = []
for row in raw_data: #Remove days with no recorded temps
    if row[TMAX_INDEX] != '-9999' and row[TMIN_INDEX] != '-9999':
        clean_data.append(row)

DICT_to_JSON('cleandata.json', _2DList_to_DICT(clean_data))

def prepare_data(data):
    weekly_data = []
    predicted_day = []
    threshhold = max(INCREMENT,DAYS_AHEAD)
    for i in range(1, len(data) - threshhold):
        currweek = []
        
        for j in range(i,i+INCREMENT+1):
            currweek.append(int(data[j][TMIN_INDEX]))
        predicted_day.append(int(data[i + DAYS_AHEAD][TMIN_INDEX]))
        weekly_data.append(currweek)
    return([weekly_data, predicted_day])
mydata = prepare_data(clean_data)
dataset = mydata[0]
classifiers = mydata[1]
#X = array of arrays for data
#Y = array for classification for each array of data
#X=[[cyan,ocean],[jade,emerald],[obsidian,onyx]]
#Y=[blue,green,black]
clf = RandomForestClassifier(n_jobs=2)
clf.fit(dataset,classifiers)
print('Last recorded week: '+str(dataset[len(dataset) - 1]))
lasweek= [44, 47, 49, 39, 36, 36, 43,
     41, 44, 40, 42, 40, 53, 66, 64, 51, 42, 49, 52,55 ,55]
prediction = clf.predict([lasweek])
print(prediction)

raw_dynamic_dataset = []
lastval = 0
for index,day in enumerate(clean_data):
    date = day[5]
    year = date[:4]
    if(year=='2001'):
        raw_dynamic_dataset.append(day)
        lastval=index

predictions = [['Date','Predicted','Actual','Error']]
dynamic_clf = RandomForestClassifier(n_jobs=2)
for i in range(lastval,len(clean_data)-11,10):
    raw_dynamic_dataset.extend(clean_data[i:i+10])
    dynamic_dataset=prepare_data(raw_dynamic_dataset)
    dynamic_clf.fit(dynamic_dataset[0], dynamic_dataset[1])
    predicted_val=dynamic_clf.predict([dynamic_dataset[0][len(dynamic_dataset[0])-1]])[0]
    print('Generated prediction for ' + str(i) + ' of ' + str(len(clean_data)))
    predictions.append([clean_data[i+11][5],(predicted_val), int(clean_data[i + 11][TMIN_INDEX])])

for index,val in enumerate(predictions):
    if(index==0):continue
    print(val)
    val.append(abs(val[1]-val[2]))

with open('accuracies.csv', 'w') as myfile:
    wr = csv.writer(myfile, lineterminator='\n')
    for row in predictions:
        wr.writerow(row)

    
