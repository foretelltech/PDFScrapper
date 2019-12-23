#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 08:50:56 2019

@author: eddy
"""

import io
import json
import os
import re

from pdfminer.converter import TextConverter
from pdfminer.converter import XMLConverter
from pdfminer.converter import PDFPageAggregator

from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams
from pdfminer.layout import LTTextBoxHorizontal,LTTextBox,LTTextLine

             
           


def extract_text_from_pdf(pdf_path):
    new_dict={} #To store extracted data as key, value pairs
    lines=[]   #To store data alternatively as list
    counter=1  #increments when <END> of block is reached
    a=[]       #dummy array to append elements of any section
    
    #Reset switches for data
    table=False
    partNo=False
    notes=False
    qty=False
    partname=False
    see=False
    ending=True
    new_dict["Metadata_%d" %counter]={}
    
    
    #PDF Miner Objects
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    codec='utf-8'
    laparams=LAParams()
    converter = PDFPageAggregator(resource_manager, laparams=laparams)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    w=0
    
    
    
    
    with open(pdf_path, 'rb') as fh:
        #text_from_pdf = open('text2FromPdf.txt','w')
        for pageNumber,page in enumerate(PDFPage.get_pages(fh, caching=True, check_extractable=True)):
            if pageNumber>31 and pageNumber<923 :
                page_interpreter.process_page(page)
                layout=converter.get_result()
                for element in layout:
                    if isinstance(element,LTTextBox) or isinstance(element,LTTextLine) :
                        lines.extend(element.get_text().strip())
                        
                        if(element.get_text().split()[0]=="<END>"):
                            #print(element.get_text().strip())
                            a=[];
                            table=False
                            #see=False
                            #notes=False
                            #partNo=False
                            #qty=False
                            #partname=False
                            ending=True
                            pno=new_dict["Metadata_%d" %counter]["Part Numbers"][1:] #Delete??,check last iter
                            #new_dict["Metadata_%d" %counter]["Part Numbers"]=pno
                            check =len(pno)
                            q=new_dict["Metadata_%d" %counter]["QTYs"][1:check+1]
                            #new_dict["Metadata_%d" %counter]["QTYs"]=q
                            pname=new_dict["Metadata_%d" %counter]["PART NAMEs"][3:check+3]
                            #new_dict["Metadata_%d" %counter]["PART NAMEs"]=pname
                            if(len(pno)==len(q) and len(pno)==len(pname)):
                                new_dict3 = {i:{"q":j,"p/n": k} for i, j, k in zip(pname, q, pno)}
                                    #print(new_dict3)
                                new_dict["Metadata_%d" %counter]["Parts/Components"]=new_dict3
                                
                            #Delete table columns
                            #del new_dict["Metadata_%d" %counter]["Notes"]
                            del new_dict["Metadata_%d" %counter]["Part Numbers"]
                            del new_dict["Metadata_%d" %counter]["QTYs"]
                            del new_dict["Metadata_%d" %counter]["PART NAMEs"]

                            
                            #replace metadata_counter with system name

                            super_list = new_dict["Metadata_%d" %counter]["Super"]
                            sup_idx = [i for i, item in enumerate(super_list) if re.search('^PART', item)]
                            sn_idx = [i for i, item in enumerate(super_list) if re.search('^S/N', item)]
                            
                            if sup_idx:
                               sup_idx=sup_idx[0]
                               #print(sup_idx)
                               #print(new_dict["Metadata_%d" %counter]["Super"][sup_idx])
                               new_dict["Metadata_%d" %counter]["Top"]=new_dict["Metadata_%d" %counter]["Super"][sup_idx]
                            if sn_idx:
                                sn_idx=sn_idx[0]
                                #print(sn_idx)
                                this_idx=sn_idx-1
                                new_dict["Metadata_%d" %counter]["Serial_No"]=new_dict["Metadata_%d" %counter]["Super"][sn_idx]
                                newkey=new_dict["Metadata_%d" %counter]["Super"][this_idx]
                                new_dict["Metadata_%d" %counter]["Component"]=newkey
                                new_dict[newkey]=new_dict["Metadata_%d" %counter]
                                del new_dict["Metadata_%d" %counter]["Super"]
                                del new_dict["Metadata_%d" %counter]
                            
                            
                            counter=counter+1;
                            new_dict["Metadata_%d" %counter]={}
                            
                            
                        elif(element.get_text().strip())=="NOTE":
                            
                            a=[];
                            table=True
                            notes=True
                            partNo=False
                            qty=False
                            partname=False
                            see=False
                            ending=False
                            
                        elif(element.get_text().split()[0])=="PART" and len(element.get_text().split())>1:
                            if(element.get_text().split()[1])=="NUMBER":
                                a=[];
                                partNo=True
                                table=True
                                notes=False
                                qty=False
                                see=False
                                ending=False
                            elif(element.get_text().split()[1])=="NAME":
                                a=[];
                                partname=True
                                table=True
                                notes=False
                                qty=False
                                see=False
                                ending=False
                            
                            
                        elif(element.get_text().strip().split()[0])=="QTY":
                            a=[];
                            qty=True
                            partNo=False
                            notes=False
                            partname=False
                            see=False
                            table=True
                            ending=False
                            
                        #elif(element.get_text().strip())=="PART NAME":
                           # a=[];
                            #partname=True
                            #partNo=False
                            #notes=False
                            #qty=False
                            #see=False
                            
                        elif(element.get_text().strip().split()[0])=="SEE":
                            #print(element.get_text().strip().split()[0])
                            a=[];
                            see=True
                            partNo=False
                            notes=False
                            qty=False
                            partname=False
                            table=True
                            ending=False
                        
                        if table==False and element.get_text().split()[0]!="<END>":
                            a.append(element.get_text().strip())
                            new_dict["Metadata_%d" %counter]["Super"]=a
                        w=w+1
                        if notes and table:
                            a.extend(element.get_text().strip().split('\n'))
                            #new_dict["Metadata_%d" %counter]["Notes"]=a
                        if partNo and table:
                            a.extend(element.get_text().strip().split('\n'))
                            new_dict["Metadata_%d" %counter]["Part Numbers"]=a
                        if qty and table:
                            a.extend(element.get_text().strip().split('\n'))
                            new_dict["Metadata_%d" %counter]["QTYs"]=a
                        if partname and table:
                            a.extend(element.get_text().strip().split('\n'))
                            new_dict["Metadata_%d" %counter]["PART NAMEs"]=a
                        if see and table:
                            a.append(element.get_text().strip().split('\n'))
                            #new_dict["Metadata_%d" %counter]["SEE PAGE"]=a
            
                
        
    #close open handles
    converter.close()
    fake_file_handle.close()

    if new_dict:
        return new_dict
    
    
    

if __name__ == '__main__':
    #print(extract_text_from_pdf('PARTS-MANUAL.pdf'))
    dictionary1 = (extract_text_from_pdf('PARTS-MANUAL.pdf'))
    #print(dictionary1)
    
    with open('extract.json', 'w') as fj:
        json.dump(dictionary1, fj)

