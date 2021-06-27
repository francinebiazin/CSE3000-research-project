import csv
from shutil import copy2

# variables
date = '2021-6-13'
phash_threshold = 19

# paths
aggregated_path = 'analysis/stage4/aggregated/{}-aggregated.csv'.format(date)
block_analysis = 'analysis/stage4/block-analysis/{}-block-analysis.csv'.format(date)
aggregated_blocks = 'analysis/stage4/individual/aggregated-blocks.csv'
manual_check_path = 'analysis/stage4/manual-checks/'
mullvad_path = 'data/stage4/screenshots/{}-mullvad'.format(date)
control_errors = 'analysis/stage4/stats/control-errors.csv'
subpage_blocks = 'analysis/stage4/individual/subpage-blocks.csv'


# ID,Subpage ID,Time,Duration (ms),Attempts,Request Domain,Response Domain,IP Address,HTTP Status Code,Error

def analyse_blocks():
    # prepare csv
    headers = [
        'ID',
        'Subpage ID',
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
        domain = 'none'
        for row in csv_reader:
            # data that needs to be saved:
            id = row['ID']
            subpage = row['Subpage ID']
            if subpage == '0':
                domain = row['Domain']
            request = row['Domain']
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
                        src = mullvad_path + '/{}-{}-{}-{}.png'.format(date, id, domain.split('//')[1], subpage)
                        copy2(src, manual_check_path)
                        blocked = '?'
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
                    'Subpage ID': subpage,
                    'Domain': request,
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
    
    dates = ['2021-6-8', '2021-6-9', '2021-6-11', '2021-6-12', '2021-6-13']

    data = {}

    for date in dates:
        path = 'analysis/stage4/aggregated/{}-aggregated.csv'.format(date)
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


# when homepage is fine, but not subpages
def get_subpages_blocks():
    # initialise data dict
    data = {
        'Date': date,
        'Not Blocked': 0,
        'Home Page Blocked': 0,
        'Subpage Blocked': 0,
        'Maybe Blocked': 0,
        'No Difference': 0,
        'HTTP Blocks': 0,
        'Timeout Blocks': 0,
        'Error Blocks': 0,
        'Differentiated Content': 0,
        'Block Page': 0,
        'Challenge-Response Test': 0
    }

    # ID,Subpage ID,Domain,PHash Difference,Manual Check,Blocked,Type of Block

    domain_id = '0'
    blocks = []
    maybe = False
    home_page_blocked = False
    no_difference = False

    with open(block_analysis, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            subpage = row['Subpage ID']
            blocked = row['Blocked']
            type_block = row['Type of Block']
            # check if it's a new domain
            if subpage == '0':
                # ensure not very first domain
                if domain_id != '0':
                    # check if there is data to add to data dictionary
                    if len(blocks) > 0:
                        # update number of domains with blocked subpages
                        data['Subpage Blocked'] += 1
                        # add types of blocks
                        for block in blocks:
                            if block == 'timeout':
                                data['Timeout Blocks'] += 1
                            elif 'net::' in block:
                                data['Error Blocks'] += 1
                            elif block == 'differentiated content':
                                data['Differentiated Content'] += 1
                            elif block == 'block page':
                                data['Block Page'] += 1
                            elif block == 'challenge-response test':
                                data['Challenge-Response Test'] += 1
                            else:
                                data['HTTP Blocks'] += 1
                    # home page or any subpages may be blocked
                    elif maybe:
                        data['Maybe Blocked'] += 1
                    # home page or any subpage with no difference
                    elif no_difference:
                        data['No Difference'] += 1
                    # last option: not blocked
                    elif not home_page_blocked:
                        data['Not Blocked'] += 1
                # reset values for new domain
                domain_id = row['ID']
                blocks = []
                maybe = False
                home_page_blocked = False
                no_difference = False
                # check homepage values
                if blocked == 'yes':
                    home_page_blocked = True
                    data['Home Page Blocked'] += 1
                elif 'maybe' in blocked:
                    maybe = True
                elif blocked == 'no difference':
                    no_difference = True
            # subpage
            else:
                if home_page_blocked:
                    continue
                else:
                    # check subpage values
                    if blocked == 'yes':
                        blocks.append(type_block)
                    elif 'maybe' in blocked:
                        maybe = True
                    elif blocked == 'no difference':
                        no_difference = True
    
    # add data for last domain
    if len(blocks) > 0:
        # update number of domains with blocked subpages
        data['Subpage Blocked'] += 1
        # add types of blocks
        for block in blocks:
            if block == 'timeout':
                data['Timeout Blocks'] += 1
            elif 'net::' in block:
                data['Error Blocks'] += 1
            elif block == 'differentiated content':
                data['Differentiated Content'] += 1
            elif block == 'block page':
                data['Block Page'] += 1
            elif block == 'challenge-response test':
                data['Challenge-Response Test'] += 1
            else:
                data['HTTP Blocks'] += 1
    # home page or any subpages may be blocked
    elif maybe:
        data['Maybe Blocked'] += 1
    # home page or any subpage with no difference
    elif no_difference:
        data['No Difference'] += 1
    # last option: not blocked
    elif not home_page_blocked:
        data['Not Blocked'] += 1
       
    with open(subpage_blocks, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, list(data.keys()))
        # writer.writeheader()
        writer.writerow(data)



# analyse_blocks()
# get_aggregated_blocks()
# analyse_control_errors()
# get_subpages_blocks()
