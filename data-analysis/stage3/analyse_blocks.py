import csv
# from shutil import copy2

# variables
date = '2021-5-25'
phash_threshold = 19

# paths
aggregated_path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)
block_analysis = 'analysis/stage3/block-analysis/{}-block-analysis.csv'.format(date)
aggregated_blocks = 'analysis/stage3/individual/aggregated-blocks.csv'
manual_check_path = 'analysis/stage3/manual-checks/'
mullvad_path = 'data/stage3/screenshots/{}-mullvad'.format(date)
control_errors = 'analysis/stage3/stats/control-errors.csv'


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
                        # copy file for manual check
                        # src = mullvad_path + '/{}-{}-{}.png'.format(date, id, domain.split('//')[1])
                        # copy2(src, manual_check_path)
                    else:
                        manual_check = 'no'
                        blocked = 'no'
                # control does not have screenshot
                else:
                    # cases already manually verified and no blocks found
                    manual_check = 'no'
                    blocked = 'no'
            # Mullvad: status code is non-2xx
            elif mullvad_code > 0:
                # check control
                # Control: status code is 2xx
                if control_code > 199 and control_code < 300:
                    blocked = 'yes'
                    type_block = mullvad_code
                # Control: status code is non-2xx
                elif control_code > 0:
                    blocked = 'no difference'
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
                    blocked = 'maybe: control {}'.format(control_code)
                # Control: no status code
                else:
                    # Mullvad: timeout
                    if 'Navigation ' in mullvad_error:
                        # check if control and Mullvad had the same error
                        if 'Navigation ' in control_error:
                            blocked = 'no difference'
                            type_block = 'NA'
                        else:
                            blocked = 'maybe: control {}'.format(control_error.split()[0])
                    # Mullvad: error
                    else:
                        # check if control and Mullvad had the same error
                        if 'Navigation ' in control_error:
                            blocked = 'maybe: control timeout'
                        else:
                            blocked = 'no difference'
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


# perform manual checks before running this!
def get_aggregated_blocks():
    # initialise data dict
    data = {
        'Date': date,
        'Manual Check': 0,
        'Not Blocked': 0,
        'Blocked': 0,
        'Maybe Blocked': 0,
        'No Difference': 0,
        'HTTP Blocks': 0,
        'Timeout Blocks': 0,
        'Error Blocks': 0,
        'Differentiated Content': 0,
        'Block Page': 0,
        'Challenge-Response Test': 0
    }
    # ID,Domain,PHash Difference,Manual Check,Blocked,Type of Block
    # add data
    with open(block_analysis, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            manual_check = row['Manual Check']
            blocked = row['Blocked']
            type_block = row['Type of Block']
            if manual_check == 'yes':
                data['Manual Check'] += 1
            if blocked == 'no':
                data['Not Blocked'] += 1
            elif blocked == 'no difference':
                data['No Difference'] += 1
            elif blocked == 'yes':
                data['Blocked'] += 1
                if type_block == 'timeout':
                    data['Timeout Blocks'] += 1
                elif 'net::' in type_block:
                    data['Error Blocks'] += 1
                elif type_block == 'differentiated content':
                    data['Differentiated Content'] += 1
                elif type_block == 'block page':
                    data['Block Page'] += 1
                elif type_block == 'challenge-response test':
                    data['Challenge-Response Test'] += 1
                else:
                    data['HTTP Blocks'] += 1
            if 'maybe' in blocked:
                data['Maybe Blocked'] += 1
    
    # write data
    with open (aggregated_blocks,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(data.keys()))
        # csv_writer.writeheader()
        csv_writer.writerow(data)


def analyse_control_errors():
    # prepare csv
    headers = [
        'ID',
        'Domain',
        'Frequency'
    ]
    with open(control_errors, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()
    
    dates = ['2021-5-21', '2021-5-22', '2021-5-23', '2021-5-24', '2021-5-25']

    data = {}

    for date in dates:
        path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)
        with open(path, mode='r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # data that needs to be saved:
                id = row['ID']
                domain = row['Domain']
                phash = row['PHash Difference']
                # get data
                mullvad_code = int(row['Mullvad Status Code'])
                # Mullvad: status code is 2xx
                if mullvad_code > 199 and mullvad_code < 300:
                    # check if control does not have a screenshot
                    if phash in ['none', 'NA']:
                        if id in data:
                            data[id]['Frequency'] += 1
                        else:
                            data[id] = {
                                'Domain': domain,
                                'Frequency': 1
                            }
                
    # write data
    for id, info in data.items():
        with open (control_errors,'a') as csv_file:                            
            csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(headers))
            data = {
                'ID': id,
                'Domain': info['Domain'],
                'Frequency': info['Frequency']
            }
            csv_writer.writerow(data)



# analyse_blocks()
get_aggregated_blocks()
# analyse_control_errors()
