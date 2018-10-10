import csv
import requests
import json
from random import shuffle
import pandas as pd
import progressbar


file_endpt = 'https://api.gdc.cancer.gov/files/%s?fields=file_id,cases.samples.tissue_type,cases.project.project_id'

download_dict = {"TCGA-LUAD":[], "TCGA-LUSC":[]}
max_files = 50

file_list = []

with open("manifest.txt") as f:
    first_row = True
    for row in csv.reader(f, delimiter='\t'):
        if first_row:
            first_row = False
            continue
        file_id = row[0]
        file_list.append(file_id)

shuffle(file_list)

df = pd.DataFrame()

counter = 0

def download_file(url, path, cancer_type):
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        bar = progressbar.ProgressBar(prefix=path + "(%s)" % cancer_type)
        total_length = int(r.headers.get('content-length'))
        for chunk in bar(r.iter_content(chunk_size=1024), max_value=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()

for file_id in file_list:
    continue_download = False
    for value in download_dict.values():
        if len(value) < max_files:
            continue_download = True
    
    if continue_download:
        response = requests.get(file_endpt % file_id)
        data = response.json()
        counter += 1
        project_id = data['data']['cases'][0]['project']['project_id']
        if project_id not in download_dict:
                download_dict[project_id] = []
                
        if len(download_dict[project_id]) < max_files:
            download_dict[project_id].append(file_id)
    else:
        break
        
for key, value in download_dict.items():
    for file in value:
        download_file('https://api.gdc.cancer.gov/data/' + file, file+ ".tar.gz", key)
