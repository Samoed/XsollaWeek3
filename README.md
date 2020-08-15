# XsollaWeek3

| Name                                | Parameters                                                   | Description                                                  | Output DF      |
| ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------- |
| getFreshData                        | Credentials - google service account object with credentials data for project<br />ProjectId - Name of project | Function for getting fresh data from BigQuery for workload scoring model | [test](#first) |
| workloadScoringByStatuses           | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) for one employee |                |
| workloadScoreStatuses               | LeftBoard - float, left boarder for confidence interval<br />RightBoard - float right boarder for confidence interval<br />CurrentNumOfTasks - integer, number of customer support agent tasks for current interval (7 days) | Function for scoring workload for current status             |                |
| insertScoreResultData               | InsertDataFrame - pandas dtaframe object, with score result data by statuses<br />ProjectId - string, name of project in google cloud platform<br />DatasetId - string, name of dataset in bigquery for raw data<br />TableId - string, name of table for raw data | Function for inserting data to BigQuery database             |                |
| MakeDF                              | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) for all employees |                |
| ConcatStatus                        | Data - pandas dataframe object, with hist data for customer support agent | Function for scoring workload by mean of statuses (In Progress and Done) for all employees |                |
| workloadScoringByStatusesAndChannel | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) and channels for one employee |                |
| MakeDFChannels                      | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) and channels for all employees |                |

## DF

### First

| id      | created    | updated    | status | assignee_id | channel     |
| ------- | ---------- | ---------- | ------ | ----------- | ----------- |
| 2140147 | 2017-01-01 | 2017-01-01 | closed | 4225872478  | help_widget |
| 2140305 | 2017-01-01 | 2017-01-01 | closed | 379332361   | help_widget |