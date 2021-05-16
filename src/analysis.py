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


def agregate_data():
    mullvad_data = get_data(mullvad_path)
    control_data = get_data(control_path)

    diff_data = {}
    undef_data = {}

    for domain, data in mullvad_data.items():
        mullvad_code = data['HTTP Status Code']
        if mullvad_code != '200':
            control_code = control_data[domain]['HTTP Status Code']
            if mullvad_code != control_code:
                diff_data[domain] = {
                    'Mullvad Response Domain': data['Response Domain'],
                    'Control Response Domain': control_data[domain]['Response Domain'],
                    'Mullvad Status Code': mullvad_code,
                    'Control Status Code': control_code,
                    'Mullvad Error': data['Error'],
                    'Control Error': control_data[domain]['Error']
                }
            else:
                undef_data[domain] = {
                    'Mullvad Response Domain': data['Response Domain'],
                    'Control Response Domain': control_data[domain]['Response Domain'],
                    'Mullvad Status Code': mullvad_code,
                    'Control Status Code': control_code,
                    'Mullvad Error': data['Error'],
                    'Control Error': control_data[domain]['Error']
                }
    
    return diff_data, undef_data


def analyse_data():

    diff_data, undef_data = agregate_data()
    
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
            

    return diff_errors, diff_codes, undef_errors, undef_codes


diff_errors, diff_codes, undef_errors, undef_codes = analyse_data()

print(diff_errors)
print("Errors: {}".format(sum(diff_errors.values())/10))
print(diff_codes)
print("Status codes: {}".format(sum(diff_codes.values())/10))
# print(undef_codes)

