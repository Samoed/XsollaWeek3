# XsollaWeek3

| Name                                | Parameters                                                   | Description                                                  | Output                                           |
| ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------ |
| getFreshData                        | Credentials - google service account object with credentials data for project<br />ProjectId - Name of project | Function for getting fresh data from BigQuery for workload scoring model | [DataFrame](#getFreshData)                       |
| workloadScoringByStatuses           | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) for one employee | [DataFrame](#workloadScoringByStatuses)          |
| workloadScoreStatuses               | LeftBoard - float, left boarder for confidence interval<br />RightBoard - float right boarder for confidence interval<br />CurrentNumOfTasks - integer, number of customer support agent tasks for current interval (7 days) | Function for scoring workload for current status             | int - workload status                            |
| insertScoreResultData               | InsertDataFrame - pandas dtaframe object, with score result data by statuses<br />ProjectId - string, name of project in google cloud platform<br />DatasetId - string, name of dataset in bigquery for raw data<br />TableId - string, name of table for raw data | Function for inserting data to BigQuery database             |                                                  |
| MakeDF                              | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) for all employees | [DataFrame](#workloadScoringByStatuses)          |
| ConcatStatus                        | Data - pandas dataframe object, with hist data for customer support agent | Function for scoring workload by mean of statuses (In Progress and Done) for all employees | [DataFrame](#concatStatus)                       |
| workloadScoringByStatusesAndChannel | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) and channels for one employee | [DataFrame](workloadScoringByStatusesAndChannel) |
| MakeDFChannels                      | Data - pandas dataframe object, with hist data for customer support agent<br />NumOfAllDays - integer, number of days for all hist data<br />NumOfIntervalDays - integer, number of days for weekly calculating interval | Function for scoring workload by statuses (In Progress and Done) and channels for all employees | [DataFrame](workloadScoringByStatusesAndChannel) |

## DF

### getFreshData

| id      | created    | updated    | status | assignee_id | channel     |
| ------- | ---------- | ---------- | ------ | ----------- | ----------- |
| 2140147 | 2017-01-01 | 2017-01-01 | closed | 4225872478  | help_widget |
| 2140305 | 2017-01-01 | 2017-01-01 | closed | 379332361   | help_widget |

| Name        | Type   | Describe                      |
| ----------- | ------ | ----------------------------- |
| id          | int    | id of request                 |
| created     | date   | date of request               |
| updated     | date   | date request was closed       |
| status      | string | request status (opened/close) |
| assignee_id | int    | id of support agent           |
| channel     | string | channel of request            |



### workloadScoringByStatuses

| assignee_id | status | count_last_period | count_mean_calc_period | count_sem_calc_period | score_value |
| ----------- | ------ | ----------------- | ---------------------- | --------------------- | ----------- |
| 4225872478  | closed | 12                | 43.62                  | 5.97                  | 0           |
| 4225872478  | opened | 1                 | 1.25                   | 0.59                  | 1           |

| Name                   | Type   | Describe                           |
| ---------------------- | ------ | ---------------------------------- |
| assignee_id            | int    | id of support agent                |
| status                 | string | request status (opened/close)      |
| count_last_period      | int    | requests ~~solved~~ in last period |
| count_mean_calc_period | float  | mean number of tasks per period    |
| count_sem_calc_period  | float  | standart error for sample          |
| score_value            | int    | workload score                     |

### concatStatus

| assignee_id | score_value |
| ----------- | ----------- |
| 4225872478  | 0.0         |
| 379332361   | 0.0         |

| Name        | Type  | Describe            |
| ----------- | ----- | ------------------- |
| assignee_id | int   | id of support agent |
| score_value | float | workload score      |

### workloadScoringByStatusesAndChannel

| assignee_id | status | channel | count_last_period | count_mean_calc_period | count_sem_calc_period | score_value |
| ----------- | ------ | ------- | ----------------- | ---------------------- | --------------------- | ----------- |
| 4225872478  | closed | sms     | 12                | 43.62                  | 5.97                  | 0           |
| 4225872478  | opened | call    | 1                 | 1.25                   | 0.59                  | 1           |

| Name                   | Type   | Describe                           |
| ---------------------- | ------ | ---------------------------------- |
| assignee_id            | int    | id of support agent                |
| status                 | string | request status (opened/close)      |
| channel                | string | channel of request                 |
| count_last_period      | int    | requests ~~solved~~ in last period |
| count_mean_calc_period | float  | mean number of tasks per period    |
| count_sem_calc_period  | float  | standard error for sample          |
| score_value            | int    | workload score                     |