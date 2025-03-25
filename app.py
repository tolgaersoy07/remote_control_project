import boto3
import requirements
from flask import Flask,request,render_template,redirect,url_for,jsonify,session
import requests
from flask_socketio import SocketIO, emit
import time
import json
import test
from DB_ITEM import dynamodb
from botocore.exceptions import NoCredentialsError,PartialCredentialsError

app=Flask(__name__)
session_userID=""
app.secret_key=requirements.app_secret_key
socketio=SocketIO(app)

@app.route('/',methods=['GET'])
def index():
    return render_template('login.html',data_sitekey=requirements.data_sitekey)

@app.route('/login',methods=['POST'])
def login():
    userID=request.form.get('username')
    password=request.form.get('password')
    table=dynamodb.Table('Users')
    data={'secret':requirements.secret,'response':request.form.get('g-recaptcha-response')}
    r=requests.post('https://www.google.com/recaptcha/api/siteverify',data=data).json()
    if not r['success']:
        return render_template('login.html',error='!!! reCAPTCHA HATASI !!!',data_sitekey=requirements.data_sitekey)
    response=table.get_item(Key={'userID':userID})
    if 'Item' in response:
        spassword=response['Item'].get('password','')
        if spassword==password:
            session['userID']=userID
            global session_userID
            session_userID=userID
            if userID=="admin":
                return render_template('admin.html')
            return redirect('/user_dashboard')
        else:
            return render_template('login.html',data_sitekey=requirements.data_sitekey,error="!!! Şifre hatalıdır. !!!")
    return render_template('login.html',data_sitekey=requirements.data_sitekey,error="!!! Kullanıcı adı bulunamadı. !!!")

@app.route('/forgetted_info',methods=['POST'])
def forgetted_info():
    return render_template('update_enter_info.html',data_sitekey=requirements.data_sitekey)

@app.route('/reset', methods=['POST'])
def reset():
    data={'secret':requirements.secret,'response':request.form.get('g-recaptcha-response')}
    r=requests.post('https://www.google.com/recaptcha/api/siteverify',data=data).json()
    if not r['success']:
        return render_template('update_enter_info.html',info="",error="!!! reCAPTCHA HATASI !!!",data_sitekey=requirements.data_sitekey)
    email=request.form.get('eMail')
    phone=request.form.get('pNumber')
    if email:
        s=test.send_user_info("eMail",email)
        if "bulunamadı" in s:
            return render_template('update_enter_info.html',info="",error=s,data_sitekey=requirements.data_sitekey)
        return render_template('update_enter_info.html',info=s,error="",data_sitekey=requirements.data_sitekey)
    elif phone:
        s=test.send_user_info("pNumber",phone)  
        if "bulunamadı" in s:
            return render_template('update_enter_info.html',info="",error=s,data_sitekey=requirements.data_sitekey)    
        return render_template('update_enter_info.html',info=s,error="",data_sitekey=requirements.data_sitekey)
    return render_template('update_enter_info.html',info="",error="!!! Lütfen bilgilerinizi giriniz. !!!",data_sitekey=requirements.data_sitekey)

@app.route('/logout',methods=['POST'])
def login_out():
    session.clear() 
    return render_template('login.html',data_sitekey=requirements.data_sitekey)

@app.route('/redirect_from_admin',methods=['POST'])
def redirect_page():
    destination=request.form.get('destination')
    n="2"
    if session['userID']!="admin":
        n="3"
    if destination=="musteri-tablolar":
        a,b=test.print_users27(session['userID'])
        return render_template('customers.html',result=a,parent=b)
    elif destination=="cihaz-tablolar":
        a,b=test.table_parser40(session['userID'])
        return render_template('list_devices.html',array=a,uniqueID=b)
    elif destination=="cihaz-ekleme":
        return render_template('add_device.html',array=test.get_user_info(n,session['userID']),output="")
    elif destination=="kullanici-kaydet":
        return render_template('register.html',array=test.get_all_parent())
    elif destination=="profilimi_duzenle":
        return render_template('edit_profile.html',data=test.print_user(session['userID']))

@app.route('/update_profile',methods=['POST'])
def update_profile():
    table=dynamodb.Table("Users")
    cAddress=request.form.get('cAddress')
    cName=request.form.get('cName')
    cNumber=request.form.get('cNumber')
    eMail=request.form.get('eMail')
    name=request.form.get('name')
    password=request.form.get('password')
    pNumber=request.form.get('pNumber')
    surName=request.form.get('surName')
    taxNumber=request.form.get('taxNumber')
    tcNumber=request.form.get('tcNumber')
    userAddress=request.form.get('userAddress')
    update_expression="""
        SET #cAddress=:cAddress, 
            #cName=:cName, 
            #cNumber=:cNumber, 
            #eMail=:eMail, 
            #name=:name, 
            #password=:password, 
            #pNumber=:pNumber, 
            #surName=:surName, 
            #taxNumber=:taxNumber, 
            #tcNumber=:tcNumber, 
            #userAddress=:userAddress"""
    expression_attribute_values={
        ':cAddress':cAddress,
        ':cName':cName,
        ':cNumber':cNumber,
        ':eMail':eMail,
        ':name':name,
        ':password':password,
        ':pNumber':pNumber,
        ':surName':surName,
        ':taxNumber':taxNumber,
        ':tcNumber':tcNumber,
        ':userAddress':userAddress}
    expression_attribute_names={
        '#cAddress':'cAddress',
        '#cName':'cName',
        '#cNumber':'cNumber',
        '#eMail':'eMail',
        '#name':'name',
        '#password':'password',
        '#pNumber':'pNumber',
        '#surName':'surName',
        '#taxNumber':'taxNumber',
        '#tcNumber':'tcNumber',
        '#userAddress':'userAddress'}
    response = table.update_item(
        Key={'userID':request.form.get('userID')},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names)
    if request.form.get('page_info')=="edit_profile.html":
        return render_template('edit_profile.html',data=test.print_user(session['userID']),output="!!! Kullanıcı bilgileri güncellenmiştir. !!!")
    a,b=test.print_users27(session['userID'])
    return render_template('customers.html',output="!!! Kullanıcı bilgileri güncellenmiştir. !!!",result=a,parent=b)

@app.route('/edit_profile',methods=['POST'])
def edit_profile():
    return render_template('edit_profile.html',data=test.print_user(session['userID']))

@app.route('/register', methods=['POST'])
def register():
    userID=request.form.get('userID')
    array={}
    array['name']=request.form.get('name')
    array['surName']=request.form.get('surName')
    array['userID']=request.form.get('userID')
    array['password']=request.form.get('password')
    array['eMail']=request.form.get('eMail')
    array['pNumber']=request.form.get('pNumber')
    array['userAddress']=request.form.get('userAddress')
    array['tcNumber']=request.form.get('tcNumber')
    array['status']=request.form.get('status')
    array['cName']="NONE"
    array['cAddress']="NONE"
    array['cNumber']="NONE"
    array['taxNumber']="NONE"
    if array['status']=="Kurumsal":
        array['cName']=request.form.get('cName')
        array['cAddress']=request.form.get('cAddress')
        array['cNumber']=request.form.get('cNumber')
        array['taxNumber']=request.form.get('taxNumber')
    if session['userID']=="admin":
        array['userType']=request.form.get('userType')
        array['userParent']="admin"
        if array['userType']=="3":
            array['userParent']=request.form.get('parent')
    else:
        array['userParent']=session['userID']
        array['userType']="3"
    table=dynamodb.Table('Users')
    response=table.get_item(Key={'userID':userID})
    if 'Item' in response:
        return render_template('register.html',array=test.get_all_parent(),eregister="!!! Bu kullanıcı adı sisteme kayıtlıdır. !!!")        
    table.put_item(Item=array)
    return render_template('register.html',array=test.get_all_parent(),eregister="!!! Sisteme kayıt oldunuz. !!!")
    
@app.route('/submit_form',methods=['POST'])
def submit_form():
    userID=request.form.get('username')
    dName=request.form.get('objectName')
    bnames=request.form.get('buttonNames')
    bdecs=request.form.get('buttonDescriptions')
    bstates=request.form.get('buttonStates')
    bpins=request.form.get('buttonPins')
    tnames=request.form.get('textboxValues')
    tdecs=request.form.get('textboxDescriptions')
    tpins=request.form.get('textboxPins')
    gnames=request.form.get('gaugeValues')
    gdecs=request.form.get('gaugeDescriptions')
    gpins=request.form.get('gaugePins')
    g2names=request.form.get('needleValues')
    g2decs=request.form.get('needleDescriptions')
    g2pins=request.form.get('needlePins')
    bnames=json.loads(bnames) if bnames else []
    bdecs=json.loads(bdecs) if bdecs else []
    bstates=json.loads(bstates) if bstates else []
    bpins=json.loads(bpins) if bpins else []
    tnames=json.loads(tnames) if tnames else []
    tdecs=json.loads(tdecs) if tdecs else []
    tpins=json.loads(tpins) if tpins else []
    gnames=json.loads(gnames) if gnames else []
    gdecs=json.loads(gdecs) if gdecs else []
    gpins=json.loads(gpins) if gpins else []
    g2names=json.loads(g2names) if g2names else []
    g2decs=json.loads(g2decs) if g2decs else []
    g2pins=json.loads(g2pins) if g2pins else []
    output=test.create_json(userID,dName,bnames,bdecs,bstates,bpins,tnames,tdecs,tpins,gnames,gdecs,gpins,g2names,g2decs,g2pins)
    n="2"
    if session['userID']!="admin":
        n="3"
    return render_template('add_device.html',array=test.get_user_info(n,session['userID']),output=output)

@app.route('/delete_user',methods=['POST'])
def delete_user():
    userID=request.form['userID']
    if userID!=session['userID']:
        print("silme basarili",flush=True)
        test.delete_user(userID)
    a,b=test.print_users27(session['userID'])
    return render_template('customers.html',result=a,parent=b)

@app.route('/go_page', methods=['POST'])
def go_page():
    userID=request.form.get('userID')
    a,b=test.table_parser40(userID)
    return render_template('list_devices.html',array=a,uniqueID=b,page_name_send="active")

@app.route('/process_form', methods=['POST','GET'])
def process_form():
    D_VALUE=request.form.get('D_VALUE')
    if D_VALUE:
        test.delete_device(D_VALUE)
        a,b=test.table_parser40(session['userID'])
        return render_template('list_devices.html',array=a,uniqueID=b)
    data=request.form
    array=[]
    for key, value in data.items():
        if key.startswith("TBOX_") and value:
            array.append([key[5:],value])
        elif key.startswith("H_") and value!="N":
            array.append([key[2:],value])
    test.update_table30(array)
    if request.form.get("page_name")=="user_dashboard.html":
        a,b=test.table_parser40(session['userID'])
        return render_template('user_dashboard.html',array=a,uniqueID=b)
    a,b=test.table_parser40(session['userID'])
    return render_template('list_devices.html',array=a,uniqueID=b)

@app.route('/user_dashboard',methods=['POST','GET'])
def users_dashboard():
    table=dynamodb.Table('Users')
    response=table.get_item(Key={'userID':session['userID']})
    userType=response.get('Item')['userType']
    if userType in ["1","2"]:
        return render_template("admin.html")
    a,b=test.table_parser40(session['userID'])
    return render_template('user_dashboard.html',array=a,uniqueID=b)

thread_flags,threads={},{}
def background_thread(sid):
    global thread_flags
    while thread_flags.get(sid,False):
        gauge_data=test.get_gdata(session_userID)
        socketio.emit('update_gauges',gauge_data,to=sid)
        time.sleep(1)
@socketio.on('connect')
def on_connect():
    sid=request.sid
    thread_flags[sid]=True
    threads[sid]=socketio.start_background_task(background_thread, sid)
@socketio.on('disconnect')
def on_disconnect():
    sid=request.sid
    thread_flags[sid]=False
    if sid in threads:
        threads[sid].join()
        del threads[sid]
        del thread_flags[sid]

@app.route('/turn_back', methods=['POST'])
def turn_back():
    if request.form.get('page_back'):
        a,b=test.print_users27(session['userID'])
        return render_template('customers.html',result=a,parent=b) 
    table=dynamodb.Table('Users')
    response=table.get_item(Key={'userID':session['userID']})
    userType=response.get('Item')['userType']
    if userType=="3":
        return redirect('/user_dashboard')
    elif userType=="1" or userType=="2":
        return render_template("admin.html")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)