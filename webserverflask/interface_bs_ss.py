from flask import request, jsonify, render_template,send_file
from .flaskapp import app
from flask_cors import CORS
import jwt
import json
from pytz import timezone
import datetime
from functools import wraps
import traceback
from src.bank_statement import credit_db
from src.pay_slip import payslip_db
import os
import pandas as pd
import time
import shutil
from src.bank_statement.bank_statement import check_password_new,get_password_status,get_file_name
from src.bank_statement.combining_dataframes import combined_dataframe
from src.bank_statement.calculation_analysis import get_statement_analysis
from src.bank_statement.document_type import get_document_type
from src.bank_statement.localization import get_localization_status
from src.pay_slip.hr_processing import extract_images
import config.config as project_configs
import pprint
from absl import logging
logging._warn_preinit_stderr = 0
logging.warning('Worrying Stuff')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
cors = CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# rel_app_url = "http://0.0.0.0:5005"
# app_url = {"host": "0.0.0.0", "port": 5005}

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'static', 'data', 'input'),
    UPLOADED_PATH_SS=os.path.join(basedir, 'static', 'data', 'ss_input'),
    UPLOADED_PATH_NEW=os.path.join(basedir, 'static', 'data', 'temp'))

with open(project_configs.INTAIN_CREDIT_ATTRIBUTE_JSON) as jsFile:
    attr_config_dict = json.load(jsFile)

attrs = []

#######################################################################################################################

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        data = request.get_json()
        if not data:
            data = {}
            new_data = request.form
            data['token'] = new_data['token']
        if data is None:
            print("USER Request has no body!")
            return jsonify({'message': 'Request has no body!'}), 201

        if 'token' in data:
            token = data['token']
        else:
            print("USER Token is missing!!")
            return jsonify({'message': 'Token is missing!'}), 201

        try:
            response = credit_db.get_token(data,'user_registration')
            if response == -2:
                print("USER Token is invalid!!")
                return jsonify({'message': 'Token is invalid'}), 201

            registered_user = response['emailid']
            secret_key = response['secretkey']

            datanew = jwt.decode(token, secret_key)
            current_user = datanew['public_id']

            if not current_user == registered_user:
                return jsonify({'message': 'Not Authorized!'}), 201
        except:
            print(traceback.print_exc())
            
            return jsonify({'message': 'Token is invalid'}), 201

        return f(current_user, *args, **kwargs)
    return decorated

########################################################################################################################

def token_required_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        data = request.get_json()
        if not data:
            data = {}
            new_data = request.form
            data['token'] = new_data['token']
        if data is None:
            print("Admin Request has no body!")
            return jsonify({'message': 'Request has no body!'}), 201

        if 'token' in data:
            token = data['token']
        else:
            print("ADMIN Token is missing!!")
            return jsonify({'message': 'Token is missing!'}), 201

        try:
            registration_type = 'admin_registration'
            response = credit_db.get_token(data,registration_type)
            if response == -2:
                print("ADMIN Token is invalid!!")
                return jsonify({'message': 'Token is invalid'}), 201

            registered_user = response['emailid']
            secret_key = response['secretkey']

            datanew = jwt.decode(token, secret_key)
            current_user = datanew['public_id']

            if not current_user == registered_user:
                return jsonify({'message': 'Not Authorized!'}), 201
        except:
            print(traceback.print_exc())
            return jsonify({'message': 'Token is invalid'}), 201

        return f(current_user, *args, **kwargs)
    return decorated

########################################################################################################################

@app.route('/credit/user_register', methods=['POST'])
def register_user():
    data = request.get_json()
    print('User register data', data)
    if data is None:
        return jsonify({'message': 'Request has no body!'}), 201
    registration_type = 'user_registration'
    response = credit_db.register_user(data, registration_type)
    print('response',response)
    if response == -1:
        return jsonify({'message': 'User Details Missing!'}), 201
    elif response == -2:
        return jsonify({'message': 'User exists!'}), 201
    elif response == -4:
        return jsonify({'message': 'Mailing error!'}), 201
    return jsonify({'message': 'Registered Successfully!'}), 200

########################################################################################################################

@app.route('/credit/admin_register', methods=['POST'])
def register_admin():
    data = request.get_json()
    print('regiser', data)
    if data is None:
        return jsonify({'message': 'Request has no body!'}), 201

    registration_type = 'admin_registration'
    response = credit_db.register_admin(data, registration_type)

    if response == -1:
        return jsonify({'message': 'User Details Missing!'}), 201
    elif response == -2:
        return jsonify({'message': 'User exists!'}), 201

    elif response == -4:
        return jsonify({'message': 'Mailing error!'}), 201
    return jsonify({'message': 'Registered Successfully!'}), 200

######################################################################################################

@app.route('/credit/activate_customer', methods=['GET'])
def activate_customer():
    data = request.args
    response = credit_db.customer_activate(data)
    print('User Testing')
    if response == -2:
        return jsonify({'message': 'Invalid Company'}), 201
    elif response == -1:
        return jsonify({'message': 'Invalid User'}), 201
    elif response == -3:
        return jsonify({'message': 'Company Already Active'}), 201
    elif response == -4:
        return jsonify({'message': 'Admin Already Active'}), 201

    return jsonify({'message': 'Activated Successfully!'}), 200

######################################################################################################

@app.route('/credit/activate_admin', methods=['GET'])
def activate_admin():
    data = request.args
    response = credit_db.admin_activate(data)
    print('Admin Testing')
    if response == -2:
        return jsonify({'message': 'Invalid Company'}), 201
    elif response == -1:
        return jsonify({'message': 'Invalid Admin'}), 201
    elif response == -3:
        return jsonify({'message': 'Company Already Active'}), 201
    elif response == -4:
        return jsonify({'message': 'Admin Already Active'}), 201

    return jsonify({'message': 'Activated Successfully!'}), 200

########################################################################################################################

@app.route('/credit/user_login', methods=['POST'])
def login():
    data = request.get_json()
    print("Login Data", data)
    if data is None:
        return jsonify({'message': 'Request has no body!'}), 201

    response,secret_key = credit_db.login_user(data)

    if response == -1:
        return jsonify({'message': 'Email ID or Password Missing!', 'secretkey': secret_key}), 201
    elif response == -2:
        return jsonify({'message': 'Incorrect Details!', 'secretkey': secret_key}), 201
    elif response == -3:
        return jsonify({'message': 'Company Inactive!', 'secretkey': secret_key}), 201
    token = jwt.encode({'public_id': data['emailid'], 'exp': datetime.datetime.now() +
                        datetime.timedelta(minutes=600)}, secret_key)

    credit_db.update_token(data['emailid'], token.decode('UTF-8'), 'user_registration')

    return jsonify({'token': token.decode('UTF-8'), 'firstname': response, 'registration_type': 'user_registration'}), 200

########################################################################################################################

@app.route('/credit/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    print("Admin login checking", data)

    if data is None:
        return jsonify({'message': 'Request has no body!'}), 201

    response, secret_key = credit_db.login_admin(data)

    print("response,", response, secret_key)
    if response == -1:
        return jsonify({'message': 'Email ID or Password Missing!', 'secretkey': secret_key}), 201
    elif response == -2:
        return jsonify({'message': 'Incorrect Details!', 'secretkey': secret_key}), 201
    elif response == -3:
        return jsonify({'message': 'Company Inactive!', 'secretkey': secret_key}), 201

    token = jwt.encode({'public_id': data['emailid'], 'exp': datetime.datetime.now() +
                        datetime.timedelta(minutes=600)}, secret_key)

    credit_db.update_token(data['emailid'], token.decode('UTF-8'), 'admin_registration')
    return jsonify({'token': token.decode('UTF-8'), 'firstname': response, 'registration_type': 'admin_registration'}), 200

########################################################################################################################

@app.route('/credit/updateprofile', methods=['POST'])
@token_required
def update_profile(current_user):
    try:
        response = credit_db.profile_update(current_user)
        if not response == -2:
            return jsonify({'result': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'message': 'User does not exist!'}), 201

########################################################################################################################

@app.route('/credit/updateuser', methods=['POST'])
@token_required
def update_user(emailid):
    data = request.get_json()

    try:
        response = credit_db.user_update(emailid, data)
        if not response == -2:
            credit_db.logout_user(emailid)
            return jsonify({'message': 'Successful!'}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'message': 'User does not exist!'}), 201

########################################################################################################################

@app.route('/credit/forgotpassword', methods=['POST'])
def forgotpassword():
    data = request.get_json()

    if data is None:
        return jsonify({'message': 'Request has no body!'}), 201

    response = credit_db.forget_password(data)

    if response == -1:
        return jsonify({'message': 'Email ID Missing!'}), 201
    elif response == -2:
        return jsonify({'message': 'User does not exist!'}), 201

    secret_key = response
    token = jwt.encode({'public_id': data['emailid'], 'exp': datetime.datetime.utcnow() +
                        datetime.timedelta(minutes=5)}, secret_key)
    registration_type = 'NULL'
    credit_db.update_token(data['emailid'], token.decode('UTF-8'), registration_type)
    return jsonify({'token': token.decode('UTF-8')}), 200

########################################################################################################################

@app.route('/credit/resetpassword', methods=['POST'])
@token_required
def resetpassword(current_user):
    data = request.get_json()

    if 'password' in data:
        password = data['password']
    else:
        return jsonify({'message': 'Password Missing!'}), 201

    try:
        emailid = current_user
        credit_db.reset_password(emailid, password)
        credit_db.logout_user(emailid)
        credit_db.update_secret(emailid)
    except:
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'message': 'Password Updated!'}), 200

########################################################################################################################

@app.route('/credit/logout', methods=['POST'])
@token_required
def logoutuser(current_user):
    try:
        emailid = current_user
        credit_db.logout_user(emailid)
    except:
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'message': 'Logged out!'}), 200

#########################################################################################################################

@app.route('/credit/user_dashboard', methods=['POST'])
@token_required
def user_dashboard(current_user):
    try:
        print("Cheking User Dashboard ")
        data = request.get_json()
        response = credit_db.user_dashboard_detail(current_user, data)
        
        if not response == -2:
            return jsonify({'result': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'result': []}), 200

#########################################################################################################################

@app.route('/credit/delete_job_data', methods=['POST'])
@token_required
def delete_job_data(current_user):
    try:
        data = request.get_json()
        job_id = data['job_id']
        credit_db.delete_by_job_id(current_user,job_id)
        return jsonify({'result': 'Removed successfully'}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'result': []}), 200

#########################################################################################################################

@app.route('/credit/admin_dashboard', methods=['POST'])
@token_required_admin
def admin_dashboard(current_user):
    try:
        print("Checking Admin Dashboard ")        
        response = credit_db.admin_dashboard_detail(current_user)

        if not response == -2:
            return jsonify({'result': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201
    return jsonify({'result': []}), 200

#########################################################################################################################

@app.route('/credit/review_admin_dashboard', methods=['POST'])
@token_required_admin
def reviewed_admin_dashboard(current_user):
    try:
        print("Checking Admin Dashboard ")        
        response = credit_db.get_reviewed_admin_dashboard(current_user)

        if not response == -2:
            return jsonify({'result': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201
    return jsonify({'result': []}), 200
########################################################################################################################

@app.route('/credit/clear_documents', methods=['POST'])
@token_required
def clear_document(current_user):
    try:
        if request.method == 'POST':           
            folder_path = os.path.join(app.config['UPLOADED_PATH_NEW'],current_user)
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)
            uploaded_files = os.listdir(folder_path)
            if uploaded_files:
                for f in uploaded_files:
                    f = os.path.join(folder_path,f)
                    os.remove(f)
            return jsonify({'message': 'Cleared directory!'}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

########################################################################################################################

@app.route('/credit/delete_documents', methods=['POST'])
@token_required
def delete_document(current_user):
    try:
        if request.method == 'POST': 
            data = request.get_json()
            file_name = data['file_name']
            file_path = os.getcwd() + file_name 
            folder_path = os.path.join(app.config['UPLOADED_PATH_NEW'],current_user)
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)
            uploaded_files = os.listdir(folder_path)
            for f in uploaded_files:
                f = os.path.join(folder_path,f)
                if f == file_path:
                    os.remove(f)
            return jsonify({'message': 'successful!'}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201
        
########################################################################################################################

@app.route('/credit/upload_documents', methods=['POST'])
@token_required
def upload_document(current_user):
    try:
        if request.method == 'POST':           
            uploaded_files = request.files.getlist("file")
            print('#######################',uploaded_files,len(uploaded_files))

            folder_path = os.path.join(app.config['UPLOADED_PATH_NEW'],current_user)
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)
            for file2 in uploaded_files:
                file_name = file2.filename
                file2.save(os.path.join(folder_path, file_name))
                new_file_name1 = os.path.join(folder_path, file_name)
                new_file_name = new_file_name1.replace("'", "").replace(" ","_")
                os.rename(new_file_name1, new_file_name)
                break

            new_file_name2 = new_file_name.split('hdfc_credit/webserverflask')[-1]
            new_file_name = new_file_name.split('/')[-1]
            credit_db.save_upload_file(current_user, 'Job__0',new_file_name)
            return jsonify({'message': 'Successful!','filename' :new_file_name2 }), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

########################################################################################################################

@app.route('/credit/process_documents', methods=['POST'])
@token_required
def process_document(emailid):
    try:
        if request.method == 'POST':
            data = request.form
            print( 'process_documentsdata',data)
            applicant_id = data['applicantid']
            statementtype = data['statementtype']
            company_name = credit_db.get_company_name(emailid)
            application_id_resp = credit_db.get_application_id_detail(applicant_id,emailid)
            if application_id_resp != -2:
                return jsonify({'message': 'applicant id already exits'}), 201

            temp_folder_path = os.path.join(app.config['UPLOADED_PATH_NEW'],emailid)
            jobid_counter = credit_db.get_jobid(emailid)
            folder_name = "bank_statement_" + str(jobid_counter)
            folder_path = os.path.join(app.config['UPLOADED_PATH'], folder_name)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
            os.makedirs(folder_path,mode=0o777)

            file_size = 0
            uploaded_files = credit_db.get_upload_file(emailid,'Job__0')
            temp_files = os.listdir(temp_folder_path)
            for f in temp_files:
                f = os.path.join(temp_folder_path,f)
                shutil.move(f, folder_path)

            # uploaded_files = os.listdir(folder_path)
            print('uploaded_files >>>>> ',uploaded_files)
            if not uploaded_files:
                return jsonify({'message': 'Please select a file to upload'}), 201 

            if len(uploaded_files)>1:
                new_file_name = get_file_name(uploaded_files,folder_path)
                file = os.stat(os.path.join(folder_path, new_file_name))
                file_size += file.st_size 
                pdf_count = 'multiple'

            else:
                for file2 in uploaded_files:
                    new_file_name = os.path.join(folder_path, file2)
                    file = os.stat(os.path.join(folder_path, file2))
                    new_file_name = new_file_name.replace("'", "")
                    file_size += file.st_size     
                    pdf_count = 'single'       

            if uploaded_files:
                job_details = {}
                file_size = file_size/1000
                job_id = "Job_" + str(jobid_counter)
                job_details['emailid'] = emailid
                job_details['job_id'] = job_id
                job_details['document_name'] = folder_name

                format_date = "%Y-%m-%d %H:%M"
                now_utc = datetime.datetime.now(timezone('UTC'))
                now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))

                job_details['upload_date_time'] = now_asia.strftime(format_date)
                job_details['job_size'] = str(file_size) + " kB"
                job_details['job_priority'] = 'NULL'
                job_details['job_status'] = 'Incomplete'
                job_details['pdf_count'] = pdf_count
                job_details['file_path'] = new_file_name
                job_details['review_status'] = 'No'
                job_details['applicant_id'] = applicant_id
                job_details['companyname'] = company_name
                job_details['statementtype'] = statementtype 
                try:               
                    text, word_order,bank_name = get_document_type(new_file_name)
                except:
                    print(traceback.print_exc())
                    text, word_order,bank_name = '' , '', 'Unknown Bank'
                job_details['bank_name'] = bank_name.upper()
                print("bank_name = {} ,new_file_name = {}".format(bank_name,new_file_name))
                localization_status,readable_status,final_output_json = get_localization_status(bank_name,new_file_name)     
                job_details['localization_status'] = localization_status
                job_details['text'] = text
                job_details['word_order'] = word_order
                job_details['readable_status'] = readable_status
                credit_db.insert_job(job_details)
                
                if statementtype == 'scanned':
                    return jsonify({'message': 'Bank Name is not listed in processing bank list', 'job_id': job_id}), 201
                
                if readable_status == 'non-readable':
                    return jsonify({'message': 'Bank Name is not listed in processing bank list', 'job_id': job_id}), 201
                
                print('localization_status = {}, statementtype = {}, readable_status = {}'.format(localization_status, statementtype, readable_status))
                if localization_status == False or not final_output_json:
                    return jsonify({'message': 'Bank Name is not listed in processing bank list', 'job_id': job_id}), 201
                else:
                    output_dataframe, bank_type, excel_path, transaction_data = combined_dataframe(bank_name, final_output_json, new_file_name)
                    calculation_response, calculation_result_list = get_statement_analysis(excel_path, bank_name, bank_type, new_file_name, text, word_order)
                    new_file_name = new_file_name.split('hdfc_credit/webserverflask')[-1]
                    excel_path = excel_path.split('/hdfc_credit/webserverflask')[-1]
                    credit_db.get_single_records(emailid, job_id, new_file_name, output_dataframe,excel_path,
                                                transaction_data, calculation_response,calculation_result_list,bank_type)

            return jsonify({'message': 'Successful!', 'new_file_name': new_file_name, 'excel_path': excel_path,'job_id':job_id,'calculation_result_list':calculation_result_list}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Bank Name is not listed in processing bank list', 'job_id': job_id}), 201
        # return jsonify({'message': 'Not successful!'}), 201

    return render_template('upload_documents.html')

#########################################################################################################################

@app.route('/credit/bank_name_list', methods=['POST'])
@token_required
def bank_name_list(current_user):
    try:
        df = pd.read_excel(project_configs.INTAIN_BANK_STATEMENT_IFSC_CODE_CSV)
        bank_names = []
        for index, row in df.iterrows():
            x = row['Bank_Name']
            bank_names.append(x)
        bank_names = sorted(list(set(bank_names)))
        return jsonify({'bank_names_list': bank_names}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

############################################################################################################

@app.route('/credit/getdetailsbyid', methods=['POST'])
@token_required
def userGetDetailsByID(current_user):
    data = request.get_json()
    try:
        data = request.get_json()
        emailid = current_user

        response = credit_db.get_Details_By_ID(emailid, data['job_id'])
        print('Get Details By ID',response)

        if not response == -2:
            return jsonify({'result': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'result': []}), 200


############################################################################################################

@app.route('/credit/excel_data', methods=['POST'])
@token_required
def excel_data_by_date(emailid):
    data = request.get_json()
    try:
        data = request.get_json()
        day_start_date = data['day_start_date']
        day_end_date = data['day_end_date']

        response = credit_db.get_excel_data_by_date(emailid,day_start_date,day_end_date)
        
        print('excel data by date',response)

        if not response == -2:
            return jsonify({'excel_path': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'result': []}), 200

############################################################################################################

@app.route('/check_password', methods=['POST'])
def check_password():
    folder_path = app.config['UPLOADED_PATH']
    response, file_path = check_password_new(folder_path)
    return jsonify({'passowrd_check': response, 'file_path': file_path}), 200

@app.route('/enter_password', methods=['POST'])
def enter_password():
    data = request.get_json()
    password = data['password']
    file_path = data['file_path']
    if password == "undefined" or not password:
        status = False
    else:
        status = get_password_status(password, file_path)
    return jsonify({'password_status': status, 'file_path': file_path}), 200


@app.route('/credit/pdf_password_localization_status', methods=['POST'])
@token_required_admin
def get_pdf_password_localization_status(current_user):
    try:
        data = request.get_json()
        response = credit_db.get_localization_password_status(data)
        if not response == -2:
            return jsonify({'localization_status':response[0],'readable_status':response[1]}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful! get_pdf_password_localization_status'}), 201

    return jsonify({'result': []}), 200

########################################################################################################################

@app.route('/credit/table_localization', methods=['POST'])
@token_required_admin
def document_attributes(current_user):
    try:
        data = request.get_json()
        response = credit_db.get_localization_details(data)
        if not response == -2:
            return jsonify({'response': response[0], 'width': response[1], 'height': response[2]}), 200

    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful! doc_attributes'}), 201

    return jsonify({'result': []}), 200

################################################################################################################

@app.route('/credit/table_digitization', methods=['POST'])
@token_required_admin
def get_tablewise_data(current_user):
    data = request.get_json()
    job_id = data['job_id']
    table_coords = data['table_coords']
    try:
        response = credit_db.get_digitization_details(job_id, table_coords)
        
        if not response == -2:
            return jsonify({'response': response}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful'}), 201

    return jsonify({'result': []}), 200

################################################################################################################

@app.route('/credit/table_data', methods=['POST'])
@token_required_admin
def get_extraction_get_data(current_user):
    data = request.get_json()
    job_id = data['job_id']
    try:
        response = credit_db.save_digitized_data(job_id)
        print("RRRRRRRRRR",response)
        if not response == -2:
            return jsonify({'response': 'Successful!', 'excel': response}), 200

    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful! extraction_get_data'}), 201

    # return jsonify({'result': []}), 200

###############################################################################################

@app.route('/credit/calculations_result', methods=['POST'])
@token_required_admin
def calculations_and_ratios(current_user):
    data = request.get_json()
    job_id = data['job_id']
    try:
        response = credit_db.get_calculation_data(job_id)
        print(response)
        if not response == -2:
            return jsonify({'result': response[0],'pdf_file_path': response[3], 'calculation_csv_path': response[1],
            'calculation_result_list':response[2],'comment':response[4]}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful! calculations_api'}), 201

    return jsonify({'result': []}), 200

###############################################################################################

@app.route('/credit/calculations_result_new', methods=['POST'])
@token_required_admin
def calculations_and_ratios_new(current_user):
    data = request.get_json()
    job_id = data['job_id']
    try:
        response = credit_db.get_calculation_data_new(current_user,job_id)
        print(response)
        if not response == -2:
            return jsonify({'result': response['calculation_response'],'pdf_file_path': response['file_name'],
            'calculation_csv_path': response['excel_path'],'calculation_result_list':response['calculation_result_list']}), 200
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful! calculations_result_new'}), 201

    return jsonify({'result': []}), 200

###############################################################################################

@app.route("/credit/admin_validate", methods=['POST'])
@token_required_admin
def admin_validation_bs(admin_email):
    data = request.get_json()
    try:
        response = credit_db.bs_admin_update_job(admin_email, data)
        print(response)
        if not response == -2:
            return jsonify({'message': 'Successful!'}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401

    return jsonify({'message': 'Text-field not in DB!'}), 401


#################################################################################################
##############################   Pay Slip API's #################################################

@app.route("/payslip/user_dashboard", methods=['POST'])
@token_required
def fs_payslip_dashboard(current_user):
    try:
        response = payslip_db.userDashboardDetail(current_user)
        if not response == -2:                    
            return jsonify({'result': response}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401
    return jsonify({'result': []}), 200


###############################################################################################

@app.route("/payslip/upload", methods=['POST'])
@token_required
def fs_payslip_upload(current_user):
    single_uploads = []
    try:            
        payslip_db.delete_null_job(current_user)
        freq = request.files
        freq = list(freq._iter_hashitems())

        emailid = current_user
        job_details = {}
        jobid_counter = payslip_db.get_jobid(emailid)
        folder_name = "Job_" + str(jobid_counter)
        folder_path = os.path.join(app.config['UPLOADED_PATH_SS'], folder_name)
        print(folder_path)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)
        
        total_file_size = 0
        print("UPLOADED FILES : ", end="")
        for file_ind, (_, files_sent) in enumerate(freq):
            file_name = files_sent.filename
            file_name = file_name.encode('ascii', 'ignore').decode()
            file_name = file_name.replace(" ", "")
            print(file_name, end=", ")
            
            splited_text = os.path.splitext(file_name)
            file_name = splited_text[0] + "_" + str(file_ind) + splited_text[1]
            
            files_sent.save(os.path.join(folder_path, file_name))
            file_stat = os.stat(os.path.join(folder_path, file_name))
            total_file_size += file_stat.st_size / 1000
        print()
        format_date = "%Y-%m-%d %H:%M"
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        job_details['upload_date_time'] = now_asia.strftime(format_date)
        job_details['emailid'] = emailid
        job_details['job_id'] = str(jobid_counter)
        job_details['document_name'] = "Job_" + str(jobid_counter)
        job_details['job_size'] = str(total_file_size) + " kB"
        job_details['job_priority'] = 'Medium'
        job_details['job_status'] = 'In Process'
        job_details['batch_submitted_status'] = False
        job_details['admin_submitted'] = False
        
        payslip_db.insert_job(job_details)

        return jsonify({
            'message': 'Successful!', 
            'job_id': str(jobid_counter),
            'document_name': "Job_" + str(jobid_counter)
        }), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401

###############################################################################################


@app.route("/payslip/digitize", methods=['POST'])
@token_required
def fs_payslip_digitize(current_user):
    data = request.get_json()
    try:
        emailid = current_user
        job_dir_list = payslip_db.digitise_document(emailid, data)
        print(job_dir_list)
        if not job_dir_list == -2:
            extract_images(emailid, job_dir_list[0])
            result=payslip_db.batch_submit(emailid,data['job_id'])
            if result!=-2:
                return jsonify({'message': "Document Submitted Successfully"}), 200
        else:
            return jsonify({'message': 'Document already Digitised!'}), 401
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message':'Documents Not Submitted'}), 401
    return jsonify({'message': 'No Data uploaded!'}), 401

###############################################################################################


@app.route("/payslip/download", methods=['POST'])
@token_required
def payslip_download(current_user):
    data = request.get_json()
    try:
        emailid = current_user
        result = payslip_db.download_result(emailid, data['job_id'])
        if result!=-2:
            file_name='Job_'+data['job_id']+'.xlsx'
            return send_file(result,attachment_filename=file_name)
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message':'Error in File Download'}), 401
    return jsonify({'message': 'No File Downloaded!'}), 401

###############################################################################################

@app.route('/payslip/excel_data', methods=['POST'])
@token_required
def aggregate_excel_data(current_user):
    data = request.get_json()
    try:
        data = request.get_json()
        day_start_date = data['day_start_date']
        day_end_date = data['day_end_date']
        response = payslip_db.get_excel_data_by_date(current_user,day_start_date,day_end_date)
        if not response == -2:
            # return jsonify({'excel_path': response}), 200
            return send_file(response,attachment_filename='daily_report.xlsx')
    except:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 201

    return jsonify({'result': []}), 200


###############################################################################################

@app.route("/payslip/admin_dashboard", methods=['POST'])
@token_required_admin
def payslip_admin_dashboard(admin_email):
    try:
        response = payslip_db.adminDashboardDetail(admin_email,False)
        if not response == -2:                    
            return jsonify({'result': response}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401
    return jsonify({'result': []}), 200

###############################################################################################


@app.route("/payslip/admin_submitted_dashboard", methods=['POST'])
@token_required_admin
def payslip_admin_submitted_dashboard(admin_email):
    try:
        response = payslip_db.adminDashboardDetail(admin_email,True)
        if not response == -2:                    
            return jsonify({'result': response}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401
    return jsonify({'result': []}), 200

###############################################################################################

def format_review_response(response):
    try:
        payslip_attrs = attr_config_dict['attrs_payslip']
        payslip_attrs_names = attr_config_dict['attrs_names_payslip']
        payslip_thres_dict = attr_config_dict['thres_dict_payslip']
        payslip_result = []
        attrs = []
        attrs_names = []
        thres_dict = []
        # print("response")
        # pprint.pprint(response)
        for resp in response:
            # pprint.pprint(resp)
            finalbatchresult = {}
            finalbatchresult['fields'] = []
            for output in resp['Result']:
                fieldslist=[]
                # print("output",output)
                for j, attr in enumerate(payslip_attrs):
                    fields = {}
                    fields['varname'] = attr
                    fields['label'] = payslip_attrs_names[j]
                    fields['value'] = output["Output"][attr]
                    fields['order_id'] = j
                    fields['confidence_score'] = output["Output"][attr + '_conf']
                    fields['confidence_score_green'] = payslip_thres_dict[attr + '_thres'] * 100
                    fields['user_edited'] = 0
                    fieldslist.append(fields)
                Page = {'Result':fieldslist,'file_name':output["image"]}
                finalbatchresult['fields'].append(Page)

            finalbatchresult['file_name'] = resp['file_name']            
            #finalbatchresult['fields']['Page_0'] = fieldslist 
            finalbatchresult['image_path'] = resp['image_path']
            finalbatchresult['inv_level_conf'] = 10 # change accordingly
            # finalbatchresult['tabledata'], finalbatchresult['tabledetails'] = findEmptyTable()
            finalbatchresult['email_id'] = resp['emailid']
            payslip_result.append(finalbatchresult)
        return payslip_result

    except Exception as e:
        print(traceback.print_exc())
        return []

###############################################################################################

@app.route("/payslip/admin_review_job", methods=['POST'])
@token_required_admin
def admin_review_job(admin_email):
    data = request.get_json()
    if 'user_email' in data:
        emailid = data['user_email']
    else:
        return jsonify({'message': 'Email Id-Applicant is Missing!'}), 401
    
    try:
        response = payslip_db.admin_review_job(emailid,data['job_id'])
        if not response == -2: 
            payslip_result = format_review_response(response)#, doc_type)

            return jsonify({'result': payslip_result}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401
    return jsonify({'result': []}), 200

###############################################################################################

@app.route("/payslip/admin_validate", methods=['POST'])
@token_required_admin
def admin_validation(admin_email):
    data = request.get_json()
    try:
        #emailid = data['email_id']
        response = payslip_db.admin_update(admin_email, data)
        print(response)
        if not response == -2:
            return jsonify({'message': 'Successful!'}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401
    return jsonify({'message': 'Text-field not in DB!'}), 401

###############################################################################################
	
@app.route("/payslip/admin_submit", methods=['POST'])
@token_required_admin
def admin_submit(admin_email):
    data = request.get_json()
    if 'user_email' in data and 'job_id' in data:
        emailid = data['user_email']
        jobid=data['job_id']
    else:
        return jsonify({'message': 'Email Id of Applicant or Job Id is Missing!'}), 401
    try:
        #emailid = data['email_id']
        response = payslip_db.admin_submit(emailid, jobid)
        print(response)
        if not response == -2:
            return jsonify({'message': 'Successful!'}), 200
    except Exception as e:
        print(traceback.print_exc())
        return jsonify({'message': 'Not successful!'}), 401
    return jsonify({'message': 'Job cannot be submitted'}), 401




# if __name__ == '__main__':
#     app.run(host=app_url["host"], port=app_url["port"])
