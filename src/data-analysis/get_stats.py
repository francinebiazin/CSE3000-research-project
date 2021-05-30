import pandas as pd
import csv

# aggregated_path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)
mullvad_analysis_path = 'analysis/stage3/individual/mullvad-analysis.csv'
control_analysis_path = 'analysis/stage3/individual/control-analysis.csv'
aggregated_blocks = 'analysis/stage3/individual/aggregated-blocks.csv'

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
    print(mullvad_df)

    print('Mullvad 2xx average: {} (std: {})'.format(mullvad_df['2xx'].mean()/30, mullvad_df['2xx'].std()/30))
    print('Mullvad non-2xx average: {} (std: {})'.format(mullvad_df['Non-2xx'].mean()/30, mullvad_df['Non-2xx'].std()/30))
    print('Mullvad timeout average: {} (std: {})'.format(mullvad_df['Timeouts'].mean()/30, mullvad_df['Timeouts'].std()/30))
    print('Mullvad errors average: {} (std: {})'.format(mullvad_df['Errors'].mean()/30, mullvad_df['Errors'].std()/30))

    control_df = pd.read_csv(control_analysis_path)
    print(control_df)

    print('Control 2xx average: {} (std: {})'.format(control_df['2xx'].mean()/30, control_df['2xx'].std()/30))
    print('Control non-2xx average: {} (std: {})'.format(control_df['Non-2xx'].mean()/30, control_df['Non-2xx'].std()/30))
    print('Control timeout average: {} (std: {})'.format(control_df['Timeouts'].mean()/30, control_df['Timeouts'].std()/30))
    print('Control errors average: {} (std: {})'.format(control_df['Errors'].mean()/30, control_df['Errors'].std()/30))


def get_block_stats():
    blocks_df = pd.read_csv(aggregated_blocks)
    print(blocks_df)

    print('Manual check average: {} (std: {})'.format(blocks_df['Manual Check'].mean()/30, blocks_df['Manual Check'].std()/30))
    print('Blocked average: {} (std: {})'.format(blocks_df['Blocked'].mean()/30, blocks_df['Blocked'].std()/30))
    print('Maybe blocked average: {} (std: {})'.format(blocks_df['Maybe Blocked'].mean()/30, blocks_df['Maybe Blocked'].std()/30))
    print('HTTP Blocks average: {} (std: {})'.format(blocks_df['HTTP Blocks'].mean()/30, blocks_df['HTTP Blocks'].std()/30))
    print('Timeout Blocks average: {} (std: {})'.format(blocks_df['Timeout Blocks'].mean()/30, blocks_df['Timeout Blocks'].std()/30))
    print('Error Blocks average: {} (std: {})'.format(blocks_df['Error Blocks'].mean()/30, blocks_df['Error Blocks'].std()/30))
    print('Differentiated Content average: {} (std: {})'.format(blocks_df['Differentiated Content'].mean()/30, blocks_df['Differentiated Content'].std()/30))
    print('Block Page average: {} (std: {})'.format(blocks_df['Block Page'].mean()/30, blocks_df['Block Page'].std()/30))
    print('Challenge-Response Test average: {} (std: {})'.format(blocks_df['Challenge-Response Test'].mean()/30, blocks_df['Challenge-Response Test'].std()/30))

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



get_stats_individual()
get_block_stats()
