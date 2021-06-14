import pandas as pd
import numpy as np
import csv
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest

# aggregated_path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)
mullvad_analysis_path = 'analysis/stage4/individual/mullvad-analysis.csv'
control_analysis_path = 'analysis/stage4/individual/control-analysis.csv'
aggregated_blocks = 'analysis/stage4/individual/aggregated-blocks.csv'
block_stats_path = 'analysis/stage4/stats/blocks-analysis.csv'
mullvad_stats_path = 'analysis/stage4/stats/mullvad-analysis.csv'
control_stats_path = 'analysis/stage4/stats/control-analysis.csv'
chi_squared_individual_path = 'analysis/stage4/stats/chi-squared-individual.txt'
chi_squared_blocks_path = 'analysis/stage4/stats/chi-squared-blocks.txt'
two_sample_proportion_unsure_path = 'analysis/stage4/stats/two-sample-proportion-unsure.txt'
two_sample_proportion_unsure_check_path = 'analysis/stage4/stats/two-sample-proportion-unsure-check.txt'
two_sample_proportion_blocks_path = 'analysis/stage4/stats/two-sample-proportion-blocks.txt'
control_domains_analysis = 'analysis/stage4/individual/control-domains-analysis.csv'
subpage_blocks = 'analysis/stage4/individual/subpage-blocks.csv'
subpage_stats_path = 'analysis/stage4/stats/subpage-analysis.csv'
chi_squared_subpages_path = 'analysis/stage4/stats/chi-squared-subpages.txt'
two_sample_proportion_subpages_path = 'analysis/stage4/stats/two-sample-proportion-subpages.txt'
categories_path = 'analysis/stage4/categories/stage4-categories-analysis.csv'
chi_squared_categories_path = 'analysis/stage4/stats/chi-squared-categories.txt'

# ID,Domain,Mullvad Response Domain,Control Response Domain,Mullvad Status Code,Control Status Code,Mullvad Error,Control Error,PHash Difference

# df = pd.read_csv(aggregated_path)
# df[['Mullvad Status Code', 'Control Status Code']] = df[['Mullvad Status Code', 'Control Status Code']].fillna(0.0).astype(int)
# print(df)

# print(df.mean())

# x = list(df['Mullvad Status Code'].fillna(0.0).astype(int))
# y = list(df['Control Status Code'].fillna(0.0).astype(int))
# # plt.scatter(x, y)

# # Add x and y lables, and set their font size
# plt.xlabel("Mullvad Status Code", fontsize=10)
# plt.ylabel("Control Status Code", fontsize=10)

# plt.show()

def get_stats_individual():
    mullvad_df = pd.read_csv(mullvad_analysis_path)
    # print(mullvad_df)

    # print('Mullvad 2xx average: {} (std: {})'.format(mullvad_df['2xx'].mean()/30, mullvad_df['2xx'].std()/30))
    # print('Mullvad non-2xx average: {} (std: {})'.format(mullvad_df['Non-2xx'].mean()/30, mullvad_df['Non-2xx'].std()/30))
    # print('Mullvad timeout average: {} (std: {})'.format(mullvad_df['Timeouts'].mean()/30, mullvad_df['Timeouts'].std()/30))
    # print('Mullvad errors average: {} (std: {})'.format(mullvad_df['Errors'].mean()/30, mullvad_df['Errors'].std()/30))

    mullvad_data = {
        'Date': 'Averages',
        'Connection': 'Mullvad VPN',
        '2xx': "%.2f" % (mullvad_df['2xx'].mean()/30),
        'Non-2xx': "%.2f" % (mullvad_df['Non-2xx'].mean()/30),
        'Timeouts': "%.2f" % (mullvad_df['Timeouts'].mean()/30),
        'Errors': "%.2f" % (mullvad_df['Errors'].mean()/30)
    }

    mullvad_df.to_csv(path_or_buf=mullvad_stats_path, index=False)

    # write data
    with open (mullvad_stats_path,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(mullvad_data.keys()))
        csv_writer.writerow(mullvad_data)

    control_df = pd.read_csv(control_analysis_path)
    # print(control_df)

    # print('Control 2xx average: {} (std: {})'.format(control_df['2xx'].mean()/30, control_df['2xx'].std()/30))
    # print('Control non-2xx average: {} (std: {})'.format(control_df['Non-2xx'].mean()/30, control_df['Non-2xx'].std()/30))
    # print('Control timeout average: {} (std: {})'.format(control_df['Timeouts'].mean()/30, control_df['Timeouts'].std()/30))
    # print('Control errors average: {} (std: {})'.format(control_df['Errors'].mean()/30, control_df['Errors'].std()/30))

    control_data = {
        'Date': 'Averages',
        'Connection': 'Control',
        '2xx': "%.2f" % (control_df['2xx'].mean()/30),
        'Non-2xx': "%.2f" % (control_df['Non-2xx'].mean()/30),
        'Timeouts': "%.2f" % (control_df['Timeouts'].mean()/30),
        'Errors': "%.2f" % (control_df['Errors'].mean()/30)
    }

    control_df.to_csv(path_or_buf=control_stats_path, index=False)

    # write data
    with open (control_stats_path,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(control_data.keys()))
        csv_writer.writerow(control_data)


def get_block_stats():
    blocks_df = pd.read_csv(aggregated_blocks)
    # print(blocks_df)

    # print('Manual check average: {} (std: {})'.format(blocks_df['Manual Check'].mean()/30, blocks_df['Manual Check'].std()/30))
    # print('Blocked average: {} (std: {})'.format(blocks_df['Blocked'].mean()/30, blocks_df['Blocked'].std()/30))
    # print('Maybe blocked average: {} (std: {})'.format(blocks_df['Maybe Blocked'].mean()/30, blocks_df['Maybe Blocked'].std()/30))
    # print('HTTP Blocks average: {} (std: {})'.format(blocks_df['HTTP Blocks'].mean()/30, blocks_df['HTTP Blocks'].std()/30))
    # print('Timeout Blocks average: {} (std: {})'.format(blocks_df['Timeout Blocks'].mean()/30, blocks_df['Timeout Blocks'].std()/30))
    # print('Error Blocks average: {} (std: {})'.format(blocks_df['Error Blocks'].mean()/30, blocks_df['Error Blocks'].std()/30))
    # print('Differentiated Content average: {} (std: {})'.format(blocks_df['Differentiated Content'].mean()/30, blocks_df['Differentiated Content'].std()/30))
    # print('Block Page average: {} (std: {})'.format(blocks_df['Block Page'].mean()/30, blocks_df['Block Page'].std()/30))
    # print('Challenge-Response Test average: {} (std: {})'.format(blocks_df['Challenge-Response Test'].mean()/30, blocks_df['Challenge-Response Test'].std()/30))

    # Date,Manual Check,Not Blocked,Blocked,Maybe Blocked,No Difference,HTTP Blocks,Timeout Blocks,Error Blocks,Differentiated Content,Block Page,Challenge-Response Test
    # Date,Manual Check,Not Blocked,Blocked,Maybe Blocked,No Difference,HTTP Blocks,Timeout Blocks,Error Blocks,Differentiated Content,Block Page,Challenge-Response Test

    data = {
        'Date': 'Averages',
        'Manual Check': "%.2f" % (blocks_df['Manual Check'].mean()/30),
        'Not Blocked': "%.2f" % (blocks_df['Not Blocked'].mean()/30),
        'Blocked': "%.2f" % (blocks_df['Blocked'].mean()/30),
        'Maybe Blocked': "%.2f" % (blocks_df['Maybe Blocked'].mean()/30),
        'No Difference': "%.2f" % (blocks_df['No Difference'].mean()/30),
        'HTTP Blocks': "%.2f" % (blocks_df['HTTP Blocks'].mean()/30),
        'Timeout Blocks': "%.2f" % (blocks_df['Timeout Blocks'].mean()/30),
        'Error Blocks': "%.2f" % (blocks_df['Error Blocks'].mean()/30),
        'Differentiated Content': "%.2f" % (blocks_df['Differentiated Content'].mean()/30),
        'Block Page': "%.2f" % (blocks_df['Block Page'].mean()/30),
        'Challenge-Response Test': "%.2f" % (blocks_df['Challenge-Response Test'].mean()/30)
    }

    blocks_df.to_csv(path_or_buf=block_stats_path, index=False)

    # write data
    with open (block_stats_path,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(data.keys()))
        csv_writer.writerow(data)


def get_subpage_stats():
    subpage_df = pd.read_csv(subpage_blocks)

    # Date,Not Blocked,Home Page Blocked,Subpage Blocked,Maybe Blocked,No Difference,HTTP Blocks,Timeout Blocks,Error Blocks,Differentiated Content,Block Page,Challenge-Response Test

    data = {
        'Date': 'Averages',
        'Not Blocked': "%.2f" % (subpage_df['Not Blocked'].mean()/10),
        'Home Page Blocked': "%.2f" % (subpage_df['Home Page Blocked'].mean()/10),
        'Subpage Blocked': "%.2f" % (subpage_df['Subpage Blocked'].mean()/10),
        'Maybe Blocked': "%.2f" % (subpage_df['Maybe Blocked'].mean()/10),
        'No Difference': "%.2f" % (subpage_df['No Difference'].mean()/10),
        'HTTP Blocks': "%.2f" % (subpage_df['HTTP Blocks'].mean()/30),
        'Timeout Blocks': "%.2f" % (subpage_df['Timeout Blocks'].mean()/30),
        'Error Blocks': "%.2f" % (subpage_df['Error Blocks'].mean()/30),
        'Differentiated Content': "%.2f" % (subpage_df['Differentiated Content'].mean()/30),
        'Block Page': "%.2f" % (subpage_df['Block Page'].mean()/30),
        'Challenge-Response Test': "%.2f" % (subpage_df['Challenge-Response Test'].mean()/30)
    }

    subpage_df.to_csv(path_or_buf=subpage_stats_path, index=False)

    # write data
    with open (subpage_stats_path,'a') as csv_file:                            
        csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=list(data.keys()))
        csv_writer.writerow(data)


def chi_squared_individual():

    # prep file writer
    file = open(chi_squared_individual_path,"w")
    file.write('Test if the data collected on the 5 different days are dependent or not.\n')
    file.write('H0: independently distributed.\n')
    file.write('H1: dependently distributed.\n')
    file.write('Alpha value set at 0.05\n')
    file.write('\n \n')

    # define Mullvad data table
    mullvad_data = []

    mullvad_df = pd.read_csv(mullvad_analysis_path)

    for i in range(5):
        row_df = mullvad_df.iloc[i]
        row = []
        row.append(row_df['2xx'])
        row.append(row_df['Non-2xx'])
        row.append(row_df['Timeouts'])
        row.append(row_df['Errors'])
        mullvad_data.append(row)

    mullvad_chi2, mullvad_p, mullvad_dof, mullvad_expected = chi2_contingency(mullvad_data)
  
    # interpret p-value
    alpha = 0.05
    file.write("Mullvad chi2 value is " + ("%.3f" % mullvad_chi2) + '\n')
    file.write("Mullvad p value is " + ("%.3f" % mullvad_p) + '\n')
    file.write("Mullvad degrees of freedom: " + str(mullvad_dof) + '\n')
    file.write("Mullvad expected frequencies table:" + '\n')
    file.write(str(mullvad_expected) + '\n')
    if mullvad_p <= alpha:
        file.write('Dependent (reject Mullvad H0)' + '\n')
    else:
        file.write('Independent (Mullvad H0 holds true)' + '\n')
    
    file.write('\n \n')
    
    # define Control data table
    control_data = []

    control_df = pd.read_csv(control_analysis_path)

    for i in range(5):
        row_df = control_df.iloc[i]
        row = []
        row.append(row_df['2xx'])
        row.append(row_df['Non-2xx'])
        row.append(row_df['Timeouts'])
        row.append(row_df['Errors'])
        control_data.append(row)

    control_chi2, control_p, control_dof, control_expected = chi2_contingency(control_data)
  
    # interpret p-value
    file.write("Control chi2 value is " + ("%.3f" % control_chi2) + '\n')
    file.write("Control p value is " + ("%.3f" % control_p) + '\n')
    file.write("Control degrees of freedom: " + str(control_dof) + '\n')
    file.write("Control expected frequencies table:" + '\n')
    file.write(str(control_expected) + '\n')
    if control_p <= alpha:
        file.write('Dependent (reject Control H0)' + '\n')
    else:
        file.write('Independent (Control H0 holds true)' + '\n')


def chi_squared_blocks():

    # prep file writer
    file = open(chi_squared_blocks_path,"w")
    file.write('Test if the blocks identified on the 5 different days are dependent or not.\n')
    file.write('H0: independently distributed.\n')
    file.write('H1: dependently distributed.\n')
    file.write('Alpha value set at 0.05\n')
    file.write('\n \n')

    # define data table
    data = []

    blocks_df = pd.read_csv(block_stats_path)

    for i in range(5):
        row_df = blocks_df.iloc[i]
        row = []
        row.append(row_df['Not Blocked'])
        row.append(row_df['Blocked'])
        # row.append(row_df['Maybe Blocked'])
        row.append(row_df['No Difference'])
        data.append(row)

    chi2, p, dof, expected = chi2_contingency(data)
  
    # interpret p-value
    alpha = 0.05
    file.write("Blocks chi2 value is " + ("%.3f" % chi2) + '\n')
    file.write("Blocks p value is " + ("%.3f" % p) + '\n')
    file.write("Blocks degrees of freedom: " + str(dof) + '\n')
    file.write("Blocks expected frequencies table:" + '\n')
    file.write(str(expected) + '\n')
    if p <= alpha:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')


def chi_squared_subpages():

    # prep file writer
    file = open(chi_squared_subpages_path,"w")
    file.write('Test if the subpage blocks identified on the 5 different days are dependent or not.\n')
    file.write('H0: independently distributed.\n')
    file.write('H1: dependently distributed.\n')
    file.write('Alpha value set at 0.05\n')
    file.write('\n \n')

    # define data table
    data = []

    subpages_df = pd.read_csv(subpage_blocks)

    # Not Blocked,Home Page Blocked,Subpage Blocked,Maybe Blocked,No Difference

    for i in range(5):
        row_df = subpages_df.iloc[i]
        row = []
        row.append(row_df['Not Blocked'])
        row.append(row_df['Home Page Blocked'])
        row.append(row_df['Subpage Blocked'])
        # row.append(row_df['Maybe Blocked'])
        row.append(row_df['No Difference'])
        data.append(row)

    chi2, p, dof, expected = chi2_contingency(data)
  
    # interpret p-value
    alpha = 0.05
    file.write("Subpage chi2 value is " + ("%.3f" % chi2) + '\n')
    file.write("Subpage p value is " + ("%.3f" % p) + '\n')
    file.write("Subpage degrees of freedom: " + str(dof) + '\n')
    file.write("Subpage expected frequencies table:" + '\n')
    file.write(str(expected) + '\n')
    if p <= alpha:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')



def two_sample_proportion_unsure():
    # can we assume anything from our sample
    significance = 0.025

    # prep file writer
    file = open(two_sample_proportion_unsure_check_path,"w")
    file.write('Test if the requests that could not be identified as blocks are statistically significant.\n')
    file.write('\n')
    file.write('p_b is the proportion of blocked requests when we count unsure as blocked.\n')
    file.write('p_nb is the proportion of blocked requests when we count unsure as not blocked.\n')
    file.write('\n')
    file.write('H0: p_b - p_nb = 0.\n')
    file.write('H1: p_b - p_nb != 0.\n')
    file.write('\n')
    file.write('Alpha value set at 0.025\n')
    file.write('\n')

    # add all data points into contingency table
    total_requests = 15000
    total_blocked = 0
    total_unsure = 0

    blocks_df = pd.read_csv(block_stats_path)

    for i in range(5):
        row_df = blocks_df.iloc[i]
        total_blocked += row_df['Blocked']
        total_unsure += row_df['Maybe Blocked']

    # our samples - 82% are good in one, and ~79% are good in the other
    # note - the samples do not need to be the same size
    sample_success_a, sample_size_a = (total_blocked + total_unsure, total_requests)
    sample_success_b, sample_size_b = (total_blocked, total_requests)

    # check our sample against Ho for Ha != Ho
    successes = np.array([sample_success_a, sample_success_b])
    samples = np.array([sample_size_a, sample_size_b])

    # note, no need for a Ho value here - it's derived from the other parameters
    stat, p_value = proportions_ztest(count=successes, nobs=samples,  alternative='two-sided')

    # report
    file.write('Computed Test Statistic is ' + ("%.3f" % stat) + '\n')
    file.write('\n')
    file.write('Computed p-value is ' + ("%.3f" % p_value) + '\n')
    file.write('\n')

    # inference
    if p_value <= significance:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')


def two_sample_proportion_blocks():
    # can we assume anything from our sample
    significance = 0.025

    # prep file writer
    file = open(two_sample_proportion_blocks_path,"w")
    file.write('Test if the homepage blocks, subpage blocks, timeouts and errors experienced by Mullvad VPN are statistically significant compared to timeouts and errors experienced by the control connection.\n')
    file.write('\n')
    file.write('p_m is the proportion of blocks, non-2xx status codes, timeouts and errors from Mullvad requests.\n')
    file.write('p_c is the proportion of non-2xx status codes, timeouts and errors from control requests.\n')
    file.write('\n')
    file.write('H0: p_m - p_c = 0.\n')
    file.write('H1: p_m - p_c != 0.\n')
    file.write('\n')
    file.write('Alpha value set at 0.025\n')
    file.write('\n')

    # calculate values for Mullvad
    total_requests = 15000
    mullvad_not_blocked = 0

    blocks_df = pd.read_csv(block_stats_path)

    for i in range(5):
        row_df = blocks_df.iloc[i]
        mullvad_not_blocked += row_df['Not Blocked']
    
    mullvad_issues = total_requests - mullvad_not_blocked

    # calculate values for Control
    control_2xx = 0

    control_df = pd.read_csv(control_analysis_path)

    for i in range(5):
        row_df = control_df.iloc[i]
        control_2xx += row_df['2xx']
    
    control_issues = total_requests - control_2xx

    # check our sample against Ho for Ha != Ho
    successes = np.array([mullvad_issues, control_issues])
    samples = np.array([total_requests, total_requests])

    # note, no need for a Ho value here - it's derived from the other parameters
    stat, p_value = proportions_ztest(count=successes, nobs=samples,  alternative='two-sided')

    # report
    file.write('Computed Test Statistic is ' + ("%.3f" % stat) + '\n')
    file.write('\n')
    file.write('Computed p-value is ' + ("%.3f" % p_value) + '\n')
    file.write('\n')

    # inference
    if p_value <= significance:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')


def two_sample_proportion_subpages():
    # can we assume anything from our sample
    significance = 0.025

    # prep file writer
    file = open(two_sample_proportion_subpages_path,"w")
    file.write('Test if the subpage blocks experienced by Mullvad VPN are statistically significant compared to timeouts and errors experienced by the control connection.\n')
    file.write('\n')
    file.write('p_m is the proportion of domains that have either home page or subpage blocked from Mullvad requests.\n')
    file.write('p_c is the proportion of domains that have non-2xx status codes, timeouts and errors from control requests.\n')
    file.write('\n')
    file.write('H0: p_m - p_c = 0.\n')
    file.write('H1: p_m - p_c != 0.\n')
    file.write('\n')
    file.write('Alpha value set at 0.025\n')
    file.write('\n')

    # calculate values for Mullvad
    total_requests = 5000
    mullvad_not_blocked = 0

    blocks_df = pd.read_csv(subpage_blocks)

    for i in range(5):
        row_df = blocks_df.iloc[i]
        mullvad_not_blocked += row_df['Not Blocked']
        mullvad_not_blocked += row_df['No Difference']
    
    mullvad_issues = total_requests - mullvad_not_blocked

    # calculate values for Control
    control_2xx = 0

    control_df = pd.read_csv(control_domains_analysis)

    for i in range(5):
        row_df = control_df.iloc[i]
        control_2xx += row_df['2xx']
    
    control_issues = total_requests - control_2xx

    # check our sample against Ho for Ha != Ho
    successes = np.array([mullvad_issues, control_issues])
    samples = np.array([total_requests, total_requests])

    # note, no need for a Ho value here - it's derived from the other parameters
    stat, p_value = proportions_ztest(count=successes, nobs=samples,  alternative='two-sided')

    # report
    file.write('Computed Test Statistic is ' + ("%.3f" % stat) + '\n')
    file.write('\n')
    file.write('Computed p-value is ' + ("%.3f" % p_value) + '\n')
    file.write('\n')

    # inference
    if p_value <= significance:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')


def chi_squared_categories():

    # prep file writer
    file = open(chi_squared_categories_path,"w")
    file.write('Test if any category blocks more than others.\n')
    file.write('H0: independently distributed.\n')
    file.write('H1: dependently distributed.\n')
    file.write('Alpha value set at 0.05\n')
    file.write('\n \n')

    # define data table
    data = []

    categories_df = pd.read_csv(categories_path)

    for i in range(65):
        row_df = categories_df.iloc[i]
        if row_df['Blocked'] == 0:
            continue
        row = []
        row.append(row_df['Blocked'])
        row.append(row_df['Other'])
        data.append(row)

    chi2, p, dof, expected = chi2_contingency(data)
  
    # interpret p-value
    alpha = 0.05
    file.write("Categories chi2 value is " + ("%.3f" % chi2) + '\n')
    file.write("Categories p value is " + ("%.3f" % p) + '\n')
    file.write("Categories degrees of freedom: " + str(dof) + '\n')
    file.write("Categories expected frequencies table:" + '\n')
    file.write(str(expected) + '\n')
    if p <= alpha:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')




# get_stats_individual()
# get_block_stats()
# get_subpage_stats()
# chi_squared_individual()
# chi_squared_blocks()
# two_sample_proportion_unsure()
# two_sample_proportion_unsure_check()
# two_sample_proportion_blocks()
# chi_squared_subpages()
# two_sample_proportion_subpages()
# chi_squared_categories()
