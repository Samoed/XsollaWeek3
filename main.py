import lib_main
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

if __name__=='__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    CREDENTIALS = service_account.Credentials.from_service_account_info({
        "type": "service_account",
        "project_id": "findcsystem",
        "private_key_id": os.getenv("env_private_key_id"),
        "private_key": os.getenv("env_private_key"),
        "client_email": os.getenv("env_client_email"),
        "client_id": os.getenv("env_client_id"),
        "auth_uri": os.getenv("env_auth_uri"),
        "token_uri": os.getenv("env_token_uri"),
        "auth_provider_x509_cert_url": os.getenv("env_auth_provider_x509_cert_url"),
        "client_x509_cert_url": os.getenv("env_client_x509_cert_url")
    })
    DataFrame = lib_main.getFreshData(CREDENTIALS, 'findcsystem')
    data = lib_main.MakeDF(DataFrame)
    df = lib_main.ConcatStatus(data)
    df_channel = lib_main.MakeDFChannels(DataFrame)
    print(df.shape)
    #lib_main.insertScoreResultData(data,'findcsystem','xsolla_summer_school','score_result_status')
    #lib_main.insertScoreResultData(df,'findcsystem','xsolla_summer_school','score_result_total')
    #lib_main.insertScoreResultData(df_channel,'findcsystem','xsolla_summer_school','score_result_status_channel')