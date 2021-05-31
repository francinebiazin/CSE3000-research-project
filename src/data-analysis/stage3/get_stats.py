import pandas as pd
import numpy as np
import csv
from scipy.stats import chi2_contingency, ttest_ind
import scipy.stats.distributions as dist

# aggregated_path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)
mullvad_analysis_path = 'analysis/stage3/individual/mullvad-analysis.csv'
control_analysis_path = 'analysis/stage3/individual/control-analysis.csv'
aggregated_blocks = 'analysis/stage3/individual/aggregated-blocks.csv'
block_stats_path = 'analysis/stage3/stats/blocks-analysis.csv'
mullvad_stats_path = 'analysis/stage3/stats/mullvad-analysis.csv'
control_stats_path = 'analysis/stage3/stats/control-analysis.csv'
chi_squared_individual_path = 'analysis/stage3/stats/chi-squared-individual.txt'
chi_squared_blocks_path = 'analysis/stage3/stats/chi-squared-blocks.txt'
two_sample_proportion_unsure_path = 'analysis/stage3/stats/two-sample-proportion-unsure.txt'

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

    data = {
        'Date': 'Averages',
        'Manual Check': "%.2f" % (blocks_df['Manual Check'].mean()/30),
        'Blocked': "%.2f" % (blocks_df['Blocked'].mean()/30),
        'Maybe Blocked': "%.2f" % (blocks_df['Maybe Blocked'].mean()/30),
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
        row.append(row_df['Blocked'])
        row.append(row_df['Maybe Blocked'])
        row.append(3000 - row_df['Blocked'] - row_df['Maybe Blocked'])
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
    

def two_sample_proportion_unsure():

    # following https://medium.com/analytics-vidhya/testing-a-difference-in-population-proportions-in-python-89d57a06254

    # prep file writer
    file = open(two_sample_proportion_unsure_path,"w")
    file.write('Test if the requests that could not be identified as blocks are statistically significant.\n')
    file.write('\n')
    file.write('p_b is the proportion of blocked requests when we count unsure as blocked.\n')
    file.write('p_nb is the proportion of blocked requests when we count unsure as not blocked.\n')
    file.write('\n')
    file.write('H0: p_b - p_nb = 0.\n')
    file.write('H1: p_b - p_nb != 0.\n')
    file.write('\n')
    file.write('Alpha value set at 0.10 (a standard for two tailed tests)\n')
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

    # columns: count unsure as blocked, count unsure as not blocked
    # rows: blocked, not blocked
    table = [
        [total_blocked + total_unsure, total_blocked],
        [total_requests - (total_blocked + total_unsure), total_requests - total_blocked]
    ]

    # transform table into proportions
    proportions = []
    for row in table:
        proportions.append(list(map(lambda x: x/total_requests, row)))
    file.write('Proportions table:\n')
    file.write(str(proportions) + '\n')
    file.write('\n')

    # Standard error for difference in Population Proportions
    total_proportion_blocked = sum(proportions[0])/2
    variance = total_proportion_blocked * (1 - total_proportion_blocked)
    standard_error = np.sqrt(variance * (1 / total_requests + 1 / total_requests))
    file.write('Sample Standard Error: ' + ("%.3f" % standard_error) + '\n')
    file.write('\n')

    # Calculate the test statistic 
    best_estimate = (proportions[0][0] - proportions[0][1])     # p_b - p_nb
    file.write('The best estimate is ' + ("%.3f" % best_estimate) + '\n')
    file.write('\n')
    hypothesized_estimate = 0
    test_stat = (best_estimate-hypothesized_estimate) / standard_error
    file.write('Computed Test Statistic is ' + ("%.3f" % test_stat) + '\n')
    file.write('\n')

    # Calculate the  p-value
    p_value = 2 * dist.norm.cdf(-np.abs(test_stat))     # multiplied by two because it is a two tailed testing
    file.write('Computed p-value is ' + ("%.3f" % p_value) + '\n')
    file.write('\n')
  
    # interpret p-value
    alpha = 0.10
    if p_value <= alpha:
        file.write('Dependent (reject H0)' + '\n')
    else:
        file.write('Independent (H0 holds true)' + '\n')


def two_sample_proportion_unsure_ttest():

    # add all data points into contingency table
    total_requests = 15000
    total_blocked = 0
    total_unsure = 0

    blocks_df = pd.read_csv(block_stats_path)

    for i in range(5):
        row_df = blocks_df.iloc[i]
        total_blocked += row_df['Blocked']
        total_unsure += row_df['Maybe Blocked']

    # columns: count unsure as blocked, count unsure as not blocked
    # rows: blocked, not blocked
    table = [
        [total_blocked + total_unsure, total_requests - (total_blocked + total_unsure)],
        [total_blocked, total_requests - total_blocked]
    ]

    t_statistic, p_value = ttest_ind(table[0], table[1], equal_var=False)

    print('Test statistic: ' + str(t_statistic))
    print('p-value: ' + str(p_value))

    # interpret p-value
    alpha = 0.10
    if p_value <= alpha:
        print('Dependent (reject H0)')
    else:
        print('Independent (H0 holds true)')





# get_stats_individual()
# get_block_stats()
# chi_squared_individual()
# chi_squared_blocks()
# two_sample_proportion_unsure()
two_sample_proportion_unsure_ttest()
