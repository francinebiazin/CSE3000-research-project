import csv
import matplotlib.pyplot as plt
import pandas as pd

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
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=['Category', 'Blocked', 'Other'])
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
                            'Other': 0
                        }
                else:
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


def get_proportion_graph():

    data = {}

    # Category,Blocked,Other
    with open(categories_analysis, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            blocked = int(row['Blocked'])
            if blocked == 0:
                continue
            other = int(row['Other'])
            category = row['Category']
            data[category] = blocked/(blocked + other) * 100
    

    df = pd.DataFrame({'categories' : list(data.keys()) , 'values' : list(data.values())})
    df = df.sort_values('values')

    # Set the figure size
    fig = plt.figure(figsize=(10, 6))
    
    # creating the bar plot
    plt.bar(list(df['categories']), list(df['values']), color ='#7400B8', width = 0.4)
    plt.tick_params(axis='x', labelsize=8)
    plt.tick_params(axis='y', labelsize=8)
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plt.autoscale()
    
    plt.xlabel("Categories")
    plt.ylabel("Ratio of requests blocked")
    plt.title("Stage 3: Blocks per Category")
    plt.show()



# analyse_categories()
get_proportion_graph()
