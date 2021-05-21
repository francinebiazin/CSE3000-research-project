import csv
import pandas as pd

date = '2021-5-21'

# paths
mullvad_path = "data/stage3/csvs/{}/{}-mullvad.csv".format(date, date)
control_path = "data/stage3/csvs/{}/{}-control.csv".format(date, date)
aggragated_path = "analysis/stage3/aggregated/{}-aggregated.csv".format(date)
mullvad_analysis = "analysis/stage3/individual/mullvad-analysis.csv"
control_analysis = "analysis/stage3/individual/control-analysis.csv"
test_analysis = "analysis/stage3/individual/mullvad-analysis-TEST.csv"
# aggregated_analysis


def get_data(csv_path):
    data_dict = {}
    with open(csv_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            id = row['ID']
            if id != '':
                data_dict[id] = {
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


def individual_data(read_data, write_data, connection):

    # get headers
    headers = []
    with open(write_data, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        headers = csv_reader.fieldnames

    # add headers to data dict
    data = {}
    for header in headers:
        if header == 'Date':
            data[header] = date
        elif header == 'Connection':
            data[header] = connection
        else:
            data[header] = 0

    # add actual data
    with open(read_data, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            code = row['HTTP Status Code']
            error = row['Error']
            if code:
                if code in data:
                    data[code] += 1
                else:
                    print(code)
            if error:
                error_name = error.split()[0]
                if error_name in data:
                    data[error_name] += 1
                else:
                    print(error_name)
    
    # write data
    with open (write_data,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=headers)
        csv_writer.writerow(data)



def aggregate_data():
    mullvad_data = get_data(mullvad_path)
    control_data = get_data(control_path)

    headers = [
        'ID',
        'Domain',
        'Mullvad Response Domain',
        'Control Response Domain',
        'Mullvad Status Code',
        'Control Status Code',
        'Mullvad Error',
        'Control Error'
    ]

    with open(aggragated_path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

        for id, data in mullvad_data.items():
            data = {
                'ID': id,
                'Domain': data['Domain'],
                'Mullvad Response Domain': data['Response Domain'],
                'Control Response Domain': control_data[id]['Response Domain'],
                'Mullvad Status Code': data['HTTP Status Code'],
                'Control Status Code': control_data[id]['HTTP Status Code'],
                'Mullvad Error': data['Error'],
                'Control Error': control_data[id]['Error']
            }
            writer.writerow(data)


# def analyse_data():
    
#     # handle different data first
#     diff_errors = {}
#     diff_codes = {}
#     for domain, data in diff_data.items():
#         error = data['Mullvad Error']
#         if 'none' in error:
#             code = data['Mullvad Status Code']
#             if code in diff_codes:
#                 diff_codes[code] += 1
#             else:
#                 diff_codes[code] = 1
#         elif 'Navigation timeout' in error:
#             if 'Navigation timeout' in diff_errors:
#                 diff_errors['Navigation timeout'] += 1
#             else:
#                 diff_errors['Navigation timeout'] = 1
#         else:
#             error_name = error.split()[0]
#             if error_name in diff_errors:
#                 diff_errors[error_name] += 1
#             else:
#                 diff_errors[error_name] = 1
    
#     # handle undefined data
#     undef_errors = {}
#     undef_codes = {}
#     for domain, data in undef_data.items():
#         error = data['Mullvad Error']
#         if 'none' in error:
#             code = data['Mullvad Status Code']
#             if code in undef_codes:
#                 undef_codes[code] += 1
#             else:
#                 undef_codes[code] = 1
#         elif 'Navigation timeout' in error:
#             if 'Navigation timeout' in undef_errors:
#                 undef_errors['Navigation timeout'] += 1
#             else:
#                 undef_errors['Navigation timeout'] = 1
#         else:
#             error_name = error.split()[0]
#             if error_name in undef_errors:
#                 undef_errors[error_name] += 1
#             else:
#                 undef_errors[error_name] = 1
            

#     return non_200, diff_errors, diff_codes, undef_errors, undef_codes

# non_200, diff_errors, diff_codes, undef_errors, undef_codes = analyse_data()

# print("Total non-2xx: {}".format(non_200))
# print(diff_errors)
# print("Errors: {}".format(sum(diff_errors.values())/10))
# print(diff_codes)
# print("Status codes: {}".format(sum(diff_codes.values())/10))
# print(undef_codes)

individual_data(control_path, test_analysis, 'Control')