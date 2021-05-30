import csv

# 22 was when there were most blocks in early domains
date = '2021-5-22'

# paths
mullvad_path = "data/stage3/csvs/{}/{}-mullvad.csv".format(date, date)
block_analysis = 'analysis/stage3/block-analysis/{}-block-analysis.csv'.format(date)
stage4_path = 'domains/{}-stage4domains.csv'.format(date)

mullvad_data = {}
with open(mullvad_path, mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        id = row['ID']
        if id != '':
            mullvad_data[id] = {
                'Domain': row['Request Domain'],
                'Time': row['Time'],
                'Duration (ms)': row['Duration (ms)'],
                'Attempts': row['Attempts'],
                'Response Domain': row['Response Domain'],
                'IP Address': row['IP Address'],
                'HTTP Status Code': row['HTTP Status Code'],
                'Error': row['Error']
            }

block_data = {}
with open(block_analysis, mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        id = row['ID']
        if id != '':
            block_data[id] = {
                'Domain': row['Domain'],
                'PHash Difference': row['PHash Difference'],
                'Manual Check': row['Manual Check'],
                'Blocked': row['Blocked'],
                'Type of Block': row['Type of Block']
            }

added = 0

for i in range(1, 3001):
    if added >= 1000:
        break
    if mullvad_data['{}'.format(i)]['HTTP Status Code'] == '200' and block_data['{}'.format(i)]['Blocked'] == 'no':
        with open (stage4_path,'a') as csv_file:                            
            csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=['ID', 'Domain'])
            data = {
                'ID': i,
                'Domain': block_data['{}'.format(i)]['Domain'].split('//')[1]
            }
            csv_writer.writerow(data)
        added += 1
