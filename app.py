from flask import Flask,request, render_template
from flask_cors import CORS
import imaplib
import email
import os

app = Flask(__name__,template_folder='templates')
CORS(app)

host = 'imap.gmail.com'     # here we are using our gmail mail servers.
username = '#############' #put your email id here
password = '###########'    # password corresponding to given email id

mail = imaplib.IMAP4_SSL(host)  #you can also use non ssl version of imaplib library.
# mail.login(username, password)
# mail.select("inbox")

text = []
unseen_mails = []
sent_mails = []
trash_mails = []
draft_mails = []

def get_formatted_mail(id_list):
    my_message = []
    for num in id_list:
        email_data = {}
        _, data = mail.fetch(num, '(RFC822)')        
        _, b = data[0]
        email_message = email.message_from_bytes(b)  
        attachments=[]
        for header in ['Subject', 'To', 'From', 'Date']:            
            email_data[header] = email_message[header]
        for part in email_message.walk():
            fileName = part.get_filename()
            if(fileName != None):
                attachments.append(fileName)
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                # body = part.get_payload()
                email_data['Body'] = body.decode()
                # email_data['Body'] = body
            elif part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True)
                # html_body = part.get_payload()
                email_data['html_body'] = html_body.decode()
                # email_data['html_body'] = html_body
        email_data['Attachment(s)']=attachments
        my_message.append(email_data)
    return my_message

def save_attachments(msg,attachments):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        # print(fileName)
        if (bool(fileName) and (fileName in attachments)):
            filePath = os.path.join(os.getcwd(), fileName)
            with open(filePath,'wb') as f:
                f.write(part.get_payload(decode=True))


@app.route('/')
def main():
    return render_template("index.html")

@app.route('/inbox.html')
def inbox_mails():
    return render_template("inbox.html")

@app.route('/sent_mails.html')
def sent_mails():
    return render_template("sent_mails.html")

@app.route('/trash_mails.html')
def trash_mails():
    return render_template("trash_mails.html")

@app.route('/draft_mails.html')
def draft_mails():
    return render_template("draft_mails.html")

@app.route('/show_body.html/<mail_body>/<mail_from>/<mail_to>/<mail_date>/<mail_subject>/<mail_attachments>/<source>',methods=['GET','POST'])
def show_body(mail_body,mail_from,mail_to,mail_date,mail_subject,mail_attachments,source):
    # print(mail_attachments)
    # print(len(mail_attachments))
    list_attachments = []
    if(len(mail_attachments) == 2):
        list_attachments = []
    else:
        mail_attachments = mail_attachments[1:len(mail_attachments)-1]
        # print(mail_attachments)
        attachments = mail_attachments.split(',')
        for k in attachments:
            stri = k.split("'")
            # print(stri)
            list_attachments.append(stri[1])
        # print(list_attachments)
        # print(type(attachments))
    len_attachments = len(list_attachments)
    print(len_attachments)
    return render_template("show_body.html",mail_body = mail_body,mail_from = mail_from,mail_to = mail_to,mail_date = mail_date,mail_subject = mail_subject,mail_attachments = list_attachments,len_attachments = len_attachments,source = source)

@app.route('/download_attachments/<attachments>/<source_of_mail>')
def download_attachments(attachments,source_of_mail):
    list_attachments2 = []
    if(len(attachments) == 2):
        list_attachments2 = []
    else:
        attachments = attachments[1:len(attachments)-1]
        # print(mail_attachments)
        attachments2 = attachments.split(',')
        for k in attachments2:
            stri = k.split("'")
            print(stri)
            list_attachments2.append(stri[1])
    if(source_of_mail == 'inbox'):
        mail.select("inbox")
    elif(source_of_mail == 'trash'):
        mail.select('"[Gmail]/Trash"')
    elif(source_of_mail == 'sent'):
        mail.select('"[Gmail]/Sent Mail"')
    elif(source_of_mail == 'draft'):
        mail.select('"[Gmail]/Drafts"')
    _, search_data_atta = mail.search(None, 'ALL')
    for num in search_data_atta[0].split():    
        _, data = mail.fetch(num, '(RFC822)')        
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        save_attachments(email_message,list_attachments2)
    return render_template('attachments_downloaded.html')
    # return render_template('show_body.html')

@app.route('/predict',methods=['GET','POST'])
def predict():
    # mail = imaplib.IMAP4_SSL(host)
    # mail.login(username, password)
    mail.select("inbox")
    _, search_data_unseen = mail.search(None, 'UNSEEN')
    _, search_data = mail.search(None, 'ALL')
    unseen_mails = get_formatted_mail(search_data_unseen[0].split())
    text = get_formatted_mail(search_data[0].split())
    text.reverse()
    return render_template('inbox.html',prediction_text=text,unseen_mails=unseen_mails)

@app.route('/sent',methods=['GET','POST'])
def sent():
    # mail = imaplib.IMAP4_SSL(host)
    # mail.login(username, password)
    mail.select('"[Gmail]/Sent Mail"')
    _, search_data_sent = mail.search(None, 'All')
    sent_mails = get_formatted_mail(search_data_sent[0].split())
    sent_mails.reverse()
    return render_template('sent_mails.html',sent_mails=sent_mails)

@app.route('/trash',methods=['GET','POST'])
def trash():
    # mail = imaplib.IMAP4_SSL(host)
    # mail.login(username, password)
    mail.select('"[Gmail]/Trash"')
    _, search_data_trash = mail.search(None, 'All')
    trash_mails = get_formatted_mail(search_data_trash[0].split())
    trash_mails.reverse()
    return render_template('trash_mails.html',trash_mails=trash_mails)

@app.route('/drafts',methods=['GET','POST'])
def drafts():
    # mail = imaplib.IMAP4_SSL(host)
    # mail.login(username, password)
    mail.select('"[Gmail]/Drafts"')
    _, search_data_drafts = mail.search(None, 'All')
    draft_mails = get_formatted_mail(search_data_drafts[0].split())
    draft_mails.reverse()
    return render_template('draft_mails.html',draft_mails=draft_mails)

@app.route('/predict_delete',methods=['GET','POST'])
def predict_delete():
    mail.select("inbox")
    _, search_data = mail.search(None, "ALL")
    for num in search_data[0].split():
       mail.store(num, '+X-GM-LABELS', '\\Trash')
    mail.expunge()
    return render_template('inbox.html',prediction_text=text,unseen_mails=unseen_mails)


@app.route('/delete_mail/<to>/<from_feild>/<date>/<subject>/<source_of_mail>',methods=['GET','POST'])
def delete_mail(to,from_feild,date,subject,source_of_mail):
    # print(source_of_mail)
    if(source_of_mail == 'inbox'):
        mail.select("inbox")
        # print("k")
    elif(source_of_mail == 'sent'):
        mail.select('"[Gmail]/Sent Mail"')
    elif(source_of_mail == 'draft'):
        mail.select('"[Gmail]/Drafts"')
    else:
        render_template('inbox.html',prediction_text=text,unseen_mails=unseen_mails)
    _, search_data = mail.search(None, "ALL")
    # all_mails = get_formatted_mail(search_data[0].split())
    for num in search_data[0].split():
        # for num in id_list:
        # email_data = {}
        _, data = mail.fetch(num, '(RFC822)')        
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        if(email_message['Date'] == date and email_message['To'] == to and email_message['From'] == from_feild and email_message['Subject'] == subject):
            mail.store(num, '+X-GM-LABELS', '\\Trash')
    mail.expunge()
    return render_template('inbox.html',prediction_text=text,unseen_mails=unseen_mails)

@app.route('/search_mail/<source_of_mail>',methods=['GET','POST'])
def search_mail(source_of_mail):
    value = request.form['search_key']
    if(source_of_mail == 'inbox'):
        mail.select("inbox")
        _, data  = mail.search(None,'FROM','"{}"'.format(value))
        _, data1  = mail.search(None,'SUBJECT','"{}"'.format(value))
        _, data2  = mail.search(None,'TO','"{}"'.format(value))
        ids = data[0].split()+data1[0].split()+data2[0].split()
        _, search_data_unseen = mail.search(None, 'UNSEEN')
        unseen_mails = get_formatted_mail(search_data_unseen[0].split())
        unseen_mails.reverse()
        text = get_formatted_mail(ids)
        text.reverse()
        return render_template('inbox.html',prediction_text=text,unseen_mails=unseen_mails)
    elif(source_of_mail == 'trash'):
        mail.select('"[Gmail]/Trash"')
        _, data  = mail.search(None,'FROM','"{}"'.format(value))
        _, data1  = mail.search(None,'SUBJECT','"{}"'.format(value))
        _, data2  = mail.search(None,'TO','"{}"'.format(value))
        ids = data[0].split()+data1[0].split()+data2[0].split()
        trash_mails = get_formatted_mail(ids)
        trash_mails.reverse()
        return render_template('trash_mails.html',trash_mails=trash_mails)
    elif(source_of_mail == 'sent'):
        mail.select('"[Gmail]/Sent Mail"')
        _, data  = mail.search(None,'FROM','"{}"'.format(value))
        _, data1  = mail.search(None,'SUBJECT','"{}"'.format(value))
        _, data2  = mail.search(None,'TO','"{}"'.format(value))
        ids = data[0].split()+data1[0].split()+data2[0].split()
        sent_mails = get_formatted_mail(ids)
        sent_mails.reverse()
        return render_template('sent_mails.html',sent_mails=sent_mails)
    elif(source_of_mail == 'draft'):
        mail.select('"[Gmail]/Drafts"')
        _, data  = mail.search(None,'FROM','"{}"'.format(value))
        _, data1  = mail.search(None,'SUBJECT','"{}"'.format(value))
        _, data2  = mail.search(None,'TO','"{}"'.format(value))
        ids = data[0].split()+data1[0].split()+data2[0].split()
        draft_mails = get_formatted_mail(ids)
        draft_mails.reverse()
        return render_template('draft_mails.html',draft_mails=draft_mails)
    # mail.select("inbox") # connect to inbox.     

@app.route('/authentication',methods=['GET','POST'])
def authentication():
    # mail = imaplib.IMAP4_SSL(host)
    usrname = request.form['username']
    passwrd = request.form['password']
    try:
        mail.login(usrname, passwrd)
        print("LOGIN SUCCESSFULLY")
        return render_template('inbox.html')
    except mail.error as e:
        if 'Invalid credentials' in str(e):
            print("It seems that password was incorrect.")
            return render_template('index.html',message = 'TRY AGAIN')
        else:
            print("Error:",e)
            return render_template('index.html',message = 'TRY AGAIN')
    except:
        print("Authorization Error")
        return render_template('index.html',message = 'TRY AGAIN')

@app.route('/logout',methods=['GET','POST'])
def logout():
    mail.select("inbox")
    mail.close()
    mail.logout()
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
