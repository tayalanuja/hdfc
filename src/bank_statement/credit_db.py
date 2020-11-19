from pymongo import MongoClient
import traceback
import os,json
import re
import openpyxl
import pandas as pd
import shutil
from datetime import datetime
from datetime import timedelta
from flask import jsonify
from config.config import MONGODB_NAME,MONGODB_PORT,MONGODB_URL,API_KEY,RAZOR_KEY,RAZOR_SECRET,INTAIN_EMAIL,INTAIN_PASSWD,BASE_URL
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .calculation_analysis import get_statement_analysis
from .function_library import get_valid_format
from .combining_dataframes import combined_dataframe
from datetime import datetime
from pytz import timezone
from .bank_statement import get_bank_statement,extraction_data,extraction_column,check_password_new,get_file_name,get_password_status
mongo_db_client = None

########################################################################################################################
def register_user(request_data,registration_type):
    user_attributes = ['firstname','lastname','password','emailid','phone','companyname']
    for attribute in user_attributes:
        if attribute not in request_data:
            return -1
        
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']

    resp = collection.find_one({'emailid':request_data['emailid'],'registration_type':registration_type})
    if not resp:
        secret_key = ""
        for attribute in user_attributes[:6]:
            if attribute != 'password':
                secret_key = secret_key + str(request_data[attribute]).replace(' ','')
        request_data['secretkey'] = secret_key
        request_data['status']='Inactive'
        request_data['registration_type'] = registration_type
        collection.insert_one(request_data)

        resp = collection.find_one({'secretkey':secret_key,'emailid':request_data['emailid']})

        port = 465  # For SSL
        sender_email=INTAIN_EMAIL
        receiver_email = request_data['emailid']
        
        activate_url = BASE_URL + "/activate_customer?emailid=" + receiver_email + "&secretkey=" + secret_key 
        print("Activate URL >>>> ",activate_url)
        message = MIMEMultipart("alternative")
        message["Subject"] = "IN-D Credit: Activation Required"
        message["From"] = INTAIN_EMAIL
        message["To"] = receiver_email
        
        text = """\
        click to activate """ + activate_url
        
        htmltext = """\
        <html>
        <head></head>
        <body>
            <div class="container justify-content-center" style="margin: 50px 100px">
    
                <h3 style="font-size: 26px; color: #2b2b2b; text-align: center ">
                    Activate your IN-D Credit account
                </h3>
    
                <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
    
                <p style="font-size: 18px; color: #4c4c4e; text-align: left;font-weight: bold; padding-top: 10px">
                    Hello , 
                </p>
    
                <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                    To activate your IN-D Credit account simply click the button below. 
                    Once clicked your request will be processed and verified and you 
                    will be redirected to the IN-D Credit Web application.
                </p>
    
                <div class="wrapper" style="margin-top: 20px; margin-bottom: 20px; text-align: center">
                    <a href=" """ + activate_url + """ "><button style="background-color: #0085d8; border: 1px solid #0085d8; color: white; font-size: 14px; height: 35px; width: 200px; cursor: pointer;">
                        ACTIVATE ACCOUNT
                    </button></a> 
                </div>
    
                <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                    You are receiving this email because you created an IN-D Credit account. 
                    If you believe you have received this email in error, please mail us 
                    to <a href="#">explore@in-d.ai</a> 
                </p>
    
                <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
                
    
            </div>
        </body>
        </html>
        """
        
        mail_body=MIMEText(htmltext,"html")
        
        message.attach(mail_body)
        
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(INTAIN_EMAIL, INTAIN_PASSWD)
            server.sendmail(sender_email,receiver_email,message.as_string())
           
        
    else:
        mongo_db_client.close()  
        return -2

    mongo_db_client.close()
    return 1

########################################################################################################################

def register_admin(request_data,registration_type):
    user_attributes = ['firstname','lastname','password','emailid','phone','companyname','jobtitle','answer','question']
    for attribute in user_attributes:
        if attribute not in request_data:
            return -1
        
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']

    resp = collection.find_one({'emailid':request_data['emailid'],'registration_type':registration_type})
    if not resp:
        secret_key = ""
        for attribute in user_attributes[:6]:
            if attribute != 'password':
                secret_key = secret_key + str(request_data[attribute]).replace(' ','')
        request_data['secretkey'] = secret_key
        request_data['status']='Inactive'
        request_data['registration_type'] = registration_type
        collection.insert_one(request_data)

        resp = collection.find_one({'secretkey':secret_key,'emailid':request_data['emailid']})

        port = 465  # For SSL
        sender_email=INTAIN_EMAIL
        receiver_email = request_data['emailid']
        
        activate_url = BASE_URL + "/activate_admin?emailid=" + receiver_email + "&secretkey=" + secret_key 
        message = MIMEMultipart("alternative")
        message["Subject"] = "IN-D Credit: Admin Activation Required"
        message["From"] = INTAIN_EMAIL
        message["To"] = receiver_email
 
        text = """\
        click to activate """ + activate_url
        
        htmltext = """\
        <html>
        <head></head>
        <body>
            <div class="container justify-content-center" style="margin: 50px 100px">
    
                <h3 style="font-size: 26px; color: #2b2b2b; text-align: center ">
                    Activate your IN-D Credit account
                </h3>
    
                <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
    
                <p style="font-size: 18px; color: #4c4c4e; text-align: left;font-weight: bold; padding-top: 10px">
                    Hello , 
                </p>
    
                <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                    To activate your IN-D Credit account simply click the button below. 
                    Once clicked your request will be processed and verified and you 
                    will be redirected to the IN-D Credit Web application.
                </p>
    
                <div class="wrapper" style="margin-top: 20px; margin-bottom: 20px; text-align: center">
                    <a href=" """ + activate_url + """ "><button style="background-color: #0085d8; border: 1px solid #0085d8; color: white; font-size: 14px; height: 35px; width: 200px; cursor: pointer;">
                        ACTIVATE ACCOUNT
                    </button></a> 
                </div>
    
                <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                    You are receiving this email because you created an IN-D Credit account. 
                    If you believe you have received this email in error, please mail us 
                    to <a href="#">explore@in-d.ai</a> 
                </p>
    
                <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
                
    
            </div>
        </body>
        </html>
        """
        
        mail_body=MIMEText(htmltext,"html")
        
        message.attach(mail_body)
        
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(INTAIN_EMAIL, INTAIN_PASSWD)
            server.sendmail(sender_email,receiver_email,message.as_string())
           
        
    else:
        mongo_db_client.close()  
        return -2

    mongo_db_client.close()
    return 1

########################################################################################################################

def customer_activate(request_data):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    print(request_data)
    #secretkey=request_data['companyname'][0:8].replace(' ','')
    collection = db['user_detail']
    print(request_data['secretkey'])
    resp = collection.find_one({'secretkey':request_data['secretkey']})
    
    if not resp:
        print('Invalid Customer')
        mongo_db_client.close()
        return -2
    else:
        if resp['status'] != 'Active':

            resp = collection.find_one({'secretkey':request_data['secretkey'],'emailid':request_data['emailid'],})
            if not resp:
                mongo_db_client.close()
                return -1
            else:
                if resp['status'] != "Active":
                    print('Activating')
                    format_date = "%Y-%m-%d %H:%M"
                    now_utc = datetime.now(timezone('UTC'))
                    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))

                    resp = collection.update_one({'secretkey':request_data['secretkey']},{"$set":{'status': 'Active','reg_date_time':now_asia.strftime(format_date)}})
                    port = 465  # For SSL
                    sender_email = INTAIN_EMAIL
                    receiver_email = request_data['emailid']
                    
                    login_url = BASE_URL
                    
                    message = MIMEMultipart("alternative")
                    message["Subject"] = "IN-D Credit: Welcome!!!!"
                    message["From"] = sender_email
                    message["To"] = receiver_email
                    htmltext = """
                    <html>
                    <head></head>
                    <body>
                        <div class="container justify-content-center" style="margin: 50px 100px">
                
                            <h3 style="font-size: 26px; color: #2b2b2b; text-align: center ">
                                IN-D Credit account activation confirmation
                            </h3>
                
                            <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
                
                            <p style="font-size: 18px; color: #4c4c4e; text-align: left;font-weight: bold; padding-top: 10px">
                                Hello , 
                            </p>
                
                            <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                                Your account has been actvated. You can now access the application with your credentials using the following link
                            </p>
                
                            <div class="wrapper" style="margin-top: 20px; margin-bottom: 20px; text-align: center">
                                <a href=" """ + login_url + """ "><button style="background-color: #0085d8; border: 1px solid #0085d8; color: white; font-size: 14px; height: 35px; width: 200px; cursor: pointer;">
                                    Click To Login
                                </button></a> 
                            </div>
                            
                             <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                                Please make a note of the customer key """ + request_data['secretkey'] + """ for API access 
                            </p>
                
                            <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                                You are receiving this email because you activated an IN-D Credit account. 
                                If you believe you have received this email in error, please mail us 
                                to <a href="#">explore@in-d.ai</a> 
                            </p>
                
                            <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
                            
                
                        </div>
                    </body>
                    </html>
                    """
            
                    mail_body=MIMEText(htmltext,"html")
                    
                    message.attach(mail_body)
                    
                    # Create a secure SSL context
                    context = ssl.create_default_context()
                    
                                        
                    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                        server.login(INTAIN_EMAIL, INTAIN_PASSWD)
                        server.sendmail(sender_email,receiver_email,message.as_string())
                else:
                    mongo_db_client.close()
                    return -2
        else:
            print('already active')
            mongo_db_client.close()
            return -3
    mongo_db_client.close()
    return 1
  
########################################################################################################################

def admin_activate(request_data):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    print(request_data)
    #secretkey=request_data['companyname'][0:8].replace(' ','')
    collection = db['user_detail']
    print(request_data['secretkey'])
    resp = collection.find_one({'secretkey':request_data['secretkey']})
    
    if not resp:
        print('Invalid Customer')
        mongo_db_client.close()
        return -2
    else:
        if resp['status'] != 'Active':

            resp = collection.find_one({'secretkey':request_data['secretkey'],'emailid':request_data['emailid'],})
            if not resp:
                mongo_db_client.close()
                return -1
            else:
                if resp['status'] != "Active":
                    print('Activating')
                    format_date = "%Y-%m-%d %H:%M"
                    now_utc = datetime.now(timezone('UTC'))
                    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
                    resp = collection.update_one({'secretkey':request_data['secretkey']},{"$set":{'status': 'Active','reg_date_time':now_asia.strftime(format_date)}})
                    port = 465  # For SSL
        
                
                    sender_email = INTAIN_EMAIL
                    receiver_email = request_data['emailid']
                    
                    login_url = BASE_URL +"/admin/index.html" 
                    print(":::::::::::",login_url)
                    message = MIMEMultipart("alternative")
                    message["Subject"] = "IN-D Credit: Welcome Admin!!!!"
                    message["From"] = sender_email
                    message["To"] = receiver_email
                    htmltext = """
                    <html>
                    <head></head>
                    <body>
                        <div class="container justify-content-center" style="margin: 50px 100px">
                
                            <h3 style="font-size: 26px; color: #2b2b2b; text-align: center ">
                                IN-D Credit account activation confirmation
                            </h3>
                
                            <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
                
                            <p style="font-size: 18px; color: #4c4c4e; text-align: left;font-weight: bold; padding-top: 10px">
                                Hello , 
                            </p>
                
                            <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                                Your account has been actvated. You can now access the application with your credentials using the following link
                            </p>
                
                            <div class="wrapper" style="margin-top: 20px; margin-bottom: 20px; text-align: center">
                                <a href=" """ + login_url + """ "><button style="background-color: #0085d8; border: 1px solid #0085d8; color: white; font-size: 14px; height: 35px; width: 200px; cursor: pointer;">
                                    Click To Login
                                </button></a> 
                            </div>
                            
                             <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                                Please make a note of the customer key """ + request_data['secretkey'] + """ for API access 
                            </p>
                
                            <p style="font-size: 16px; color:#777783; text-align: left; line-height: 23px">
                                You are receiving this email because you activated an IN-D Credit account. 
                                If you believe you have received this email in error, please mail us 
                                to <a href="#">explore@in-d.ai</a> 
                            </p>
                
                            <hr style="border-top: 1px solid #b7b9bb; width: 100%; margin-top: 30px">
                            
                
                        </div>
                    </body>
                    </html>
                    """
            
                    mail_body=MIMEText(htmltext,"html")
                    
                    message.attach(mail_body)
                    
                    # Create a secure SSL context
                    context = ssl.create_default_context()
                    
                                        
                    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                        server.login(INTAIN_EMAIL, INTAIN_PASSWD)
                        server.sendmail(sender_email,receiver_email,message.as_string())
                else:
                    mongo_db_client.close()
                    return -2
        else:
            print('already active')
            mongo_db_client.close()
            return -3
    mongo_db_client.close()
    return 1
  
########################################################################################################################

def login_user(request_data):
    login_attributes = ['emailid', 'password'] 

    for attribute in login_attributes:
        if attribute not in request_data:
            return -1,""

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']

    resp = collection.find_one({'emailid': request_data['emailid'], 'password': request_data['password'],
                                'registration_type':'user_registration'})

    if resp:
        if resp['status'] == "Inactive":
            mongo_db_client.close()
            return -3,""
        else:  
            secret_key = resp['secretkey']
            first_name = resp['firstname']
    
    else:
        mongo_db_client.close()   
        return -2,""

    mongo_db_client.close()
    return first_name, secret_key

########################################################################################################################

def login_admin(request_data):
    login_attributes = ['emailid', 'password'] 

    for attribute in login_attributes:
        if attribute not in request_data:
            return -1,""

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']


    resp = collection.find_one({'emailid': request_data['emailid'], 'password': request_data['password'],
                                'registration_type':'admin_registration'})

    if resp:
        if resp['status'] == "Inactive":
            mongo_db_client.close()
            return -3,""
        else:  
            secret_key = resp['secretkey']
            first_name = resp['firstname']
    
    else:
        mongo_db_client.close()   
        return -2,""

    mongo_db_client.close()
    return first_name, secret_key
########################################################################################################################
def update_token(request_email, request_token,registration_type):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['token_detail']

    resp = collection.find_one(({'emailid': request_email}))

    if resp:
        collection.update_one({'emailid': request_email}, {"$set":{'token': request_token,'registration_type':registration_type}})
    else:
        collection.insert_one(({'emailid': request_email, 'token': request_token,'registration_type':registration_type}))

    mongo_db_client.close()
    return 1

########################################################################################################################
def forget_password(request_data):
    if 'emailid' not in request_data:
        return -1

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']

    resp = collection.find_one({'emailid': request_data['emailid']})

    if resp:
        secret_key = resp['secretkey']
    else:
        mongo_db_client.close()   
        return -2

    mongo_db_client.close()
    return secret_key

########################################################################################################################
def get_token_process_docs(request_data):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['token_detail']

    resp = collection.find_one(({'token': request_data['token'],'registration_type':'user_registration'}))
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>",resp)
    if resp:
        email_id = resp['emailid']
        mongo_db_client_new = MongoClient(MONGODB_URL, MONGODB_PORT)
        db_new = mongo_db_client[MONGODB_NAME]
        collection_new = db_new['user_detail']

        resp_new = collection_new.find_one(({'emailid': email_id}))
        secret_key = resp_new['secretkey']
    else:
        mongo_db_client.close()   
        return -2

    mongo_db_client.close()
    mongo_db_client_new.close()
    return {'emailid': email_id, 'secretkey': secret_key}

########################################################################################################################
def get_token(request_data,registration_type):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['token_detail']

    resp = collection.find_one(({'token': request_data['token'],'registration_type':registration_type}))

    if resp:
        email_id = resp['emailid']
        mongo_db_client_new = MongoClient(MONGODB_URL, MONGODB_PORT)
        db_new = mongo_db_client[MONGODB_NAME]
        collection_new = db_new['user_detail']

        resp_new = collection_new.find_one(({'emailid': email_id}))
        secret_key = resp_new['secretkey']
    else:
        mongo_db_client.close()   
        return -2

    mongo_db_client.close()
    mongo_db_client_new.close()
    return {'emailid': email_id, 'secretkey': secret_key}

#######################################################################################################################

def get_single_records(emailid,job_id,new_file_name,output_dataframe,excel_path,transaction_data,calculation_response,calculation_result_list,bank_type):

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['analysis_detail']
    collection_job_status = db['job_detail']

    collection.insert_one(({'emailid':emailid,'job_id': job_id, 'file_name': new_file_name,
                            'excel_path': excel_path,'calculation_response': str(calculation_response) ,
                            'calculation_result_list':calculation_result_list}))

    collection_job_status.update_one({'job_id': job_id}, {"$set":{'job_status': "Incomplete",'excel_path':excel_path,'bank_type':bank_type,'review_status':'Yes'}})
    
    mongo_db_client.close()
    return 

########################################################################################################################
def reset_password(request_email, request_pwd):

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']
    collection.update_one({'emailid': request_email}, {"$set": {'password': request_pwd}})

    mongo_db_client.close()
########################################################################################################################
def logout_user(request_email):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['token_detail']

    collection.delete_one({'emailid': request_email})
    mongo_db_client.close()

########################################################################################################################

def delete_by_job_id(request_email,job_id):

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']
    collection_analysis = db['analysis_detail']

    response = collection.find_one({'emailid': request_email,'job_id': job_id})
    file_path = response['file_path']
    folder_path = file_path.split('/')[-1]
    folder_path = file_path.replace(folder_path,'')
    if os.path.exists:
        shutil.rmtree(folder_path)
    collection.delete_one({'emailid': request_email,'job_id': job_id})
    collection_analysis.delete_one({'emailid': request_email,'job_id': job_id})

    mongo_db_client.close()
    return 

########################################################################################################################

def get_company_name(request_email):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']
    company_name = collection.find_one({'emailid':request_email})
    company_name = company_name['companyname'] 
    mongo_db_client.close()
    return company_name

########################################################################################################################

def long_words(lst,dashboard):
    words = []
    for word in lst:
        if dashboard == 'user':
            word = {key: word[key] for key in word.keys() 
                    & {'bank_name','upload_date_time','job_id','job_status','applicant_id','excel_path','comment'}} 
            words.append(word)
        elif dashboard == 'admin':
            word = {key: word[key] for key in word.keys() 
                    & {'bank_name','upload_date_time','job_id','job_status','emailid','applicant_id','excel_path','document_name','review_status','comment'}} 
            words.append(word)
    return words
    
def user_dashboard_detail(request_email,data):

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']
    response = collection.find({'emailid': request_email}, { '_id': 0})
    if response:
        api_response = long_words(response,'user')
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################

def admin_dashboard_detail(request_email):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find({'job_status': 'Incomplete'}, { '_id': 0})
    if response:
        api_response = long_words(response,'admin')
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################

def get_reviewed_admin_dashboard(request_email):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find({'job_status': 'Completed'}, { '_id': 0})
    if response:
        api_response = long_words(response,'admin')
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################

def get_application_id_detail(applicant_id,emailid):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']
  
    response = collection.find_one(({'applicant_id':applicant_id,'emailid':emailid}))
    if response:
        mongo_db_client.close()
        return response
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################

def get_Details_By_ID(request_email, request_jobid):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['analysis_detail']

    response = collection.find_one({'emailid': request_email, 'job_id': request_jobid}, {'emailid': 0, '_id': 0, 'job_id': 0})
    if response:
        mongo_db_client.close()
        return response
    else:
        mongo_db_client.close()
        return -2
########################################################################################################################

def get_excel_data(lst):
    words = []
    indexes = []
    for word in lst:
        word_list = {key: word[key] for key in word.keys() 
                & {'upload_date_time','job_id','job_status','applicant_id','calculation_response'}} 
        word = word_list['calculation_response']
        index = word_list['applicant_id']
        indexes.append(index)
        words.append(word)
    return words,indexes

def get_excel_data_by_date(request_email, day_start_date,day_end_date):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail'] 
    date_time_obj = datetime.strptime(day_end_date,'%Y-%m-%d')
    day_end_date = str(date_time_obj.date() + timedelta(days=1))
    myquery = { "emailid":request_email,'job_status':'Completed', "upload_date_time":{"$gt": day_start_date,"$lte": day_end_date }}
    response = collection.find(myquery)
    if response:
        api_response,indexes = get_excel_data(response)
        df = pd.DataFrame(api_response, index = indexes)
        df = df.sort_index()
        daily_data_csv_path = os.getcwd() + f'/webserverflask/static/data/input/daily_report_{day_start_date}.csv'
        df.to_csv(daily_data_csv_path)
        excel_path = daily_data_csv_path.split('/hdfc_credit/webserverflask')[-1]
        mongo_db_client.close()
        return excel_path
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################

def save_upload_file(emailid, job_id,file_name):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find_one({'emailid': emailid, 'job_id': job_id})
    
    if response:
        x = response['file_names']
        x.append(file_name)
        collection.update_one({'emailid': emailid,'job_id': job_id}, {"$set": {'file_names': x}})
        mongo_db_client.close()
        return x
    else:
        x = []
        x.append(file_name)
        collection.insert_one(({'emailid':emailid,'job_id': job_id, 'file_names': x}))
        mongo_db_client.close()
        return x

########################################################################################################################

def get_upload_file(emailid, job_id):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find_one({'emailid': emailid, 'job_id': job_id})
    
    if response:
        x = response['file_names']
        collection.delete_one({'emailid': emailid,'job_id': job_id})
        mongo_db_client.close()
        return x
        
    else:
        collection.delete_one({'emailid': emailid,'job_id': job_id})
        mongo_db_client.close()
        return -2

########################################################################################################################

def get_localization_password_status(request_data):

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find_one({'job_id': request_data['job_id']})

    if response:
        # file_path = response['file_path'] 
        # password = response['password']
        # bank_name = response['bank_name']
        localization_status = response['localization_status']
        readable_status = response['readable_status']

        collection.update_one({'job_id': request_data['job_id']}, {"$set": {'doc_type': 'Bank Statement'}})
        mongo_db_client.close()
        return [localization_status,readable_status]
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################
def get_localization_details(request_data):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']
    response = collection.find_one({'job_id': request_data['job_id'],'job_status': 'Incomplete'})

    if response:
        file_path = response['file_path']
        # doc_type = response['doc_type']
        doc_type = 'Bank Statement'
        bank_name = response['bank_name']
        readable_status = response['readable_status']
        print("-------- Input File Name = {} -------".format(file_path))

        try:        
            table_coordinate_list,width, height,reduced_percentage,columns_list = get_bank_statement(file_path,doc_type,bank_name,readable_status)
            NewList1=[]
            for ind_, temp in enumerate(table_coordinate_list):
                keys_needed = ['left', 'top', 'width', 'height']
                table__ = {k:temp[k] for k in keys_needed}
                major_table = {k:temp[k] for k in temp if k not in keys_needed}
                if ind_ == 0:
                    table__['colItem'] = columns_list
                major_table['table_data'] = [table__]
                NewList1.append(major_table)

            table_coordinate_list = NewList1
            collection.update_one({'job_id': request_data['job_id']}, {"$set": {'table_coordinate_list': table_coordinate_list,'width':width,
                                'height':height,'reduced_percentage':reduced_percentage,'columns_list':columns_list}})
            mongo_db_client.close()
            return [table_coordinate_list,width,height]
        except:
            print(traceback.print_exc())
            return -2
    else:
        mongo_db_client.close()
        return -2    

#############################################################################################################################

def get_digitization_details(request_jobid,table_coords):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find_one({'job_id': request_jobid})
    if response:
        # data_input = response['table_coordinate_list']

        data_input = table_coords
        file_path = response['file_path']
        readable_status = response['readable_status']
        bank_name = response['bank_name']
        reduced_percentage = response['reduced_percentage']
        data = get_valid_format(bank_name,data_input)
        try:
            final_output = extraction_data(data,readable_status,reduced_percentage,file_path)
            collection.update_one({'job_id': request_jobid}, {"$set": {'table_data': final_output}})
            mongo_db_client.close()
            return final_output
        except:
            print(traceback.print_exc())
            return -2
    else:
        mongo_db_client.close()
        return -2  

#########################################################################################################################
def save_digitized_data(request_jobid):

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['job_detail']

    response = collection.find_one({'job_id': request_jobid})

    if response:
        file_path = response['file_path']
        bank_name = response['bank_name']
        table_data = response['table_data']
        
        try:
            output_dataframe,bank_type,excel_path,transaction_data = combined_dataframe(bank_name,table_data,file_path)
            final_combined = output_dataframe.to_json(orient='records')
            collection.update_one({'job_id': request_jobid}, {"$set": {'final_combined': final_combined,'bank_type':bank_type,'excel_path':excel_path,'transaction_data':transaction_data}})
            mongo_db_client.close()
            return final_combined
        except:
            print(traceback.print_exc())
            return -2
    else:
        mongo_db_client.close()
        return -2  

#########################################################################################################################

def get_calculation_data(request_jobid):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection_job_status = db['analysis_detail']
    collection = db['job_detail']

    comment = ''
    response = collection.find_one({'job_id': request_jobid})
    response_analysis = collection_job_status.find_one({'job_id': request_jobid})
    if response_analysis:
        if 'calculation_result_list' in response_analysis.keys() and 'calculation_response' in response_analysis.keys():
            calculation_response = response_analysis['calculation_response']
            return [calculation_response,response_analysis['excel_path'],response_analysis['calculation_result_list'],response_analysis['file_name'],comment]

    if response:
        file_path = response['file_path']
        bank_name = response['bank_name']
        bank_type = response['bank_type']
        text = response['text']
        word_order = response['word_order']
        excel_path = response['excel_path']
        emailid = response['emailid']
        # transaction_data = response['transaction_data']
        
        try:
            calculation_response,calculation_result_list = get_statement_analysis(excel_path,bank_name,bank_type,file_path,text,word_order)
            response = collection_job_status.find_one({'job_id': request_jobid})
            excel_path = excel_path.split('/hdfc_credit/webserverflask')[-1]
            file_path = file_path.split('/hdfc_credit/webserverflask')[-1]

            if not response:
                collection_job_status.insert_one(({'emailid':emailid,'job_id':request_jobid ,'excel_path': excel_path,'file_name':file_path,
                                        'calculation_result_list':calculation_result_list,'comment':'',
                                        'calculation_response':str(calculation_response)}))
            else:
                collection_job_status.update_one({'job_id': request_jobid}, {"$set":{'emailid':emailid,'job_id':request_jobid ,'excel_path': excel_path,'file_name':file_path,
                                        'calculation_result_list':calculation_result_list,'comment':'',
                                        'calculation_response':str(calculation_response)}})
            
            collection.update_one({'job_id': request_jobid}, {"$set":{'job_status': "Completed",'calculation_csv':excel_path,'review_status':'Yes','comment':comment}})
            mongo_db_client.close()
            
            return [calculation_response,excel_path,calculation_result_list,file_path,comment]
        except:
            excel_path = excel_path.split('/hdfc_credit/webserverflask')[-1]
            file_path = file_path.split('/hdfc_credit/webserverflask')[-1]
            comment = ''
            collection_job_status.insert_one(({'emailid':emailid,'job_id':request_jobid ,'excel_path': excel_path,'file_name':file_path,'review_status':'Yes','comment':comment}))
            print(traceback.print_exc())
            mongo_db_client.close()
            return ['',excel_path,[],file_path,comment]
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################

def get_calculation_data_new(emailid,job_id):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['analysis_detail']

    response = collection.find_one({'job_id': job_id})
    if response:
        print('calculation_response>',response['calculation_response'])
        return response
   
    mongo_db_client.close()
    return 
########################################################################################################################

def get_final_dict(input_dict):
    final_result_list = []
    final_result_id = {}
    count = 1
    for key,val in input_dict.items():
        new_key = re.sub('[^A-Za-z]+', ' ', key)
        new_key = new_key.strip()
        final_result_id = {}
        final_result_id['id'] = count
        final_result_id['name'] = new_key
        final_result_id['value'] = val
        count += 1
        final_result_list.append(final_result_id)
    return final_result_list

def get_col_widths(dataframe):
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(str(col))]) for col in dataframe.columns]

def bs_admin_update_job(emailid,data):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['analysis_detail']
    job_collection = db['job_detail']
    response = collection.find_one({'job_id': data['job_id']})
    try:
        excel_path = response['excel_path']
    except:
        excel_path = 'static/data/input/'
    new_data = {}
    new_data['Account Holder'] = data['Account Holder']
    new_data['Account Opening Date'] = data['Account Opening Date']
    new_data['Type of Account'] = data['Type of Account']
    new_data['Monthly Average Balance'] = data['Monthly Average Balance']
    new_data['Total Salary'] = data['Total Salary']
    comment = data['comment']
    final_result_list = get_final_dict(new_data)
    
    key,val,values = [],[],[]
    for name,cal in new_data.items():
        name = re.sub('[^A-Za-z]+', ' ', name)
        key.append(name.strip())
        val.append(cal)
    values.append(key); values.append(val)
    df2 = pd.DataFrame(values,index=['Parameter', 'Result']).transpose()
    excel_path_cwd = os.getcwd() + '/webserverflask'+ excel_path
    # with pd.ExcelWriter(excel_path_cwd, engine="openpyxl", mode="a") as writer:
    #     workbook=openpyxl.load_workbook(excel_path_cwd)
    #     try:
    #         std=workbook.get_sheet_by_name('calculations and ratios')
    #         workbook.remove_sheet(std)
    #     except:
    #         pass
    #     df2.to_excel(writer,sheet_name = 'calculations and ratios',index=False)
    
    try:
        writer = pd.ExcelWriter(excel_path_cwd,engine='xlsxwriter')
        df2.to_excel(writer, sheet_name='Bank Statement Result', header = True,index=False)
        worksheet = writer.sheets['Bank Statement Result']
        for i, width in enumerate(get_col_widths(df2)):
            worksheet.set_column(i, i,width+5)
        writer.save()
    except:
        print(traceback.print_exc())
        pass

    collection.update_one({'job_id': data['job_id']}, {"$set": {'calculation_result_list':final_result_list,'calculation_response':new_data,'excel_path':excel_path,'comment':comment}})
    job_collection.update_one({'job_id': data['job_id']}, {"$set": {'job_status': "Completed",'comment':comment,'review_status':'Yes','excel_path':excel_path,'calculation_response':new_data}})
    mongo_db_client.close()
    return 'Successful'

########################################################################################################################

def profile_update(request_email):
    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']

    response = collection.find({'emailid': request_email}, {'_id': 0, 'secretkey': 0})

    if response:
        api_response = [row for row in response]
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2

########################################################################################################################
def update_secret(request_email):
    user_attributes = ['firstname','lastname','password','emailid','phone','companyname']

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']

    resp = collection.find_one({'emailid':request_email})

    if resp:
        secret_key = ""
        for attribute in user_attributes[:6]:
            secret_key = secret_key + resp[attribute]

        collection.update_one({'emailid': request_email}, {"$set": {'secretkey':secret_key}})

    mongo_db_client.close()
    return 1
########################################################################################################################
def user_update(request_email, request_data):
    user_attributes = ['firstname','lastname','password','phone','companyname']

    mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
    db = mongo_db_client[MONGODB_NAME]
    collection = db['user_detail']
    resp = collection.find_one({'emailid': request_email})

    if resp:
        update_data = {}
        for attribute in user_attributes:
            if attribute in request_data:
                attrb_GT = resp[attribute]
                attrb_value = request_data[attribute]
                if not attrb_value == attrb_GT:
                    update_data[attribute] = attrb_value

        if len(update_data):
            collection.update_one({'emailid': request_email}, {"$set": update_data})
            update_secret(request_email)
    else:
        mongo_db_client.close()
        return -2

    mongo_db_client.close()
    return 1
 

########################################################################################################################
def get_jobid(request_email):
    try:
        mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
        db = mongo_db_client[MONGODB_NAME]
        collection = db['job_detail']

        response = collection.count()

        mongo_db_client.close()
        return response
    except:
        print(traceback.print_exc())
        return -2
########################################################################################################################
def insert_job(request_data):
    try:
        mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
        db = mongo_db_client[MONGODB_NAME]
        collection = db['job_detail']

        collection.insert_one(request_data)

        mongo_db_client.close()
        return 0
    except:
        print(traceback.print_exc())
        return -2

########################################################################################################################
def update_jobstatus(request_email, request_jobid, request_status):
    try:
        mongo_db_client = MongoClient(MONGODB_URL, MONGODB_PORT)
        db = mongo_db_client[MONGODB_NAME]
        collection = db['job_detail']

        collection.update_one({'emailid': request_email, "job_id": request_jobid}, {"$set": {'job_status': request_status}})

        mongo_db_client.close()
        return 0
    except:
        print(traceback.print_exc())
        return -2
########################################################################################################################
if __name__ == "__main__":
    print("")
    pass
