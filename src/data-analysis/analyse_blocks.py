import csv

# variables
date = '2021-5-24'
phash_threshold = 15

# paths
aggregated_path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)
block_analysis = 'analysis/stage3/block-analysis/{}-block-analysis.csv'.format(date)


# ID,Domain,Mullvad Response Domain,Control Response Domain,Mullvad Status Code,Control Status Code,Mullvad Error,Control Error,PHash Difference

def analyse_blocks():
    # prepare csv
    headers = [
        'ID',
        'Domain',
        'PHash Difference',
        'Manual Check',
        'Blocked',
        'Type of Block'
    ]
    with open(block_analysis, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

    with open(aggregated_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # data that needs to be saved:
            id = row['ID']
            domain = row['Domain']
            phash = row['PHash Difference']
            manual_check = 'NA'
            blocked = '?'
            type_block = 'NA'
            # get data
            mullvad_code = int(row['Mullvad Status Code'])
            control_code = int(row['Control Status Code'])
            mullvad_error = row['Mullvad Error']
            control_error = row['Control Error']
            # Mullvad: status code is 2xx
            if mullvad_code > 199 and mullvad_code < 300:
                # check if control has a screenshot
                if phash not in ['none', 'NA']:
                    phash = int(phash)
                    # manually check phash values larger than threshold
                    if phash > phash_threshold:
                        manual_check = 'yes'
                    else:
                        manual_check = 'no'
                        blocked = 'no'
                # control does not have screenshot
                else:
                    manual_check = 'yes'
            # Mullvad: status code is non-2xx
            elif mullvad_code > 0:
                # check control
                # Control: status code is 2xx
                if control_code > 199 and control_code < 300:
                    blocked = 'yes'
                    type_block = mullvad_code
                # Control: status code is non-2xx
                elif control_code > 0:
                    blocked = 'no'
                    type_block = 'NA'
                # Control: no status code
                else:
                    # Control: timeout
                    if 'Navigation ' in control_error:
                        blocked = 'maybe: control timeout'
                        type_block = mullvad_code
                    # Control: error
                    else:
                        blocked = 'maybe: control {}'.format(control_error.split()[0])
                        type_block = mullvad_code
            # Mullvad: no status code
            else:
                # Mullvad: timeout
                if 'Navigation ' in mullvad_error:
                    # potential block
                    type_block = 'timeout'
                # Mullvad: error
                else:
                    # potential block
                    type_block = '{}'.format(mullvad_error.split()[0])
                # check control
                # Control: status code is 2xx
                if control_code > 199 and control_code < 300:
                    blocked = 'yes'
                # Control: status code is non-2xx
                elif control_code > 0:
                    blocked = 'no'
                    type_block = 'NA'
                # Control: no status code
                else:
                    # Control: timeout
                    if 'Navigation ' in control_error:
                        # Mullvad: timeout
                        if 'Navigation ' in mullvad_error:
                            blocked = 'no'
                            type_block = 'NA'
                        # Mullvad: error
                        else:
                            blocked = 'maybe: control timeout'
                    # Control: error
                    else:
                        blocked = 'no'
                        type_block = 'NA'
            # write data
            with open (block_analysis,'a') as csv_file:                            
                csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(headers))
                data = {
                    'ID': id,
                    'Domain': domain,
                    'PHash Difference': phash,
                    'Manual Check': manual_check,
                    'Blocked': blocked,
                    'Type of Block': type_block
                }
                csv_writer.writerow(data)

analyse_blocks()
