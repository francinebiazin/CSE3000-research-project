import csv
import pandas as pd

date = '2021-5-25'

# paths
phash_path = "analysis/stage3/screenshots/{}-phash.csv".format(date)
analysis_path = 'analysis/stage3/phash/phash-values-analysis.csv'

def get_analysis():
    # initialise data dict
    data = {
        'Date': date,
        'none/NA': 0,
        '0-4': 0,
        '5-9': 0,
        '10-14': 0,
        '15-19': 0,
        '20-24': 0,
        '25-29': 0,
        '30-34': 0,
        '35-39': 0,
        '40-49': 0,
        '>= 50': 0
    }

    # add data
    with open(phash_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            difference = row['Difference']
            if difference in ['none', 'NA']:
                data['none/NA'] += 1
            else:
                difference = int(difference)
                if difference > -1 and difference < 5:
                    data['0-4'] += 1
                elif difference > 4 and difference < 10:
                    data['5-9'] += 1
                elif difference > 9 and difference < 15:
                    data['10-14'] += 1
                elif difference > 14 and difference < 20:
                    data['15-19'] += 1
                elif difference > 19 and difference < 25:
                    data['20-24'] += 1
                elif difference > 24 and difference < 30:
                    data['25-29'] += 1
                elif difference > 29 and difference < 35:
                    data['30-34'] += 1
                elif difference > 34 and difference < 40:
                    data['35-39'] += 1
                elif difference > 39 and difference < 50:
                    data['40-49'] += 1
                else:
                    data['>= 50'] += 1
    
    # write data
    with open (analysis_path,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(data.keys()))
        csv_writer.writerow(data)


def get_analysis_stats():
    phash_df = pd.read_csv(analysis_path)
    print(phash_df)

    print('none/NA average: {} (std: {})'.format(phash_df['none/NA'].mean()/30, phash_df['none/NA'].std()/30))
    print('0-4 average: {} (std: {})'.format(phash_df['0-4'].mean()/30, phash_df['0-4'].std()/30))
    print('5-9 average: {} (std: {})'.format(phash_df['5-9'].mean()/30, phash_df['5-9'].std()/30))
    print('10-14 average: {} (std: {})'.format(phash_df['10-14'].mean()/30, phash_df['10-14'].std()/30))
    print('15-19 average: {} (std: {})'.format(phash_df['15-19'].mean()/30, phash_df['15-19'].std()/30))
    print('20-24 average: {} (std: {})'.format(phash_df['20-24'].mean()/30, phash_df['20-24'].std()/30))
    print('25-29 average: {} (std: {})'.format(phash_df['25-29'].mean()/30, phash_df['25-29'].std()/30))
    print('30-34 average: {} (std: {})'.format(phash_df['30-34'].mean()/30, phash_df['30-34'].std()/30))
    print('35-39 average: {} (std: {})'.format(phash_df['35-39'].mean()/30, phash_df['35-39'].std()/30))
    print('40-49 average: {} (std: {})'.format(phash_df['40-49'].mean()/30, phash_df['40-49'].std()/30))
    print('>= 50 average: {} (std: {})'.format(phash_df['>= 50'].mean()/30, phash_df['>= 50'].std()/30))



# get_analysis()
get_analysis_stats()
