from google.oauth2 import service_account
import pandas_gbq

import numpy as np
import pandas as pd
import math as mt
import datetime as dt

"""[summary]
Funtion for getting fresh data from BigQuery for workload scoring model
[description]
Credentials - google service account object with credentials data for project
SqlQuery - string, sql query for BigQeury database
[example]
Input: Credentials = credentials_object
       SqlQuery = 'select * from dataset_name.table_name'
Output: id	    created_at	        updated_at	        type	  subject   description	                                                                                          status	requester_id	submitter_id   assignee_id	 id_project	 id_invoice	channel	country	 manual_category  auto_category	 subcategory   feedback_score	feedback_comment
	    2520211	2018-02-05 08:59:15	2018-02-23 13:05:39	question	        Credit card payments not working from website.	I have been trying since Thursday 1st of Jan t...	  closed	360790164527	360790164527   20890258907	 21190	     316520736	other	za	     None	          None	         None	       unoffered	    None
        2740781	2018-08-17 01:48:04	2018-09-15 11:00:15	question	        Re: error showed during paid subscription on t...	__________________________________\nType your ... closed	365082895633	951579756	   360133124587	 15174	     367443669	email	za	     None	          None	         None	       offered	        None
"""


def getFreshData(Credentials, ProjectId):
    bigquery_sql = " ".join([
                                "SELECT id, DATE(CAST(created_at AS DATETIME)) AS created, DATE(CAST(updated_at AS DATETIME)) AS updated, status, assignee_id, channel",
                                "FROM `xsolla_summer_school.customer_support`",
                                "WHERE status IN ('closed','solved')",
                                "ORDER BY updated_at"])

    dataframe = pandas_gbq.read_gbq(bigquery_sql, project_id=ProjectId, credentials=Credentials, dialect="standard")

    return dataframe


"""[summary]
Function for scoring workload by statuses (In Progress and Done) for one employee, NumOfAllDays = 63, NumOfIntervalDays = 7
[description]
Data - pandas dataframe object, with hist data for customer support agent
NumOfAllDays - integer, number of days for all hist data
NumOfIntervalDays - integer, number of days for weekly calculating interval
[example]
Input: Data = id	   created	   updated	   status	assignee_id
              2936149  2018-12-31  2019-01-30  closed	26979706288
              2936171  2018-12-31  2019-01-30  closed	26979706288
       NumOfAllDays = 63
       NumOfIntervalDays = 7
Output: assignee_id	 status	 count_last_period	count_mean_calc_period	count_sem_calc_period	score_value
        12604869947	 closed	 196	            196.62	                9.43	                1
        12604869947	 solved	 0	                0.00	                0.00	                0    
"""


def workloadScoringByStatuses(Data, NumOfAllDays=63, NumOfIntervalDays=7):
    assignee_id = np.unique(Data.assignee_id)
    assignee_id = assignee_id[0]

    # splitting by status
    statuses = np.unique(Data.status)
    assignee_id_list = []
    status_list = []
    avg_num_of_task_per_week_list = []
    ste_list = []
    num_tasks_per_current_week_list = []
    score_for_status_list = []
    for status in statuses:
        dataframe_status = Data[(Data.status == str(status))][:]

        # time borders params
        curr_date = dt.datetime.strptime(str('2017-04-01'), '%Y-%m-%d')
        curr_date = curr_date.date()
        delta = dt.timedelta(days=NumOfAllDays)
        first_date = curr_date - delta

        # time interval params
        delta_interval = dt.timedelta(days=NumOfIntervalDays)
        first_interval = first_date + delta_interval

        num_of_intervals = int(NumOfAllDays / NumOfIntervalDays)
        num_tasks_per_week = []
        for i in range(0, num_of_intervals):
            interval = dataframe_status[(dataframe_status.updated >= str(first_date)) & (
                        dataframe_status.updated <= str(first_interval))][:]
            first_date = first_date + delta_interval
            first_interval = first_interval + delta_interval

            if i != (num_of_intervals - 1):
                num_of_tasks = len(np.unique(interval['id']))
                num_tasks_per_week.append(num_of_tasks)  # history number of tasks
            else:
                num_tasks_per_current_week = len(np.unique(interval['id']))  # currently number of tasks

        avg_num_of_task_per_week = round(np.mean(num_tasks_per_week), 2)

        # squared deviations
        x_values = []
        for num in num_tasks_per_week:
            x = round((num - avg_num_of_task_per_week) ** 2, 2)
            x_values.append(x)

        # data sampling statistics
        x_sum = round(sum(x_values), 2)  # sum of squared deviations
        dispersion = round(x_sum / (num_of_intervals - 1), 2)  # dispersion
        std = round(mt.sqrt(dispersion), 2)  # standart deviation for sample
        ste = round(std / mt.sqrt(num_of_intervals), 2)  # standart error for sample

        # confidence interval
        left_border = int(avg_num_of_task_per_week - ste)
        right_border = int(avg_num_of_task_per_week + ste)

        # workload scoring for status
        score_for_status = workloadScoreStatuses(left_border, right_border, num_tasks_per_current_week)
        assignee_id_list.append(assignee_id)
        status_list.append(status)
        avg_num_of_task_per_week_list.append(avg_num_of_task_per_week)
        ste_list.append(ste)
        num_tasks_per_current_week_list.append(num_tasks_per_current_week)
        score_for_status_list.append(score_for_status)

    score_data = {"assignee_id": assignee_id_list, "status": status_list,
                  "count_last_period": num_tasks_per_current_week_list,
                  "count_mean_calc_period": avg_num_of_task_per_week_list, "count_sem_calc_period": ste_list,
                  "score_value": score_for_status_list}
    scores = pd.DataFrame(data=score_data)

    return scores


"""[summary]
Function for scoring workload for current status
[description]
LeftBoard - float, left boarder for confidence interval
RightBoard - float right boarder for confidence interval
CurrentNumOfTasks - integer, number of customer support agent tasks for current interval (7 days)
[example]
Input: LeftBoard = 187
       RightBoard = 206
       CurrentNumOfTasks = 196
Output: 1
"""


def workloadScoreStatuses(LeftBoard, RightBoard, CurrentNumOfTasks):
    if (LeftBoard == 0) & (CurrentNumOfTasks == 0) & (RightBoard == 0):
        score = 0
    elif (CurrentNumOfTasks >= 0) & (CurrentNumOfTasks < LeftBoard):
        score = 0
    elif (CurrentNumOfTasks >= LeftBoard) & (CurrentNumOfTasks <= RightBoard):
        score = 1
    else:
        score = 2
    return score


"""[summary]
Function for inserting data to BigQuery database
[description]
InsertDataFrame - pandas dtaframe object, with score result data by statuses
ProjectId - string, name of project in google cloud platform 
DatasetId - string, name of dataset in bigquery for raw data
TableId - string, name of table for raw data
[example]
Input: InsertDataFrame = assignee_id	status	count_last_period	count_mean_calc_period	count_sem_calc_period	score_value
                         11527290367	closed	163	                140.38	                12.4	                2
                         11527290367	solved	0	                0.00	                0.0 	                0
       ProjectId = 'test-gcp-project'
       DatasetId = 'test_dataset'
       TableId = 'test_table'
"""


def insertScoreResultData(InsertDataFrame, ProjectId, DatasetId, TableId):
    destination_table = f"{DatasetId}.{TableId}"

    res_df = pd.DataFrame()
    res_df['assignee_id'] = InsertDataFrame['assignee_id'].astype('int64')

    if TableId == 'score_result_status':
        res_df['status'] = InsertDataFrame['status'].astype('str')
        res_df['count_last_period'] = InsertDataFrame['count_last_period'].astype('int')
        res_df['count_mean_calc_period'] = InsertDataFrame['count_mean_calc_period'].astype('float')
        res_df['count_sem_calc_period'] = InsertDataFrame['count_sem_calc_period'].astype('float')
        res_df['score_value'] = InsertDataFrame['score_value'].astype('int')
    elif TableId == 'score_result_total':
        res_df['score_value'] = InsertDataFrame['score_value'].astype('float')
    elif TableId == 'score_result_status_channel':
        res_df['status'] = InsertDataFrame['status'].astype('str')
        res_df['channel'] = InsertDataFrame['channel'].astype('str')
        res_df['count_last_period'] = InsertDataFrame['count_last_period'].astype('int')
        res_df['count_mean_calc_period'] = InsertDataFrame['count_mean_calc_period'].astype('float')
        res_df['count_sem_calc_period'] = InsertDataFrame['count_sem_calc_period'].astype('float')
        res_df['score_value'] = InsertDataFrame['score_value'].astype('int')

    res_df['developer'] = 'roman.solomatin'
    res_df['developer'] = res_df['developer'].astype('str')
    pandas_gbq.to_gbq(res_df, destination_table=destination_table, project_id=ProjectId, if_exists='append')


"""
[summary]
Function for scoring workload by statuses (In Progress and Done) for all employees
[description]
Data - pandas dataframe object, with hist data for customer support agent
NumOfAllDays - integer, number of days for all hist data
NumOfIntervalDays - integer, number of days for weekly calculating interval
[example]
Input: Data = id	   created	   updated	   status	assignee_id
              2936149  2018-12-31  2019-01-30  closed	26979706288
              2936171  2018-12-31  2019-01-30  closed	26979706288
              2140360  2017-01-01  2017-01-01  closed 	12604869947
              2140375  2017-01-01  2017-01-01  closed 	12604869947
       NumOfAllDays = 63
       NumOfIntervalDays = 7
Output: assignee_id	status	count_last_period	count_mean_calc_period	count_sem_calc_period	score_value
        11527290367	closed	163	                140.38	                12.4	                2
        11527290367	solved	0	                0.00	                0.0 	                0
        4225872478 	closed 	46 	                246.38               	37.48 	                0
        4225872478 	solved 	0 	                0.00 	                0.00                 	0
"""


def MakeDF(DataFrame, NumOfAllDays: int = 63, NumOfIntervalDays: int = 7):
    data = pd.DataFrame()
    tmp = 0
    for i in DataFrame['assignee_id'].unique():
        user = DataFrame[DataFrame.assignee_id == i]
        result = workloadScoringByStatuses(user, NumOfAllDays, NumOfIntervalDays)
        if tmp == 0:
            data = result
            tmp += 1
        else:
            data = pd.concat([data, result], ignore_index=True)
        tmp += 1
    return data


"""
[summary]
Function for scoring workload by mean of statuses (In Progress and Done) for all employees
[description]
Data - pandas dataframe object, with hist data for customer support agent
[example]
Input:  assignee_id	status	count_last_period	count_mean_calc_period	count_sem_calc_period	score_value
        11527290367	closed	163	                140.38	                12.4	                2
        11527290367	solved	0	                0.00	                0.0 	                0
        4225872478 	closed 	46 	                246.38               	37.48 	                0
        4225872478 	solved 	0 	                0.00 	                0.00                 	0
Output: assignee_id 	score_value
        4225872478 	    0.0
        379332361 	    0.0
        12604869947 	0.5
        14318037588 	0.0
"""


def ConcatStatus(data):
    df = pd.DataFrame(columns=["assignee_id", "score_value"])
    lis = []
    for user in data['assignee_id'].unique():
        ans = sum(data[data['assignee_id'] == user]['score_value']) / data[data['assignee_id'] == user].shape[0]
        lis.append([user, ans])

    df = pd.DataFrame(lis, columns=["assignee_id", "score_value"])
    return df


##################################################################################
# Channels
##################################################################################
"""[summary]
Function for scoring workload by statuses (In Progress and Done) for one employee, NumOfAllDays = 63, NumOfIntervalDays = 7
[description]
Data - pandas dataframe object, with hist data for customer support agent
NumOfAllDays - integer, number of days for all hist data
NumOfIntervalDays - integer, number of days for weekly calculating interval
[example]
Input: Data = id	   created	   updated	   status	assignee_id
              2936149  2018-12-31  2019-01-30  closed	26979706288
              2936171  2018-12-31  2019-01-30  closed	26979706288
       NumOfAllDays = 63
       NumOfIntervalDays = 7
Output: assignee_id	 status	 channel    count_last_period	count_mean_calc_period	count_sem_calc_period	score_value
        12604869947	 closed	 sms        196 	            196.62	                9.43	                1
        12604869947	 solved	 call       0	                0.00	                0.00	                0    
"""


def workloadScoringByStatusesAndChannel(Data, NumOfAllDays=63, NumOfIntervalDays=7):
    assignee_id = np.unique(Data.assignee_id)
    assignee_id = assignee_id[0]

    # splitting by status
    statuses = np.unique(Data.status)
    channels = Data['channel'].unique()
    assignee_id_list = []
    status_list = []
    channel_list = []
    avg_num_of_task_per_week_list = []
    ste_list = []
    num_tasks_per_current_week_list = []
    score_for_status_list = []
    score_for_channel_list = []
    for status in statuses:
        dataframe_status = Data[(Data.status == str(status))][:]
        for channel in channels:
            dataframe_channel = dataframe_status[(dataframe_status['channel'] == str(channel))][:]
            # time borders params
            curr_date = dt.datetime.strptime(str('2017-04-01'), '%Y-%m-%d')
            curr_date = curr_date.date()
            delta = dt.timedelta(days=NumOfAllDays)
            first_date = curr_date - delta

            # time interval params
            delta_interval = dt.timedelta(days=NumOfIntervalDays)
            first_interval = first_date + delta_interval

            num_of_intervals = int(NumOfAllDays / NumOfIntervalDays)
            num_tasks_per_week = []
            for i in range(0, num_of_intervals):
                interval = dataframe_channel[(dataframe_channel.updated >= str(first_date)) & (
                            dataframe_channel.updated <= str(first_interval))][:]
                first_date = first_date + delta_interval
                first_interval = first_interval + delta_interval

                if i != (num_of_intervals - 1):
                    num_of_tasks = len(np.unique(interval['id']))
                    num_tasks_per_week.append(num_of_tasks)  # history number of tasks
                else:
                    num_tasks_per_current_week = len(np.unique(interval['id']))  # currently number of tasks

            avg_num_of_task_per_week = round(np.mean(num_tasks_per_week), 2)

            # squared deviations
            x_values = []
            for num in num_tasks_per_week:
                x = round((num - avg_num_of_task_per_week) ** 2, 2)
                x_values.append(x)

            # data sampling statistics
            x_sum = round(sum(x_values), 2)  # sum of squared deviations
            dispersion = round(x_sum / (num_of_intervals - 1), 2)  # dispersion
            std = round(mt.sqrt(dispersion), 2)  # standart deviation for sample
            ste = round(std / mt.sqrt(num_of_intervals), 2)  # standart error for sample

            # confidence interval
            left_border = int(avg_num_of_task_per_week - ste)
            right_border = int(avg_num_of_task_per_week + ste)

            # workload scoring for status
            score_for_status = workloadScoreStatuses(left_border, right_border, num_tasks_per_current_week)
            assignee_id_list.append(assignee_id)

            status_list.append(status)
            channel_list.append(channel)
            avg_num_of_task_per_week_list.append(avg_num_of_task_per_week)
            ste_list.append(ste)
            num_tasks_per_current_week_list.append(num_tasks_per_current_week)
            score_for_status_list.append(score_for_status)

    score_data = {"assignee_id": assignee_id_list, "status": status_list, "channel": channel_list,
                  "count_last_period": num_tasks_per_current_week_list,
                  "count_mean_calc_period": avg_num_of_task_per_week_list, "count_sem_calc_period": ste_list,
                  "score_value": score_for_status_list}
    scores = pd.DataFrame(data=score_data)

    return scores


"""
[summary]
Function for scoring workload by statuses (In Progress and Done) for all employees
[description]
Data - pandas dataframe object, with hist data for customer support agent
NumOfAllDays - integer, number of days for all hist data
NumOfIntervalDays - integer, number of days for weekly calculating interval
[example]
Input: Data = id	   created	   updated	   status	assignee_id
              2936149  2018-12-31  2019-01-30  closed	26979706288
              2936171  2018-12-31  2019-01-30  closed	26979706288
              2140360  2017-01-01  2017-01-01  closed 	12604869947
              2140375  2017-01-01  2017-01-01  closed 	12604869947
       NumOfAllDays = 63
       NumOfIntervalDays = 7
Output: assignee_id	status  channel 	count_last_period	count_mean_calc_period	count_sem_calc_period	score_value
        4225872478 	closed 	help_widget	12   	            43.62 	                5.97                 	0
        4225872478 	closed 	facebook 	1 	                1.25 	                0.59 	                1
        4225872478 	closed 	other 	    1 	                0.75 	                0.43 	                1
        4225872478 	closed 	chat 	    22 	                143.75 	                26.80                	0
"""


def MakeDFChannels(DataFrame, NumOfAllDays: int = 63, NumOfIntervalDays: int = 7):
    data = pd.DataFrame()
    tmp = 0
    for i in DataFrame['assignee_id'].unique():
        user = DataFrame[DataFrame.assignee_id == i]
        result = workloadScoringByStatusesAndChannel(user, NumOfAllDays, NumOfIntervalDays)
        if tmp == 0:
            data = result
            tmp += 1
        else:
            data = pd.concat([data, result], ignore_index=True)
        tmp += 1
    return data