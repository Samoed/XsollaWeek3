import lib_main
from google.oauth2 import service_account

if __name__=='__main__':
    

    DataFrame = lib_main.getFreshData(CREDENTIALS, 'findcsystem')
    data = lib_main.MakeDF(DataFrame)
    df = lib_main.ConcatStatus(data)
    df_channel = lib_main.MakeDFChannels(DataFrame)
    lib_main.insertScoreResultData(data,'findcsystem','xsolla_summer_school','score_result_status')
    # insertScoreResultData(df,'findcsystem','xsolla_summer_school','score_result_total')
    # insertScoreResultData(df_channel,'findcsystem','xsolla_summer_school','score_result_status_channel')