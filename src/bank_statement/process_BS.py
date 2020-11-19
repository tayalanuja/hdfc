import os
from google.cloud.vision import types
from google.cloud import vision
from pdf2image import convert_from_path
import io,re
import traceback
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import config.config as project_configs
apikey = project_configs.INTAIN_BANK_STATEMENT_GOOGLE_APPLICATION_CREDENTIALS



def pdf2jpg(pdf_file):
    try:
        c=0
        if pdf_file.endswith(".pdf") or pdf_file.endswith(".PDF"):
            pages = convert_from_path(pdf_file, 200)
            pdf_file = pdf_file[:-4]    
            for page in pages:
                c=c+1
                page.save("%s-page%d.jpg" % (pdf_file,pages.index(page)), "JPEG")
        return c
    except:
        return "pdf not found"
    
    
def IFSCAttr(lines):
    IFSC = "NA"
    for l in lines:
        if "ifsc" in l.lower():
           l_list = l.split(" ")
           for l1 in l_list:
               if l1[:4].isupper()==True and l1[-3:].isdigit()==True:
                   IFSC = l1
    return IFSC
    
    
    
def DateAttr(lines):
    Range = "NA"
    # print("Hi")
    months =  ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_SC =  ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    res_list = []
    for l in lines:
        
        if ("from" in l.lower() and "to" in l.lower()) or "period" in l.lower() or "between" in l.lower():
            if Range == "NA":
                # l_list = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{2})|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{1}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{2}-[A-Za-z]{3}-[0-9]{4}|[0-9]{1}-[A-Za-z]{3}-[0-9]{4}',l)
                l_list = re.findall(r'([0-3]{0,1}[0-9]{1}[-]{1}[0-1]{1}[0-9]{1}[-]{1}[1-2]{1}[09]{1}\d{2})', l)                
                if len(l_list)!=0:
                    Range = l_list[0] + " " + "to" + " " + l_list[1]
                
        if Range == "NA":
            if "canara bank" not in lines[0].lower():
                if "to" in l.lower():
                    # print("Date6",l)
                    l_list = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{2}/[0-9]{2}/[0-9]{2}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{1}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{2}-[A-Za-z]{3}-[0-9]{4}|[0-9]{1}-[A-Za-z]{3}-[0-9]{4}',l)
                    # print(l_list)
                    if len(l_list)==2:
                        Range = l_list[0] + " " + "to" + " " + l_list[1]

        if Range == "NA":
            for m in months:
                if m in l:
                    l_list = re.findall(r'[0-9]{2},\s[0-9]{4}',l)
                    if len(l_list)==2:
                        # print("Third2")
                        Range = m + " " + l_list[0] + " " + "to" + " " + m + " " + l_list[1]
        
        if range == "NA" and "period" in l:
            # print("Date3")
            res = ''
            date_list = l.split(" ")
            index_of = date_list.index("period")
            for i in date_list[index_of+1:]:
                res = res + " " + i
            Range = res
        
    for i,l in enumerate(lines):
        if Range == "NA":
            # print("Date4")
            if "from" in l.lower() and "to" in lines[i+1].lower():
                l1_list = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{2}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{1}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{2}-[A-Za-z]{3}-[0-9]{4}|[0-9]{1}-[A-Za-z]{3}-[0-9]{4}',l)
                l2_list = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{2}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{1}\s[A-Za-z]{3}\s[0-9]{4}|[0-9]{2}-[A-Za-z]{3}-[0-9]{4}|[0-9]{1}-[A-Za-z]{3}-[0-9]{4}',lines[i+1])
                if len(l1_list)!=0 and len(l2_list)!=0:
                    Range = l1_list[0] + " " + "to" + " " + l2_list[0]
    
    return Range
                                         
def NameAttr(df,lines):
    Name = "NA"
    temp = lines
    name_list = []

    # for i,l in enumerate(lines[10]):      
    #     # Axis 
        
    #     print("lines[10]lines[10]lines[10]lines[10]\n",lines)
    #     if Name == "NA" or Name == '':
    #         if "axis" in l.lower():
    #             print("First13")
    #             for t in temp:
    #                 if "joint holder" in t.lower():
    #                     Name = lines[1]
    
    for i,l in enumerate(lines):      
        
        # VIJAYA BANK
        if Name == "NA" or Name == '':
            if "VIJAYA BANK" in lines[0:2]:
                if "user details" in l.lower():
                    Name = lines[i+1]
        
        if Name == "NA" or Name == '':
            if "AXIS BANK" in lines[0:2]:
                if "joint holder" in l.lower():
                    Name = lines[i-1]

        # Kotak mahindra bank
        if Name == "NA" or Name == '':
            if "kotak mahindra bank" in l.lower():
                print("Second1")
                if "date" in lines[i+1].lower():
                    Name = lines[i+2]
                elif "page" in lines[i+1].lower():
                    Name = lines[i+3]
                elif "account" not in lines[i+1].lower():
                    Name = lines[i+1]
                Name = re.sub('[^A-Za-z\s]+','',Name)
                Name = Name.replace("Period",'').replace("to",'')
        
        
                        
        # Tamilnad Merchant
        if Name == "NA" or Name == '':
            if "my transactions" in l.lower():
                print("First3")
                Name = lines[i+1]
                Name = Name.replace("Account",'').replace("Number",'')
    
        if Name == "NA" or Name == '':
            if "bank of india" not in lines[0].lower():
                if "account type" in l.lower() or "product type" in l.lower():
                    print("First",l)
                    if lines[i+1].isupper()==True and "personal" not in lines[i+1].lower():
                        lines[i+1] = lines[i+1].replace("CUSTOMER",'').replace("DETAILS",'')
                        Name = lines[i+1]
                        
        # Central Bank of India
        if Name == "NA" or Name == '':
            if "central bank of india" in lines[0].lower():
                if "account type" in l.lower() or "product type" in l.lower():
                    print("First",l)
                    if lines[i+1].isupper()==True and "personal" not in lines[i+1].lower():
                        lines[i+1] = lines[i+1].replace("CUSTOMER",'').replace("DETAILS",'')
                        Name = lines[i+1]
        
         # Indusland bank
        if Name == "NA" or Name == '':
            name = ''
            if "indusland bank" in l.lower() or "induslnd bank" in l.lower() or "indusind bank" in l.lower():
                print("Indusland Bank",l)
                # print(lines[i+2])
                Name = lines[i+2]
                if "Address" in Name:
                    name_list = Name.split(" ")
                    index_of = name_list.index("Address")
                    for l1 in name_list[:index_of]:
                        name = name + " " + l1
                        Name = name

        
        # RBL BANK
        if Name == "NA" or Name == '':
            if "accountholder" in l.lower():
                print("First6")
                l_list = l.split(":")
                for l1 in l_list:
                    l1 = l1.replace("Home",'').replace("Branch",'')
                    l1 = l1.strip()
                    if l1.isupper()==True:
                        Name = l1
                        break
        
        # Federal bank
        if Name == "NA" or Name == '':
             
             if "name and address" in l.lower():
                 print("First2")
                 Name = lines[i+1] + " " + lines[i+2]
        
        if Name == "NA" or Name == '':  
          if "account name" in l.lower() or "customer name" in l.lower():
              print("First8")
            #   print(l)
              l = l.replace("Account",'').replace("Name",'').replace("No",'').replace("Customer",'').replace("Nickname",'').replace("Number",'')
              print(l)
              Name = l
    if bool(re.search(r'[0-9]',Name))==True:
        Name = "NA"
             
    # Indusland bank
    if Name == "NA" or Name == '':
        print("Inside")
        name = ''
        for row in df.itertuples():
#            print(row)
            if "indusind" in row[1].lower() or "induslnd" in row[1].lower() or "indusland" in row[1].lower():
                print("Indusland Bank-2",l)
                y_coord = row[3]
                mask = df['y0']<y_coord+200
                coord_list = df[mask]['word'].tolist()
                print(coord_list)
                
                for c in coord_list:
                    if c.isupper()==True:
                        name = name +  ' ' + c
                        
                Name = name
                break
        
        
    # UNION
    if Name == "NA" or Name == '':
        for i,l in enumerate(lines[:10]):
            if "to" in l.lower() and "date:" in l.lower():
                print("First4")
                Name = lines[i+1]
                Name = Name.replace("CD GENRAL",'')
                Name = Name.strip()     
                
    
                    
    if Name == "NA" or Name == '':
        for l in lines:
            if "name" in l.lower() and "branch" in l.lower():
                l_list = l.split(":")
                for l1 in l_list:
                    l1 = l1.replace("Branch",'').replace("Name",'')
                    l1 = l1.strip()
                    if l1.isupper()==True:
                        Name = l1
                        break
                
    
    
    for l in lines:
        if Name == "NA" or Name == '':
            if ("m/s" in l.lower() or "mr" in l.lower() or "mrs" in l.lower() or "ms." in l.lower()) and "generated by" not in l.lower():
                print("Firs7",l)
                l = l.replace("Account",'').replace("Name",'').replace("No",'').replace("OD Limit",'').replace("Your",'').replace("Details",'').replace("Address",'')
                name_list.append(l)
            Name = " ".join(n for n in name_list)
        
        if Name == "NA" or Name == '':
            if "customer details" in l.lower():
                l = l.replace("CUSTOMER DETAILS",'')
                Name = l
        
        if Name == "NA" or Name == '':
           if "name" in l.lower() and "branch" not in l.lower() and "account" not in l.lower() and "customer" not in l.lower():
               print("First11",l)
               if ":" in l:
                   list_ = l.split(":")
                   for l1 in list_:
                       if l1.isupper()==True:
                           Name = l1
               else:
                   print("First12",l)
                   l1 = l.replace("Name",'')
                   if l1.isupper()==True:
                       Name = l1
        
        # ICICI
        if Name == "NA" or Name == '':
            name = ''
            if "account number" in l.lower() and "-" in l:
                l_list = l.split("-")
                for l1 in l_list:
                    if l1.isupper()==True:
                        name = name + " " + l1 
                Name = name
            if ('transactions list') in l.lower() :
                l_list = l.split("-")
                for l1 in l_list:
                    if l1.isupper()==True:
                        name = name + " " + l1 
                Name = name
                
        # BOI
        if Name == "NA" or Name == '':
            if "bank of india" in lines[0].lower():
                if "name" in l.lower() and "account" in l.lower():
                   l = l.replace("Account",'').replace("No",'')
                   print("First20",l)
                   if ":" in l:
                       list_ = l.split(":")
                       for l1 in list_:
                           if l1.isupper()==True:
                               Name = l1
                   else:
                       print("First21",l)
                       l1 = l.replace("Name",'')
                       if l1.isupper()==True:
                           Name = l1
    
    if Name == "NA" or Name == '':
        for i,l in enumerate(lines[:10]):
            if "statement of account" in l.lower():
                print("First5")
                Name = lines[i+1]
                Name = Name.strip()
            if "account statement" in l.lower() and bool(re.search(r'[0-9]',l))==False:
                print("First14",l)
                if "as of" in lines[i+1].lower():
                    Name = lines[i+2]
                else:
                    Name = lines[i+1]
                Name = Name.strip()
            
    return Name
        
    
def Account_num(lines):
    Account = "NA"
    for l in lines:
        # print("LLL",l)
        if "account number" in l.lower() and bool(re.search(r'[0-9]',l))==True and Account == "NA":
            print("Account1",l)
            l_list = l.split(" ")
            for i in l_list:
                i = re.sub('[^0-9]+','',i)
                if len(i)>=9:
                    Account = i
        elif "account no" in l.lower() and bool(re.search(r'[0-9]',l))==True and Account == "NA":
            print("Account2",l)
            l_list = l.split(" ")
            for i in l_list:
                i = re.sub('[^0-9]+','',i)
                if len(i)>=9:
                    Account = i
        elif ("account" in l.lower() or 'ccount' in l.lower() or "a/c" in l.lower()) and bool(re.search(r'[0-9]',l))==True and Account == "NA" and "cust id :" not in l.lower() and "a/c type" not in l.lower():
            print("Account3",l)
            l_list = l.split(" ")
            for i in l_list:
                i = re.sub('[^0-9]+','',i)
                if len(i)>=9:
                    Account = i
                    break
        elif "number" in l.lower() and bool(re.search(r'[0-9]',l))==True and Account == "NA":
            print("Account4",l)
            l_list = l.split(" ")
            for i in l_list:
                i = re.sub('[^0-9]+','',i)
                if len(i)>=9:
                    Account = i

        elif "transactions list" in l.lower() and bool(re.search(r'[0-9]',l))==True and Account == "NA":
            print("Account5",l)
            l_list = l.split(" ")
            for i in l_list:
                i = re.sub('[^0-9]+','',i)
                if len(i)>=9:
                    Account = i
        elif "statement for alc" in l.lower() and bool(re.search(r'[0-9]',l))==True and Account == "NA":
            print("Account6",l)
            l_list = l.split(" ")
            for i in l_list:
                i = re.sub('[^0-9]+','',i)
                if len(i)>=9:
                    Account = i           

    # Indian Overseas bank
    for i,l in enumerate(lines):
        if "indian overseas bank" in l.lower():
            l_list = lines[i+2].split(" ")
            for l1 in l_list:
                if len(l1)>9 and bool(re.search(r'[0-9]',l1))==True:
                    Account = l1
    return Account

def ocr(image_path,lang_hint,apikey_path):
        '''
        Accepts image path and language hint 
        Returns two items: 
            (i)  list of list containing words and their corresponding 4 vertices(x,y)
            (ii) blocks of ocr text
        '''
    
        bboxes = None
        blocks = None
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = apikey_path
        vision_client = vision.ImageAnnotatorClient()
        
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            image = types.Image(content=content)

            kwargs = {}
            if lang_hint:
                kwargs = {"image_context": {"language_hints": ["en", "hi", "mr", "bn", "ta",'te','kn','gu','or']}}

            response = vision_client.text_detection(image=image,**kwargs)
            texts = response.text_annotations

            bboxes = []
            for text in texts:
                bbox = []
                bbox.append(text.description)
                for vertice in text.bounding_poly.vertices:
                    bbox.extend([vertice.x,vertice.y])
                bboxes.append(bbox)

            document = response.full_text_annotation

            paratext = ""
            blocktext = ""
            blocks = []

            for page in document.pages:
                for block in page.blocks:
                    blocktext = ""
                    for paragraph in block.paragraphs:
                        paratext = ""
                        for word in paragraph.words:
                            strWord = ""
                            for symbol in word.symbols:
                                strWord = strWord + symbol.text
                            paratext = paratext + " " + strWord
#                            print(strWord)
                        blocktext = blocktext + " " + paratext
#                        print(paratext)
                    blocks.append(blocktext.strip())
            
        except:
            traceback.print_exc()
            bboxes = None
            blocks=None
        
        finally:
            return bboxes,blocks 
        
def group_ocr_words(ocr_list,min_word_length=4,line_split=0.8,debug=False):
        '''
        Accepts word list with coordinates. All eight points of vertices need to be passed
        Returns grouped df with line number and word ascending order (bool)
        '''
        df = pd.DataFrame(ocr_list,columns=('word','x0','y0','x1','y1','x2','y2','x3','y3'))
        
        ##############################################################################
        # Slope and intercept for each of the words
        ##############################################################################
        df['slope'] = (df['y1']+df['y2']-df['y0']-df['y3'])/(df['x1']+df['x2']-df['x0']-df['x3'])
        
        # Words with len >=4 are considered as significant
        slopes = df[df['word'].str.len()>=min_word_length]['slope']

        # To remove infinity and outlier slopes; Two iterations of std of slopes
        if slopes[np.isinf(slopes)].shape[0] <= slopes.shape[0]//3:
            slopes = slopes[~np.isinf(slopes)]
            slopes = slopes[abs(slopes - np.mean(slopes)) <= np.std(slopes)]
            mean_slope = slopes[abs(slopes - np.mean(slopes)) <= np.std(slopes)].mean() 
        else:
            mean_slope = slopes[np.isinf(slopes)].mode()   
            mean_slope = mean_slope.tolist()[0]

        if np.isinf(mean_slope):
            df['intercept'] = df['x0']+df['x1']
        else:
            df['intercept'] = df['y1']+df['y2']-(mean_slope*(df['x1']+df['x2']))
        
        ##############################################################################
        # For determining word order and line order
        # True - Ascending, False - Descending
        ##############################################################################
        df['x_diff'] = df['x1']>df['x0']
        df['y_diff'] = df['y1']>df['y0']

        if mean_slope > -1 and mean_slope < 1:
            word_order = df[df['word'].str.len()>=min_word_length]['x_diff'].mode()[0]
            df['order'] = df['x0']
        else:
            word_order = df[df['word'].str.len()>=min_word_length]['y_diff'].mode()[0]
            df['order'] = df['y0']       
            
        if mean_slope > -1 and not np.isinf(mean_slope):
            line_order = word_order
        else:
            line_order = not word_order
            
        ##############################################################################
        # To separate lines based on the intercept
        ##############################################################################
        scaler = MinMaxScaler()
        df['fit'] = scaler.fit_transform(df[['intercept']])
        
        if not line_order:
            df['fit'] = 1.0-df['fit']
        df = df.sort_values(by=['fit'])
        
        df['fit_diff'] = df['fit'].diff()
        mean_diff = df['fit_diff'].mean()
        
        line_no = 1
        for index, row in df.iterrows():
            if row['fit_diff'] > mean_diff*line_split:
                line_no += 1
                df.loc[index, 'line'] = line_no
            else:
                df.loc[index, 'line'] = line_no   
        
        if debug:
            print(mean_diff,' ',mean_slope)
        else:
            df = df.drop(['slope','intercept','fit','fit_diff','x_diff','y_diff'],axis=1)
            
        return df,word_order



def generate_lines(df,word_order):
        '''
        Accepts grouped df and word_order(bool)
        Returns list of lines in the df
        '''
        
        list_df = [df_g for name_g, df_g in df.groupby('line')]
        new_list_df = [l.sort_values('order',ascending=word_order) for l in list_df]
        
        lines = []
        for ldf in new_list_df:
            line = ' '.join([re.sub(r'[^A-Za-z0-9,.\-\:/ ]','',w) for w in ldf['word'].to_list()]).strip()
            if line:
                lines.append(line)

        return lines
    
def BS_attributes(filename,df,word_order):
    # df = pd.read_csv("/home/anirudh/Documents/AxisBank_cheque/Cheque_final/Result_cheque.csv")
    BS_SCHEMA = {
            'Account':'',
            'Name':'',
            'Date':'',
            'IFSC':''}
    
#    image_path = filename.split(".pdf")
#    image_path = image_path[0] + "-page0" + ".jpg"
#    print(image_path)
        
#        file_path_deskewed = imagedeskewing(file_path)
    # boxes = ocr(filename,False,apikey)
    # print("boxes,boxes",boxes)
    # word_order = True
    df = pd.read_json(df)
    # print(df)
    # df,word_order = group_ocr_words(boxes[0][1:])
    # print('+++++++++++++++++++++++++++++++++++++++++++',df,'---------------------------------',word_order)
    lines = generate_lines(df,word_order)
    # print(lines)
    
    Account = Account_num(lines)
    Account = re.sub('[^0-9]+','',Account)
    Name = NameAttr(df,lines)
    dirt_list = ["Branch","No","STATEMENT","OF ","ACCOUNT","Account","Name"]
    Name = re.sub('[^a-zA-Z\s,.()]+','',Name)
    name_list = Name.split(" ")
    for d in dirt_list:
        for n in name_list:
            if d in n:
                name_list.remove(n)
    Name = " ".join(name_list)
    Name = Name.strip()
    Name = Name.replace('MS.','').replace('MR.','')
    Name = Name.replace('MS','').replace('MR','')

    Range = DateAttr(lines)
    IFSC = IFSCAttr(lines)
    
    BS_SCHEMA['Account']=Account 
    BS_SCHEMA['Name']=Name
    BS_SCHEMA['Date']=Range
    BS_SCHEMA['IFSC']=IFSC
    print("++++++++++++  BS_SCHEMA  +++++++++",BS_SCHEMA)
    return BS_SCHEMA


# filename = "/home/rahul/workspace/bank_statement_analyser/static/data/input/bank_statement_518/BS_Sample-page0.jpg"
# #c = pdf2jpg(filename)

# BS_attributes(filename) 