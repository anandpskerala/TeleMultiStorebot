import traceback
# Enable logging
import time, datetime, os, re, sys, sqlite3, json, io, requests, pyrogram
from pyrogram import Client, Filters
from utils.dbmanager import *
import logging
import subprocess

from uuid import uuid4 
from utils.dbmanager import savedb, loadDB, fetchNews, checkUserLastNews, checkTodayFirstNewsID, fileid, sfileid

from datetime import datetime

from requests import get
import sqlite3 as lite

from datetime import date, datetime

ip = get('https://api.ipify.org').text
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING) 


from urllib.request import urlopen
from utils.handlers import *
import datetime 
from clint.textui import progress
import fnmatch 
from bs4 import BeautifulSoup

loadDB()
from subprocess import Popen, PIPE

from datetime import datetime, timezone
import os,json,datetime,subprocess,time
download_path = "{}/Downloads/".format(os.getcwd())
def append_to_downloads(data):
    # append the argument to Downloads/downloads.json file
     
    downloads_json_file = json.loads(open(download_path+"/downloads.json","r").read())
    downloads_json_file.append(data)
    downloads_json_file = json.dumps(downloads_json_file,sort_keys=True, indent=4)
    open(download_path + "/downloads.json","w").write(downloads_json_file)

def index():
    size = subprocess.check_output(['du','-sh', download_path]).split()[0].decode('utf-8')
    return size
@Client.on_message(Filters.command("dls", prefix="!") & Filters.private)
def api_download(c, m):
    link = " ".join(m.command[1:])
    # starting the download
    m.reply("hello there")
    wget_cmd = "wget {} -o wget.log".format(link)
    with requests.get(link) as r:
      fname = ''
      if "Content-Disposition" in r.headers.keys():
        fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
      else:
        fname = link.split("/")[-1]
        fname = fname.strip('\n').replace('\"','')
        required_file_name = os.path.basename(fname) 
    folder_name = required_file_name 
    isd = download_path+"/"+folder_name
    
    now = datetime.datetime.now()
    current_date_time = str(now).split(" ")[0] + " " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
    try:
        location = './files/'
#as suggested by @SilentGhost the `location` and `url` should be separate argument
        args = ['wget', '-O', folder_name, '-l', '1', '-P', location, link]
        output = subprocess.check_output(
            args, stderr=subprocess.STDOUT)
         
        #append_to_downloads({'time':current_date_time,'link':link,'folder':folder_name})
        m.reply(output.decode("UTF-8") + "\n")
    except subprocess.CalledProcessError as e:
        print("")
        m.reply(e.output.decode("UTF-8"))
    return None
@Client.on_message(Filters.command("link", prefix="!") & Filters.private)
def sendServerStartedMessage(c, m):
        link = " ".join(m.command[1:])
    # starting the download
        m.reply("hello there")
        ngrok_data = json.loads(requests.get("http://127.0.0.1:4040/api/tunnels",headers={"Content-Type":"application/json"}).text)
        public_url = ngrok_data["tunnels"][1]["public_url"]

        try:   
            m.reply(str(public_url))
        except Exception as e:
            m.reply(str(e))

options={}
base_headers = {   
        'User-Agent':  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.5 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.5',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
headers = dict(base_headers, **options) 



from datetime import datetime, timezone



@Client.on_message(Filters.command("dl", prefix="!") & Filters.private)
def dl(client, message, **current):
    try:
      url = " ".join(message.command[1:])
      logger.info(message.from_user)
      if len(url) < 3: 
        message.reply("That is not a valid command")
        return True
      else:
        sent = client.send_message(message.chat.id, "Processing your request...", reply_to_message_id=message.message_id).message_id  
        
        time.sleep(2)
        ctype = is_downloadable(url) 
        if ctype:
          with requests.get(url) as r:
           
            fname = ''
            if "Content-Disposition" in r.headers.keys():
                fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
            else:
                fname = url.split("/")[-1]
                fname = fname.strip('\n').replace('\"','').replace(" ", "_")
                required_file_name = os.path.basename(fname) 
           
                client.edit_message_text(message.chat.id, sent, "**Checking:** `{}`\n\n if it exist on my server..".format(required_file_name))
                time.sleep(2)
                lr = checkUserLastNews(message.chat.id)
                tr = checkTodayFirstNewsID()
                tnews = "No files so let me download it for you"
                ttfiles = "Could not send requested file"
                opp = "oh mine its gone"
        
                if(tr == 0):
                  tnews = "No news for today."
                elif(lr < tr):
                  lr = tr
                if(tr != 0):
                  tnews = sfileid(required_file_name)
                if tnews:
                  client.send_document(message.chat.id, tnews, caption="Oh! i had this alread so it was faster")
                  with open("file.json") as json_file: 
                    data = json.load(json_file) 
                    json_data = json.loads(data)
                    for p in range(6):
                      batch = data[p]["Date"]
                    message.reply(batch)
   
       
                  client.delete_messages(message.chat.id, sent)
                  return True
                
                else:
                  client.edit_message_text(message.chat.id, sent, "Downloading your file")
                  r = requests.get(url, stream=True, allow_redirects=True, headers=headers)
                  if r.status_code < 400:
                      with open(required_file_name, 'wb') as file:
                        total_length = r.headers.get('content-length')
                        if total_length is None:  # no content length header
                            file.write(r.content)
                        else:
                          dl = 0
                          total_length = int(total_length)
                          for chunk in progress.bar(r.iter_content(chunk_size=8192*1024), expected_size=(total_length / 1024) + 1):
                            if chunk:
                                dl += len(chunk)
                                done = int(100 * dl / total_length)
                                file.write(chunk)
                                file.flush()
                      time.sleep(5)
                      client.edit_message_text(message.chat.id, sent, "Done")
                      chat_id = message.chat.id
                      file = client.send_document(message.chat.id, required_file_name, progress = prog, progress_args = (sent, message.chat.id, required_file_name), reply_to_message_id=sent)  
                      os.remove(required_file_name)
                      
                      file_size1 = file.document.file_size
                      uploader1 = message.from_user.id
                      file_name1 = file.document.file_name
                      file_id1 = file.document.file_id
                      fetchNews(file_name1, file_size1, file_id1)
                      LastReadNewsID = checkUserLastNews(chat_id)
                      TodayFirstNewsID = checkTodayFirstNewsID()
                      news = "No news"
                      tfiles = None
                      if(TodayFirstNewsID == 0):
                        news = "No news for today."
                      elif(LastReadNewsID < TodayFirstNewsID):
                        LastReadNewsID = TodayFirstNewsID
                      if(TodayFirstNewsID != 0):
                        news = getNews(LastReadNewsID, chat_id)
                      message.reply(news) 
                  else:
                    client.edit_message_text(message.chat.id, sent, "Requested url returned: `{}` status code. Kindly try again".format(r.status_coded))
        else:
          client.edit_message_text(message.chat.id, sent, "`Your link doesn't look like a downloadable link...... Kindly try again`")
        
    except RequestException as e:
      message.reply(sent, "hello `{}`".format(e))
    except pyrogram.Error as e:
      message.reply(sent, "nof`{}`".format(e))