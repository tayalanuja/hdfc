import os

DATABASE_CONFIG = {
            'db_vm': 'localhost',
            'db_port': '27017',
            'db_name': 'ind_credit'
}

API_KEY = ["NOKS0PMW2V-KP8625Z8PG","NKOBMJJAM4-LTY-L312C3GHQLX064V"]
RAZOR_KEY="rzp_test_lTC2a61xb5plrG"
RAZOR_SECRET="Dp5DcbF3jSnctiZmCtcmx5MX"
# INTAIN_EMAIL="rahul.kendre@in-d.ai"
# INTAIN_PASSWD="Rahul@2830"

INTAIN_EMAIL = "no-reply@in-d.ai"
INTAIN_PASSWD = "Intain@2019"
# BASE_URL = os.environ.get('BASE_URL',"http://0.0.0.0:5005")
# BASE_URL = os.environ.get('BASE_URL',"http://35.209.125.251:3000")
BASE_URL = os.environ.get('BASE_URL',"https://credit.in-d.ai/hdfc")

MONGODB_URL = os.environ.get('MONGODB_URL','localhost')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
MONGODB_NAME = 'ind_credit'

# Project_variables
INTAIN_BANK_STATEMENT_PROJECT_NAME = 'ind_credit'

# MongoDB variables
INTAIN_BANK_STATEMENT_MONGODB_URL='localhost'

INTAIN_BANK_STATEMENT_MONGODB_PORT=27017
INTAIN_BANK_STATEMENT_MONGODB_DATABASE_NAME='intain_db'
INTAIN_BANK_STATEMENT_MONGODB_COLLECTION_NAME='cert_extract_col'

# Project variables
INTAIN_BANK_STATEMENT_ROOT_DIR=os.getcwd()
INTAIN_BANK_STATEMENT_TEMP_DIR=os.path.join('/tmp',INTAIN_BANK_STATEMENT_PROJECT_NAME)

# Google vision variables
INTAIN_BANK_STATEMENT_GOOGLE_APPLICATION_CREDENTIALS = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/apikey.json')

# Upload dir variables
INTAIN_BANK_STATEMENT_UPLOAD_DIR_FLASK_REL='static/uploads'
INTAIN_BANK_STATEMENT_UPLOAD_DIR_ABS = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'webserverflask',INTAIN_BANK_STATEMENT_UPLOAD_DIR_FLASK_REL)

#Template Folder
INTAIN_BANK_STATEMENT_TEMPLATES=os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'webserverflask/templates/')

# Required CSV files
INTAIN_BANK_STATEMENT_IFSC_CODE_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/IFSC_Code.xlsx')
INTAIN_BANK_STATEMENT_LOCALIZATION_BANK_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/localization_bank.csv')
# INTAIN_BANK_STATEMENT_IFSC_CODE_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/IFSC_Code.csv')
INTAIN_BANK_STATEMENT_FILE_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/coordinates.csv')
INTAIN_BANK_STATEMENT_TABLE_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/table.csv')
INTAIN_BANK_STATEMENT_PARA_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/para.csv')
INTAIN_BANK_STATEMENT_TXNDATA_JSON = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config','txndata.json')
INTAIN_BANK_STATEMENT_COORDINATE_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/coordinate.csv')
INTAIN_BANK_STATEMENT_TXNDATA_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config','txn_data.csv')
INTAIN_BANK_STATEMENT_DOCUMENT_HTML = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/documentselection.html')

# Calculation CSV
INTAIN_BANK_STATEMENT_KEYWORDS_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/keywords.xlsx')
INTAIN_BANK_STATEMENT_BANK_TAGS_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/bank_taglines.xlsx')
# INTAIN_BANK_STATEMENt_HEADERS_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/headers.csv')
INTAIN_BANK_STATEMENt_HEADERS_CSV = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/headers.csv')
INTAIN_BANK_STATEMENt_FORMULA = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/formula.ods')

INTAIN_BANK_STATEMENT_INTERFACE_GRAPH = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/model_weights/frozen_inference_graph.pb')
INTAIN_BANK_STATEMENT_LABEL_MAP = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/model_weights/trial_label_map.pbtxt')

INTAIN_CREDIT_INTERFACE_GRAPH = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/model_weights/frozen_inference_graph_payslip.pb')
INTAIN_CREDIT_LABEL_MAP = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config/model_weights/objectdetection_payslip.pbtxt')
INTAIN_CREDIT_ATTRIBUTE_JSON = os.path.join(INTAIN_BANK_STATEMENT_ROOT_DIR,'config','attribute_config.json')

