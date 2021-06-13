import csv

categories_path = 'categories/categories-domains.csv'
categories_analysis = 'analysis/stage4/categories/stage4-categories-analysis.csv'

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
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=['Category', 'Blocked', 'Other'])
        csv_writer.writeheader()

    categories = get_categories()
    
    dates = ['2021-6-8', '2021-6-9', '2021-6-11', '2021-6-12', '2021-6-13']

    data = {}

    # ID,Subpage ID,Domain,PHash Difference,Manual Check,Blocked,Type of Block

    for date in dates:
        path = 'analysis/stage4/block-analysis/{}-block-analysis.csv'.format(date)

        domain_id = '0'
        subpage_blocked = False
        maybe = False
        home_page_blocked = False
        category = 'none'

        with open(path, mode='r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            home_page_blocked = False
            for row in csv_reader:
                subpage = row['Subpage ID']
                url = row['Domain']
                blocked = row['Blocked']
                # check if it's a new domain
                if subpage == '0':
                    category = categories[url]
                    # ensure not very first domain
                    if domain_id != '0':
                        if subpage_blocked or maybe:
                            # update number of domains with blocked subpages
                            # check if category already in dictionary
                            if category in data:
                                data[category]['Blocked'] += 1
                            else:
                                data[category] = {
                                    'Blocked': 1,
                                    'Other': 0
                                }
                        # not blocked or no difference
                        elif not home_page_blocked:
                            # check if category already in dictionary
                            if category in data:
                                data[category]['Other'] += 1
                            else:
                                data[category] = {
                                    'Blocked': 0,
                                    'Other': 1
                                }
                    # reset values for new domain
                    domain_id = row['ID']
                    subpage_blocked = False
                    maybe = False
                    home_page_blocked = False
                    # check homepage values
                    if blocked == 'yes':
                        home_page_blocked = True
                        # check if category already in dictionary
                        if category in data:
                            data[category]['Blocked'] += 1
                        else:
                            data[category] = {
                                'Blocked': 1,
                                'Other': 0
                            }
                    elif 'maybe' in blocked:
                        maybe = True
                # subpage
                else:
                    if home_page_blocked:
                        continue
                    else:
                        # check subpage values
                        if blocked == 'yes':
                            subpage_blocked = True
                        elif 'maybe' in blocked:
                            maybe = True
        
        # add data for last domain
        if subpage_blocked or maybe:
            # update number of domains with blocked subpages
            # check if category already in dictionary
            if category in data:
                data[category]['Blocked'] += 1
            else:
                data[category] = {
                    'Blocked': 1,
                    'Other': 0
                }
        # not blocked or no difference
        elif not home_page_blocked:
            # check if category already in dictionary
            if category in data:
                data[category]['Other'] += 1
            else:
                data[category] = {
                    'Blocked': 0,
                    'Other': 1
                }

    # write data
    for category, info in data.items():
        with open (categories_analysis,'a') as csv_file:                            
            csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=['Category', 'Blocked', 'Other'])
            data = {
                'Category': category,
                'Blocked': info['Blocked'],
                'Other': info['Other']
            }
            csv_writer.writerow(data)


analyse_categories()
