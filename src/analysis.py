import csv

mullvad_path = "data/csvs/2021-5-19/2021-5-19-mullvad.csv"
control_path = "data/csvs/2021-5-19/2021-5-19-control-test.csv"
aggragated_path = "analysis/aggregated/2021-5-19-aggregated.csv"


def get_data(csv_path):
    data_dict = {}
    with open(csv_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            domain = row['Request Domain']
            if domain != '':
                data_dict[domain] = {
                    'ID': row['ID'],
                    'Time': row['Time'],
                    'Duration (ms)': row['Duration (ms)'],
                    'Attempts': row['Attempts'],
                    'Response Domain': row['Response Domain'],
                    'IP Address': row['IP Address'],
                    'HTTP Status Code': row['HTTP Status Code'],
                    'Error': row['Error']
                }
    return data_dict


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

        for domain, data in mullvad_data.items():
            data = {
                'ID': data['ID'],
                'Domain': domain,
                'Mullvad Response Domain': data['Response Domain'],
                'Control Response Domain': control_data[domain]['Response Domain'],
                'Mullvad Status Code': data['HTTP Status Code'],
                'Control Status Code': control_data[domain]['HTTP Status Code'],
                'Mullvad Error': data['Error'],
                'Control Error': control_data[domain]['Error']
            }
            writer.writerow(data)


def analyse_data():

    non_200, diff_data, undef_data = agregate_data()
    
    # handle different data first
    diff_errors = {}
    diff_codes = {}
    for domain, data in diff_data.items():
        error = data['Mullvad Error']
        if 'none' in error:
            code = data['Mullvad Status Code']
            if code in diff_codes:
                diff_codes[code] += 1
            else:
                diff_codes[code] = 1
        elif 'Navigation timeout' in error:
            if 'Navigation timeout' in diff_errors:
                diff_errors['Navigation timeout'] += 1
            else:
                diff_errors['Navigation timeout'] = 1
        else:
            error_name = error.split()[0]
            if error_name in diff_errors:
                diff_errors[error_name] += 1
            else:
                diff_errors[error_name] = 1
    
    # handle undefined data
    undef_errors = {}
    undef_codes = {}
    for domain, data in undef_data.items():
        error = data['Mullvad Error']
        if 'none' in error:
            code = data['Mullvad Status Code']
            if code in undef_codes:
                undef_codes[code] += 1
            else:
                undef_codes[code] = 1
        elif 'Navigation timeout' in error:
            if 'Navigation timeout' in undef_errors:
                undef_errors['Navigation timeout'] += 1
            else:
                undef_errors['Navigation timeout'] = 1
        else:
            error_name = error.split()[0]
            if error_name in undef_errors:
                undef_errors[error_name] += 1
            else:
                undef_errors[error_name] = 1
            

    return non_200, diff_errors, diff_codes, undef_errors, undef_codes

# non_200, diff_errors, diff_codes, undef_errors, undef_codes = analyse_data()

# print("Total non-2xx: {}".format(non_200))
# print(diff_errors)
# print("Errors: {}".format(sum(diff_errors.values())/10))
# print(diff_codes)
# print("Status codes: {}".format(sum(diff_codes.values())/10))
# print(undef_codes)

aggregate_data()