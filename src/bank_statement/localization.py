from .tabula_pdf import get_direct_table_data
from .bank_statement import get_readable_status
from .function_library import number_of_pages
import pandas as pd
import traceback
import config.config as project_configs
localization_bank = project_configs.INTAIN_BANK_STATEMENT_LOCALIZATION_BANK_CSV

def get_localization_status(bank_name,pdf_file_name):
    if pdf_file_name.endswith('.pdf') or pdf_file_name.endswith('.PDF'):
        readable_status = get_readable_status(pdf_file_name)
        page_count = number_of_pages(pdf_file_name)
        if readable_status == 'non-readable':
            return False,readable_status,[]
        localization_banks = pd.read_csv(localization_bank,header=None)
        for index, row in localization_banks.iterrows():
            if bank_name == row[0]:
                try:
                    final_output_json = get_final_dataframe(bank_name,pdf_file_name,page_count)
                    return True,readable_status,final_output_json
                except:
                    print(traceback.print_exc())
                    return True,readable_status,[]
        return False,readable_status,[]
    else:
        readable_status = 'non-readable'
        return False,readable_status,[]

def get_final_dataframe(bank_name,pdf_file_name,page_count):
    result ={}
    final_output_json =[]
    df = get_direct_table_data(pdf_file_name,page_count,bank_name)
    excel_data = df.to_json(orient='index')
    result["excel_data"] = excel_data
    final_output_json.append(result)
    return final_output_json
