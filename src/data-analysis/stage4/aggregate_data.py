import csv

date = '2021-6-11'

# paths
mullvad_path = "data/stage4/csvs/{}/{}-mullvad.csv".format(date, date)
control_path = "data/stage4/csvs/{}/{}-control.csv".format(date, date)
aggragated_path = "analysis/stage4/aggregated/{}-aggregated.csv".format(date)
mullvad_analysis = "analysis/stage4/individual/mullvad-analysis.csv"
control_analysis = "analysis/stage4/individual/control-analysis.csv"
phash_path = "analysis/stage4/screenshots/{}-phash.csv".format(date)


# ID,Subpage ID,Time,Duration (ms),Attempts,Request Domain,Response Domain,IP Address,HTTP Status Code,Error

def get_data(csv_path):
    data_dict = {}
    with open(csv_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            id = row['ID']
            if id != '':
                data_dict[id] = {
                    'Subpage ID': row['Subpage ID'],
                    'Domain': row['Request Domain'],
                    'Time': row['Time'],
                    'Duration (ms)': row['Duration (ms)'],
                    'Attempts': row['Attempts'],
                    'Response Domain': row['Response Domain'],
                    'IP Address': row['IP Address'],
                    'HTTP Status Code': row['HTTP Status Code'],
                    'Error': row['Error']
                }
    return data_dict


def get_phash(csv_path):
    data_dict = {}
    with open(csv_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            image = row['Image']
            if image != '':
                id = image.split("-")[3]
                data_dict[id] = {
                    'Image': image,
                    'Mullvad Hash': row['Mullvad Hash'],
                    'Control Hash': row['Control Hash'],
                    'Difference': row['Difference']
                }
    return data_dict


def individual_data(read_data, write_data, connection):
    # initialise data dict
    data = {
        'Date': date,
        'Connection': connection,
        '2xx': 0,
        'Non-2xx': 0,
        'Timeouts': 0,
        'Errors': 0
    }

    # add data
    with open(read_data, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            code = int(row['HTTP Status Code'])
            error = row['Error']
            if code > 199 and code < 300:
                data['2xx'] += 1
            elif code > 0:
                data['Non-2xx'] += 1
            else:
                error_name = error.split()[0]
                if 'Navigation' in error_name:
                    data['Timeouts'] += 1
                else:
                    data['Errors'] += 1
    
    # write data
    with open (write_data,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(data.keys()))
        # csv_writer.writeheader()
        csv_writer.writerow(data)


def aggregate_data():
    mullvad_data = get_data(mullvad_path)
    control_data = get_data(control_path)
    phash_data = get_phash(phash_path)

    headers = [
        'ID',
        'Subpage ID',
        'Domain',
        'Mullvad Response Domain',
        'Control Response Domain',
        'Mullvad Status Code',
        'Control Status Code',
        'Mullvad Error',
        'Control Error',
        'PHash Difference',
    ]

    with open(aggragated_path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        for id, data in mullvad_data.items():
            if id in phash_data:
                phash = phash_data[id]['Difference']
            else:
                phash = 'NA'
            data = {
                'ID': id,
                'Subpage ID': data['Subpage ID'],
                'Domain': data['Domain'],
                'Mullvad Response Domain': data['Response Domain'],
                'Control Response Domain': control_data[id]['Response Domain'],
                'Mullvad Status Code': data['HTTP Status Code'],
                'Control Status Code': control_data[id]['HTTP Status Code'],
                'Mullvad Error': data['Error'],
                'Control Error': control_data[id]['Error'],
                'PHash Difference': phash
            }
            writer.writerow(data)


aggregate_data()
individual_data(mullvad_path, mullvad_analysis, 'Mullvad VPN')
individual_data(control_path, control_analysis, 'Control')
