
#########################################################################################################
# Using LendingClub's loan data, please answer the below:
# 1.	create a chart showing LC's monthly loan origination volumes between 2017 and 2018
# 2.	create a chart showing monthly weighted average FICO score (by loan amount) between 2017 and 2018
# 3.	what would have been a better investments strategy during Q1 2017:
#   a. investing in all loans with FICO > 730
#   b. investing in all A, B and C graded loans
#
# LC data available here: https://www.kaggle.com/wordsforthewise/lending-club
#########################################################################################################

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# read LendingClub's loan data and build dataset
LC_df = pd.read_csv('./accepted_2007_to_2018Q4.csv')

# create a new dataset with only the relevant data
VC_df = LC_df[['issue_d', 'loan_amnt', 'fico_range_low', 'fico_range_high', 'grade', 'total_rec_int']]

# convert issue_d from string to datetime
VC_df['issue_d'] = pd.to_datetime(VC_df['issue_d'])

# reset the index
VC_df = VC_df[VC_df['issue_d'].between('2017-1-1', '2018-12-31')].reset_index(drop='true')


# ~~~~~~~~~~~~ Solution 1 ~~~~~~~~~~~~ #

# create new dataset with only the relavent data, resample by months sums
s1 = VC_df[['issue_d', 'loan_amnt']].resample('MS', on='issue_d').sum()

# plot s1 dataset as bar chart
fig1 = plt.figure(figsize=(15, 5), dpi=80)
ax1 = fig1.add_subplot()
s1.plot(kind="bar", ax=ax1)

# format xtick-labels with list comprehension
ax1.set_xticklabels([x.strftime("%m-%Y") for x in s1.index], rotation=90)

# fromat the y axis as millions USD
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / 1e6)))
ax1.bar_label(ax1.containers[0], fmt='%.3s')

# visual config of figure1
ax1.set_ylabel('M$')
ax1.set_xlabel('')
ax1.set_title('Total loan amount per month in millions USD')
ax1.margins(y=0.1)
ax1.get_legend().remove()
fig1.tight_layout()


# ~~~~~~~~~~~~ Solution 2 ~~~~~~~~~~~~ #

# create new dataset with only the relavent data
s2 = VC_df[['issue_d', 'loan_amnt', 'fico_range_low', 'fico_range_high']]

# add colume to the dataset of fico score average
s2['fico_avg'] = VC_df[['fico_range_low', 'fico_range_high']].mean(axis=1)

# define a functuin to calculate weighted average


def w_avg(df, values, weights):
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()


# group the dataset by month and apply the weighted average fico score calculation
s2 = s2.groupby('issue_d').apply(w_avg, 'fico_avg', 'loan_amnt')

# plot s2 dataset as bar chart
fig2 = plt.figure(figsize=(15, 5), dpi=80)
ax2 = fig2.add_subplot()
s2.plot(kind="bar", ax=ax2)

# format xtick-labels with list comprehension
ax2.set_xticklabels([x.strftime("%m-%Y") for x in s2.index], rotation=90)

# fromat the y axis
ax2.set_ylim([695, 715])
ax2.bar_label(ax2.containers[0], fmt='%.1f')

# visual config of figure2
ax2.set_title('monthly weighted average FICO score by loan amount')
ax2.set_xlabel('')
ax2.set_ylabel('FICO')
fig2.tight_layout()


# ~~~~~~~~~~~~ Solution 3 ~~~~~~~~~~~~ #

# create new dataset with only the relavent data needed
s3 = pd.DataFrame(index=['FICO>730', 'Grades_ABC'], columns=['sum_loan_amnt', 'sum_rec_int', 'int_per_loan'])

# create new temp datasets with only the relavent data
VC_df_FICO = VC_df[(VC_df['fico_range_low'] >= 730.0) & (VC_df['issue_d'].between('2017-1-1', '2017-3-31'))].reset_index(drop='true')
VC_df_Grades = VC_df[(VC_df['grade'] <= "C") & (VC_df['issue_d'].between('2017-1-1', '2017-3-31'))].reset_index(drop='true')


# copy calculated data to s3 dataset
s3['sum_loan_amnt']['Grades_ABC'] = VC_df_Grades['loan_amnt'].sum()
s3['sum_loan_amnt']['FICO>730'] = VC_df_FICO['loan_amnt'].sum()
s3['sum_rec_int']['Grades_ABC'] = VC_df_Grades['total_rec_int'].sum()
s3['sum_rec_int']['FICO>730'] = VC_df_FICO['total_rec_int'].sum()
s3['int_per_loan']['Grades_ABC'] = (s3['sum_rec_int']['Grades_ABC'] / s3['sum_loan_amnt']['Grades_ABC'] * 100)
s3['int_per_loan']['FICO>730'] = (s3['sum_rec_int']['FICO>730'] / s3['sum_loan_amnt']['FICO>730'] * 100)

# plot s3 dataset as two bar charts
fig3 = plt.figure(figsize=(6, 8), dpi=80)
ax3 = fig3.add_subplot(2, 1, 1)
ax4 = fig3.add_subplot(2, 1, 2)
s3[['sum_loan_amnt', 'sum_rec_int']].plot(kind="bar", ax=ax3)
s3['int_per_loan'].plot(kind="bar", ax=ax4, color="green")

# fromat the y axis
ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / 1e6)))
ax4.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
ax3.bar_label(ax3.containers[0], labels=(s3.loc['Grades_ABC'][['sum_rec_int', 'sum_loan_amnt']].values / 1e6).astype('int'))
ax3.bar_label(ax3.containers[1], labels=(s3.loc['FICO>730'][['sum_rec_int', 'sum_loan_amnt']].values / 1e6).astype('int'))
ax4.bar_label(ax4.containers[0], fmt='%.2f%%')

# fromat the x axis
fig3.autofmt_xdate(rotation=0, ha='center')

# visual config of figure3
ax3.margins(y=0.1)
ax4.margins(y=0.1)
ax3.set_ylabel('M$')
ax3.set_title('Total loan amount and intrest recived in millions USD ')
ax4.set_title('Percent of intrest recived from loan amount ')
fig3.tight_layout()

# show all the plots
plt.show()
