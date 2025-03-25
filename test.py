import boto3
from DB_ITEM import dynamodb
import yagmail
import json
import requirements
import sys
import io
import base64
from flask import session
import re
from boto3.dynamodb.conditions import Attr
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

def send_user_info(opinion,info):
    table=dynamodb.Table("Users")
    response=table.scan(FilterExpression=Attr(opinion).eq(info))
    if response['Items']:
        s="SİSTEME GİRİŞ BİLGİLENİRİZ AŞAĞIDADIR.\nKullanıcı Adı:"+response['Items'][0]['userID']+"\nŞifre:"+response['Items'][0]['password']
        if opinion=="pNumber":
            #pno: response['Items'][0]['pNumber']
            #telefona gönder.api ekle
            return "!!! Giriş bilgileriniz telefon numaranıza gönderildi. !!!"
        elif opinion=="eMail":
            yag=yagmail.SMTP(requirements.mail,requirements.password)
            yag.send(to=response['Items'][0]['eMail'],subject='Parosis Giriş Bilgileri',contents=s)
            return "!!! Giriş bilgileriniz mail adresinize gönderildi. !!!"
    return "!!! Girilen bilgiler sistemde bulunamadı. !!!"

def print_user(userID):
    table=dynamodb.Table("Users")
    return table.get_item(Key={'userID':userID})['Item']

def get_all_parent():
    table=dynamodb.Table("Users")
    response=table.scan(FilterExpression=Attr('userType').eq("2"))['Items']
    result={}
    for item in response:
        result[item['userID']]=item['userID']+":"+item['name']+" "+item['surName']
    return result

def get_user_info(n,userID):
    table=dynamodb.Table("Users")
    response=table.scan()['Items']
    result={}
    for item in response:
        if n=="2":
            result[item['userID']]=item['name']+" "+item['surName']+" : "+item['userType']
        elif n=="3" and item['userParent']==userID and item['userType']=="3":
            result[item['userID']]=item['name']+" "+item['surName']+" : "+item['userType']
    if n=="2":
        del result['admin']
    return result

def pin_validate(array):
    for i in array:
        if not i.isdigit():
            return "!!! Yazım hatası yapılmıştır. !!! Pin No: "+i
    return 1

def create_json(userID,dName,bnames,bdecs,bstates,bpins,tnames,tdecs,tpins,gnames,gdecs,gpins,g2names,g2decs,g2pins):
    if not (bnames or bdecs or bstates or bpins or tnames or tpins or gnames or gdecs or gpins or g2names or g2decs or g2pins):
        return "!!! Araç bilgilerini giriniz. !!!"
    dictionary1={}
    dictionary2={}
    dictionary3={}
    dictionary4={}
    dictionary5={}
    dictionary6={}
    dictionary7={}
    dictionary8={}
    if bnames and bdecs and bstates and bpins:
        output=pin_validate(bpins)
        if output!=1:
            return output
        dictionary1.update(zip(bnames,bstates)) #data
        dictionary2.update(zip(bnames,bdecs)) #explain
        dictionary3.update(zip(bnames,bpins)) #dpin
        dictionary4.update(zip(bnames,['BUTTON']*len(bnames))) #dtype
    if tnames and tdecs and tpins:
        output=pin_validate(tpins)
        if output!=1:
            return output
        a,b=[],[]
        for item in tnames: #
            if re.match(r"^[\w\d]+:\d+$",item):
                x,y=item.split(":")
                a.append(x)
                b.append(y)
            else:
                return "!!! Yazım hatası yapılmıştır. !!! Textbox ekle --> "+item
        dictionary1.update(zip(a,b)) #data
        dictionary2.update(zip(a,tdecs)) #explain
        dictionary3.update(zip(a,tpins)) #dpin
        dictionary4.update(zip(a,['TEXTBOX']*len(tnames))) #dtype
    if gnames and gdecs and gpins:
        output=pin_validate(gpins)
        if output!=1:
            return output
        a,b=[],[]
        for item in gnames:
            if re.match(r'^[^:]+:(\d+|True|False)$',item):
                x,y=item.split(":")
                a.append(x)
                b.append(y)
            else:
                return "!!! Yazım hatası yapılmıştır. !!! Gösterge ekle --> "+item
        dictionary5.update(zip(a,b)) #gdata
        dictionary6.update(zip(a,gdecs)) #gexplain
        dictionary7.update(zip(a,gpins)) #gpin
        dictionary8.update(zip(a,["BUTTON" if value in ["True","False"] else "TEXTBOX" for value in b])) #gtype
    if g2names and g2decs and g2pins:
        output=pin_validate(g2pins)
        if output!=1:
            return output
        a,b=[],[]
        for item in g2names:
            if re.match(r'^[^:]+:(\d+,\d+,\d+)$',item):
                x,y=item.split(":")
                a.append(x)
                b.append(y)
            else:
                return "!!! Yazım hatası yapılmıştır. !!! İbre ekle --> "+item
        dictionary5.update(zip(a,b)) #gdata
        dictionary6.update(zip(a,g2decs)) #gexplain
        dictionary7.update(zip(a,g2pins)) #gpin
        dictionary8.update(zip(a,['GAUGE']*len(a))) #gtype
    table=dynamodb.Table("DataTable")
    table.put_item(
        Item={
            'uniqueID':get_max_uniqueID(),
            'userID':userID,
            'dName':dName,
            'data':json.dumps(dictionary1,indent=4),
            'explain':json.dumps(dictionary2,indent=4),
            'dpin':json.dumps(dictionary3,indent=4),
            'dtype':json.dumps(dictionary4,indent=4),
            'gdata':json.dumps(dictionary5,indent=4),
            'gexplain':json.dumps(dictionary6,indent=4),
            'gpin':json.dumps(dictionary7,indent=4),
            'gtype':json.dumps(dictionary8,indent=4)
            })
    return "!!! Araç sisteme eklendi. !!!"

def get_max_uniqueID():
    table=dynamodb.Table("DataTable")
    response=table.scan(ProjectionExpression="uniqueID")
    max=0
    for i in response['Items']:
        if int(i['uniqueID'])>max:
            max=int(i['uniqueID'])
    return str(max+1)

def delete_user(userID):
    table=dynamodb.Table('Users')
    response=table.scan(FilterExpression=Attr('userParent').eq(userID))['Items']
    array=[userID]
    table.delete_item(Key={'userID':userID})
    for item in response:
        array.append(item['userID'])
        table.delete_item(Key={'userID':item['userID']})
    table=dynamodb.Table('DataTable')
    response=table.scan(FilterExpression=Attr('userID').is_in(array))['Items']
    for item in response:
        table.delete_item(Key={'uniqueID':item['uniqueID']})
    return "Kişi silme işlemi gerçekleşmiştir."

def delete_device(uniqueID):
    table=dynamodb.Table("DataTable")
    table.delete_item(Key={'uniqueID':uniqueID})
   
def get_gdata(userID):
    data=[]
    if userID!="admin":
        table=dynamodb.Table("Users")
        array=[userID]
        response=[]
        condition=table.scan(FilterExpression=Attr('userID').eq(userID))['Items']
        if condition:
            condition=condition[0]['userType']
        if condition=="2":
            response=table.scan(FilterExpression=Attr('userParent').eq(userID))['Items']
        else:
            response=table.scan(FilterExpression=Attr('userID').eq(userID))['Items']
        for item in response:
            array.append(item['userID'])
        table=dynamodb.Table("DataTable")
        data=table.scan(FilterExpression=Attr('userID').is_in(array))['Items']
    else:
        table=dynamodb.Table("DataTable")
        data=table.scan()['Items']
    dictionary={}
    for i in range(len(data)):
        temporary=coder_parser(data[i].get('uniqueID','NONE'),'gdata',mini_json_parser(data[i]['gdata']))
        array=mini_json_parser(data[i]['gdata'])
        for j in range(len(temporary)):
            dictionary[temporary[j]]=array[j].split(":")[1]
    return dictionary
########################################################################
def update_table30(array):
    table=dynamodb.Table("DataTable")
    for item in array:
        a,b,c=decoder(item[0])
        if item[1]=="Y0":
            item[1]="False"
        elif item[1]=="Y1":
            item[1]="True"
        json_data=table.get_item(Key={'uniqueID':a})['Item'][b]
        dictionary=json.loads(json_data)
        dictionary[c]=item[1]
        json_data=json.dumps(dictionary,indent=4)
        table.update_item(Key={'uniqueID':a},
        UpdateExpression=f"SET #attr=:new_value",
        ExpressionAttributeNames={"#attr":b},
        ExpressionAttributeValues={':new_value':json_data})

def table_parser40(userID):
    data=[]
    if userID!="admin":
        table=dynamodb.Table("Users")
        response=table.scan(FilterExpression=Attr('userParent').eq(userID))['Items']
        array=[userID]
        for item in response:
            array.append(item['userID'])
        table=dynamodb.Table("DataTable")
        data=table.scan(FilterExpression=Attr('userID').is_in(array))['Items']
    else:
        table=dynamodb.Table("DataTable")
        data=table.scan()['Items']
    result=[]
    ID_LIST=[]
    for i in range(len(data)):
        dictionary1={}
        dictionary1['userID']=data[i].get('userID','NONE')
        dictionary1['uniqueID']=data[i].get('uniqueID','NONE')
        dictionary1['dName']=data[i].get('dName','NONE')
        dictionary1['data']=mini_json_parser(data[i]['data'])
        dictionary1['explain']=mini_json_parser(data[i]['explain'])
        dictionary1['dtype']=mini_json_parser(data[i]['dtype'])
        dictionary1['gdata']=mini_json_parser(data[i]['gdata'])
        dictionary1['gexplain']=mini_json_parser(data[i]['gexplain'])
        dictionary1['dpin']=mini_json_parser(data[i]['dpin'])
        dictionary1['gpin']=mini_json_parser(data[i]['gpin'])
        dictionary1['gtype']=mini_json_parser(data[i]['gtype'])
        result.append(dictionary1)
        dictionary2={}
        dictionary2['dName']=coder_parser(result[i]['uniqueID'],'dName',result[i]['dName'])
        dictionary2['dpin']=coder_parser(result[i]['uniqueID'],'dpin',result[i]['dpin'])
        dictionary2['gpin']=coder_parser(result[i]['uniqueID'],'gpin',result[i]['gpin'])
        dictionary2['data']=coder_parser(result[i]['uniqueID'],'data',result[i]['data'])
        dictionary2['explain']=coder_parser(result[i]['uniqueID'],'explain',result[i]['explain'])
        dictionary2['gdata']=coder_parser(result[i]['uniqueID'],'gdata',result[i]['gdata'])
        dictionary2['gexplain']=coder_parser(result[i]['uniqueID'],'gexplain',result[i]['gexplain'])
        ID_LIST.append(dictionary2)
    return result,ID_LIST

def mini_json_parser(input):
    array=json.loads(input)
    return [f"{key}:{value}" for key,value in array.items()]

def coder_parser(uniqueID,column,array):
    result=[]
    for i in range(len(array)):
        result.append(encoder(uniqueID,column,array[i].split(":")[0]))
    return result

def encoder(uniqueID,column,item):
    combined=uniqueID+":"+column+":"+item
    encoded_bytes=base64.urlsafe_b64encode(combined.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def decoder(input):
    decoded_bytes = base64.urlsafe_b64decode(input.encode('utf-8'))
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str.split(":")

def print_users27(userID):
    response=dynamodb.Table('Users').scan()['Items']
    control=userID=="admin"
    result={}
    parent={}
    for i in range(len(response)):
        if userID==response[i].get('userID','NONE') or userID==response[i].get('userParent','NONE') or control:
            dictionary={}
            dictionary['userID']=response[i].get('userID','NONE')
            dictionary['cAddress']=response[i].get('cAddress','NONE')
            dictionary['cName']=response[i].get('cName','NONE')
            dictionary['cNumber']=response[i].get('cNumber','NONE')
            dictionary['eMail']=response[i].get('eMail','NONE')
            dictionary['name']=response[i].get('name','NONE')
            dictionary['password']=response[i].get('password','NONE')
            dictionary['pNumber']=response[i].get('pNumber','NONE')
            dictionary['status']=response[i].get('status','NONE')
            dictionary['surName']=response[i].get('surName','NONE')
            dictionary['taxNumber']=response[i].get('taxNumber','NONE')
            dictionary['tcNumber']=response[i].get('tcNumber','NONE')
            dictionary['userAddress']=response[i].get('userAddress','NONE')
            dictionary['userParent']=response[i].get('userParent','NONE')
            dictionary['userType']=response[i].get('userType','NONE')
            result[dictionary['userID']]=dictionary
        if userID=="admin":
            if response[i].get('userType','NONE')=="3":
                if response[i].get('userParent','NONE') in parent:
                    parent[response[i].get('userParent','NONE')].append(response[i].get('userID','NONE'))
                else:
                    parent[response[i].get('userParent','NONE')]=[response[i].get('userID','NONE')]
        elif response[i].get('userParent','NONE')==userID:
            if response[i].get('userParent','NONE') in parent:
                parent[response[i].get('userParent','NONE')].append(response[i].get('userID','NONE'))
            else:
                parent[response[i].get('userParent','NONE')]=[response[i].get('userID','NONE')]
    return result,parent
