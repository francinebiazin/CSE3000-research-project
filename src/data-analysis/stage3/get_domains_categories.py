import csv

domainsPath = 'categories/top-1m-forcategories.csv'

domains_data = {}
with open(domainsPath, mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    index = 1
    for row in csv_reader:
        if index > 3000:
            break
        if row['Domain'] != 'oeeee.com' and row['Domain'] != 'tamin.ir' and row['Domain'] != 'taleo.net' and row['Domain'] != 'support.wix.com':
            domains_data[index] = row['Domain']
            index += 1

# create 30 txt files with 100 domains in each
start = 1
for i in range(1, 31):
    txt_path = 'categories/domains-{}.txt'.format(i)
    file = open(txt_path,"w")
    for j in range(start, start+100):
        file.write(domains_data[j] + '\n')
    start += 100
