import config.config as config
# import config.config as project_configs
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient
import traceback
import xlwt
import os
import datetime
import json
import pandas as pd
import pprint
from pytz import timezone
import re 

# import admin_dbV8

mongo_db_client = None
fixed_secret_key = 'IntainAI@123'
uri = "mongodb://{}:{}/{}".format(config.DATABASE_CONFIG['db_vm'],config.DATABASE_CONFIG['db_port'],config.DATABASE_CONFIG['db_name'])
mongo_db_client = MongoClient(uri)
db = mongo_db_client[config.DATABASE_CONFIG['db_name']]

###############################################################################################

def userDashboardDetail(request_email):
    #pprint.pprint(request_data)
    job_collection = db['payslip_job']
    job_response = job_collection.find(
        {
            'emailid': request_email
        }, {
            'emailid': 0,
            '_id': 0,
        })
    if job_response:
        api_response = []
        for row in job_response:
            if row['job_status'] == 'NULL':
                row['job_status'] = 'In Process'
            elif row['admin_submitted']:
                row['job_status'] = 'Validated by Admin'
            elif row['batch_submitted_status']:
                row['job_status'] = 'Submitted to Admin'

            api_response.append(row)
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2


###############################################################################################


def delete_null_job(request_email):
    collection = db['payslip_job']
    collection.delete_many(
        {
            'emailid': request_email, 
            'job_status': 'NULL'
        })
    mongo_db_client.close()

###############################################################################################

def get_jobid(request_email):
    try:
        collection = db['payslip_job']
        response = collection.count()
        mongo_db_client.close()
        return response
    except Exception as e:
        print(traceback.print_exc())
        return -2

###############################################################################################
def get_batch_name(job_id):
    try:
        print(job_id)
        collection = db['payslip_job']
        response = collection.find_one({
            "document_name": job_id
        }, {
            '_id': 0,
            'emailid': 0,
            'job_id': 0
        })
        print(response)
        if response:
            print("batchhhh name")
            print(response['batch_name'])
            return response['batch_name']
        mongo_db_client.close()
    except Exception as e:
        print(traceback.print_exc())
        return -2
################################################################################################


def insert_job(request_data):
    try:
        collection = db['payslip_job']

        collection.insert_one(request_data)

        mongo_db_client.close()
        return 0
    except Exception as e:
        print(traceback.print_exc())
        return -2

###############################################################################################

def digitise_document(request_email, request_data):
    try:
        list_folders = []
        job_collection = db['payslip_job']
        result_collection = db['payslip_result']
        
        print(request_data)
        response = result_collection.find_one({
            'emailid': request_email,
            "job_id": request_data['job_id']
        }, {
            '_id': 0,
            'emailid': 0,
            'job_id': 0
        })
        print("job_digitised response",response)
        if response:
            print("Job already digitised")
            return -2
        rows = request_data

        if rows["batch_name"] == "":
            batch_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            batch_name = rows["batch_name"]

        job_collection.update_one(
            {
                'emailid': request_email,
                "document_name": rows["document_name"],
                "job_id": rows["job_id"]
            }, {
                "$set": {
                    'batch_name': batch_name,
                    'batch_submitted_status': False
                }
            })
        if rows['job_priority'] == "High":
            list_folders.append(rows["job_id"])

        if rows['job_priority'] == "Medium":
            list_folders.append(rows["job_id"])

        if rows['job_priority'] == "Auto":
            list_folders.append(rows["job_id"])

        if rows['job_priority'] == "Low":
            list_folders.append(rows["job_id"])

        mongo_db_client.close()
        new_list_folders = []
        for folders in list_folders:
            if folders not in new_list_folders:
                new_list_folders.append(folders)

        return new_list_folders         
    except Exception as e:
        print(traceback.print_exc())
        return -2

###############################################################################################

def download_result(request_email, request_jobid):

    collection = db['payslip_job']

    response = collection.find_one(
        {
            'emailid': request_email,
            'job_id': request_jobid
        }, {
            'emailid': 0,
            '_id': 0,
        })

    if response:
        # pprint.pprint(response)
        mongo_db_client.close()
        return response['excel_path']
    else:
        mongo_db_client.close()
        return -2


def batch_submit(request_email, job_id):

    collection = db['payslip_job']

    job_id = job_id.replace("Job_", "")

    response = collection.find_one({
        'emailid': request_email,
        "job_id": job_id,
        'batch_submitted_status': False
    }, {
        '_id': 0,
        'emailid': 0,
        'job_id': 0
    })

    if response:
        collection.update_one({
            'emailid': request_email,
            "job_id": job_id
        }, {"$set": {
            'batch_submitted_status': True
        }})

        inv_collection = db['payslip_result']

        response = inv_collection.find(
            {
                'emailid': request_email,
                'job_id': job_id
            }, {
                'emailid': 0,
                'job_id': 0
            })
        

        if response:
            api_response = [row for row in response]
            mongo_db_client.close()
            return api_response

    else:
        mongo_db_client.close()
        return -2

    return 1

###############################################################################################

def update_jobstatus(request_email, request_jobid, request_status):
    try:
        collection = db['payslip_job']

        collection.update_one(
            {
                'emailid': request_email,
                "job_id": request_jobid
            }, {"$set": {
                'job_status': request_status
            }})

        mongo_db_client.close()
        return 0
    except Exception as e:
        print(traceback.print_exc())
        return -2

###############################################################################################

def payslip_result(request_data,excel_path):
    try:
        collection = db['payslip_result']
        response = collection.find_one({
        'emailid': request_data['emailid'],
        "job_id": request_data['job_id'],
        'batch_submitted_status': False
    }, {
        '_id': 0,
        'emailid': 0,
        'job_id': 0
    })

        if response:
                print("Job already digitised")
                return -2
        else:
            collection.insert(request_data, check_keys=False)
            job_collection=db['payslip_job']
            job_collection.update_one(
            {
                'emailid': request_data['emailid'],
                "job_id": request_data['job_id']
            }, {"$set": {
                'excel_path': excel_path
            }})

            mongo_db_client.close()
            return 0
    except Exception as e:
        print(traceback.print_exc())
        return -2

###############################################################################################

def adminDashboardDetail(admin_email,flag):
    collection = db['payslip_job']
    
    response = collection.find(
            {
                'admin_submitted':flag
            },{
                '_id':0,
                'job_status':0,
                'job_priority':0,
                'job_size':0,
                'document_name':0,
                'batch_submitted_status':0
            })
    if response:
        api_response = []
        for row in response:
            api_response.append(row)
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2
###############################################################################################

def returnApplication(emailid,jobid):
    collection = db['payslip_result']
    response = collection.find(
        {
            'emailid':emailid,
            'job_id':jobid
        }
    )
    if response:
        api_response = [row for row in response]
        return api_response
    return -1
###############################################################################################

def get_excel_data_by_date(user_email, day_start_date,day_end_date):
    try:
        job_collection = db['payslip_job']
        base_dir = os.getcwd()
        date_time_obj = datetime.datetime.strptime(day_end_date,'%Y-%m-%d')
        day_end_date = str(date_time_obj.date() + timedelta(days=1))   
        job_id_query = { "emailid":user_email,"upload_date_time":{ "$gt": day_start_date,"$lte": day_end_date }}
        response = job_collection.find(job_id_query)
        if response:
            write_excel_file=base_dir+'/webserverflask/static/data/excels/daily_report.xlsx'
            if os.path.isfile(write_excel_file):
                os.remove(write_excel_file)
            df=pd.DataFrame()
            for resp in response:
                excel_file=base_dir+'/webserverflask/'+resp['excel_path']
                df=df.append(pd.read_excel(excel_file))
                # sheet_name=resp['batch_name']
                # sheet_name = re.sub(r'[:?*//]', "",sheet_name)
            with pd.ExcelWriter(write_excel_file, engine="openpyxl", mode="w") as writer:
                df.to_excel(writer,sheet_name = "Results",index=False)
            writer.save()
            return 'static/data/excels/daily_report.xlsx'
        else:
            mongo_db_client.close()
            return -2
    except Exception as e:
        print(traceback.print_exc())
        return -2
###############################################################################################

def admin_review_job(user_email,job_id):

    job_collection = db['payslip_job']
    job_response = job_collection.find_one(
        {
            'emailid': user_email,
            'job_id':job_id
        }, {
            'emailid': 0,
            '_id': 0, 
        })
    if job_response:
        api_response = []
        resp = returnApplication(user_email,job_id)
        api_response.extend(resp)
        mongo_db_client.close()
        return api_response
    else:
        mongo_db_client.close()
        return -2

###############################################################################################
def update_excel(request_email, request_data):
    try:
        base_dir = os.getcwd()
        print(base_dir)
        excel_file=base_dir+'/webserverflask/static/data/excels/Job_'+request_data['job_id']+'.xlsx'
        file_name=request_data['file_name'].split("/")[-1]  
        df=pd.read_excel(excel_file)
        print(df)  
        for attribute in request_data['text_fields']:
            print(file_name,attribute['varname'],attribute['value'])
            df.loc[df.file == file_name, attribute['varname']] = attribute['value']
        print("updated",df['employer_name'])
        with pd.ExcelWriter(excel_file, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer,sheet_name = 'Payslip Result',index=False)
        writer.save()
        return 1
    except Exception as e:
        print(traceback.print_exc())


###############################################################################################


def admin_submit(user_email,job_id):

    collection = db['payslip_job']

    response = collection.find_one({
        'emailid': user_email,
        'job_id':job_id
    }, {
        '_id': 0,
        'emailid': 0
    })
    format_date = "%Y-%m-%d %H:%M"
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    if response:
        collection.update_one({
            'emailid': user_email,
            'job_id':job_id
        }, {"$set": {
            'admin_submitted': True,
            'admin_submitted_time':now_asia.strftime(format_date)

        }})

        mongo_db_client.close()
        return 1

    return -2

###############################################################################################
def admin_update(admin_email, request_data):
    try:
        collection = db['payslip_result']
        full_response = collection.find({
            'emailid': request_data['user_email'],
            "job_id": request_data['job_id'],
            "Result":{"$elemMatch":{"image":request_data['file_name']}}
        })  

        if full_response:
            for row in full_response:
                print(row)
                flag=0
                for response in row["Result"]:
                    print(response)
                    if request_data["file_name"] in response["image"]:
                        update_data = {}
                        for text_attribute in request_data['text_fields']:
                            attribute = text_attribute['varname']
                            try:
                                attrb_GT = response["Output"][attribute]
                                attrb_value = text_attribute['value']
                                print(attrb_GT,attrb_value)
                                if not attrb_value == attrb_GT:
                                    response['Output'][attribute] = attrb_value
                                    response['Output'][attribute + '_conf'] = 1
                                    response['Output'][attribute + '_user_edited'] = 1
                                    flag=1
                            except Exception as e:
                                print(traceback.print_exc())
                                return -2
                    if flag:
                        print(row["Result"])
                        collection.update(
                        {
                            'emailid': request_data['user_email'],
                            'job_id': request_data['job_id'],
                                '_id':row['_id']
                        }, {"$set": {"Result":row["Result"]}})
                        print("updates")
                        update_excel(request_data['user_email'],request_data)
                        print("excel_updated")
                        return 1
        else:
            mongo_db_client.close()
            return -2

    except Exception as e:
        print(traceback.print_exc())
        return -2

        

