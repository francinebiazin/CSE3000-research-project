import csv

mullvad_path = "data/csvs/2021-05-14/2021-5-14-mullvad.csv"
control_path = "data/csvs/2021-05-14/2021-5-14-control.csv"


def get_data(csv_path):
    data_dict = {}
    with open(csv_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            domain = row['Request Domain']
            if domain != '':
                data_dict[domain] = {
                    'ID': row['ID'],
                    'Time (ms)': row['Time (ms)'],
                    'Response Domain': row['Response Domain'],
                    'IP Address': row['IP Address'],
                    'HTTP Status Code': row['HTTP Status Code'],
                    'Error': row['Error']
                }
    return data_dict
                
def analyse_data():
    mullvad_data = get_data(mullvad_path)
    control_data = get_data(control_path)

    analysis_data = {}

    for domain, data in mullvad_data.items():
        mullvad_code = data['HTTP Status Code']
        if mullvad_code != '200':
            control_code = control_data[domain]['HTTP Status Code']
            if mullvad_code != control_code:
                analysis_data[domain] = {
                    'Mullvad Response Domain': data['Response Domain'],
                    'Control Response Domain': control_data[domain]['Response Domain'],
                    'Mullvad Status Code': mullvad_code,
                    'Control Status Code': control_code,
                    'Mullvad Error': data['Error'],
                    'Control Error': control_data[domain]['Error']
                }
    
    return analysis_data


data = analyse_data()
total = 0
control_200 = 0
control_non200 = 0
mullvad_error = 0
mullvad_block = 0
for domain, data in data.items():
    total += 1
    if data['Control Status Code'] == '200':
        control_200 += 1
    else:
        control_non200 += 1
    if data['Mullvad Status Code'] == '0':
        mullvad_error += 1
    else:
        mullvad_block += 1

print("Total differences: {}".format(total))
print("Control 200: {}".format(control_200))
print("Control non-200: {}".format(control_non200))
print("Mullvad errors: {}".format(mullvad_error))
print("Mullvad HTTP blocks: {}".format(mullvad_block))

