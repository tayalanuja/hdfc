import os

from PyPDF2 import PdfFileReader, PdfFileWriter
from pdf2image import convert_from_path

def decrypt_pdf(input_path, output_path, password):
  with open(input_path, 'rb') as input_file, \
    open(output_path, 'wb') as output_file:
    reader = PdfFileReader(input_file)
    reader.decrypt(password)
    writer = PdfFileWriter()
    for i in range(reader.getNumPages()):
      writer.addPage(reader.getPage(i))
    writer.write(output_file)

def number_of_pages(file_path):
  try:
    pdf = PdfFileReader(open(file_path,'rb'))
    page_count = pdf.getNumPages()
    return page_count
  except:
    pages = convert_from_path(file_path,200)
    return len(pages)

def get_valid_format(bank_name,data):
    temp = []
    total_result = []
    for key in data.keys():
        temp.append(data[key])
    number_of_pages = len(temp)
    for index,item in enumerate(temp):
        bankname = bank_name
        documentType = item["documentType"]
        corrected_imageName = item["corrected_imageName"] 

        table_data = []
        initial_result = []
        final_output = {}
        new_dict = {}
        final_result = {}

        if 1 < index < number_of_pages-1:
            xxxx = temp[1]
            xxxx.update({'corrected_imageName': corrected_imageName})
            item = xxxx
            value_at_index = list(list(item.items())[3])

            new_dict= value_at_index[1]
            for x in new_dict:
                initial_result.append(new_dict[x])

            final_output["left"] = new_dict["left"]
            final_output["top"] = new_dict["top"]
            final_output["width"] = new_dict["width"]
            final_output["height"] = new_dict['height']
            column_list = []
            length_initial_result = len(initial_result)
            if len(initial_result) > 4:
                for i in range(4,length_initial_result):

                    column_list.append(initial_result[i])

                final_output["colItem"] = column_list
            # print("index -----++ {} ++---------".format(index),final_output)

            table_data.append(final_output)

            final_result["bank_name"] = bankname
            final_result["documentType"] = documentType
            final_result["corrected_imageName"] = corrected_imageName
            final_result["table_data"] = table_data

        else:

            value_at_index = list(list(item.items())[3])
            new_dict = value_at_index[1]
            for x in new_dict:
                initial_result.append(new_dict[x])
            final_output["left"] = new_dict["left"]
            final_output["top"] = new_dict["top"]
            final_output["width"] = new_dict["width"]
            final_output["height"] = new_dict['height']
            
            column_list = []
            length_initial_result = len(initial_result)
            if len(initial_result) > 4:
                for i in range(4,length_initial_result):
                    column_list.append(initial_result[i])
                final_output["colItem"] = column_list

            # print("index ------- {} -----------".format(index),final_output)

            table_data.append(final_output)

            final_result["bank_name"] = bankname
            final_result["documentType"] = documentType
            final_result["corrected_imageName"] = corrected_imageName
            final_result["table_data"] = table_data

        total_result.append(final_result)

    # print(total_result)
    return total_result