import csv

categories_path = 'categories/categories-domains.csv'
categories_analysis = 'analysis/stage3/categories/stage3-categories-analysis.csv'

def get_categories():
    categories = {}

    # URL,Status,Categorization,Reputation
    with open(categories_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # data that needs to be saved:
            url = row['URL']
            category = row['Categorization']
            categories[url] = category[2:]
    
    return categories


def analyse_categories():

    # prepare csv file
    with open (categories_analysis,'w') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=['Category', 'Blocked', 'Not Blocked'])
        csv_writer.writeheader()

    categories = get_categories()
    
    dates = ['2021-5-21', '2021-5-22', '2021-5-23', '2021-5-24', '2021-5-25']

    data = {}

    # ID,Domain,PHash Difference,Manual Check,Blocked,Type of Block

    for date in dates:
        path = 'analysis/stage3/block-analysis/{}-block-analysis.csv'.format(date)
        with open(path, mode='r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                url = row['Domain']
                blocked = row['Blocked']
                category = categories[url]
                # check if blocked or maybe blocked
                # since maybe blocked not statistically significant, we count it as blocked
                if blocked == 'yes' or 'maybe' in blocked:
                    # check if category already in dictionary
                    if category in data:
                        data[category]['Blocked'] += 1
                    else:
                        data[category] = {
                            'Blocked': 1,
                            'Not Blocked': 0
                        }
                else:
                    # check if category already in dictionary
                    if category in data:
                        data[category]['Not Blocked'] += 1
                    else:
                        data[category] = {
                            'Blocked': 0,
                            'Not Blocked': 1
                        }

    # write data
    for category, info in data.items():
        with open (categories_analysis,'a') as csv_file:                            
            csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=['Category', 'Blocked', 'Not Blocked'])
            data = {
                'Category': category,
                'Blocked': info['Blocked'],
                'Not Blocked': info['Not Blocked']
            }
            csv_writer.writerow(data)


analyse_categories()
