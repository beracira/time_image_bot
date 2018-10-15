#! /usr/bin/python3

import datetime
import time
import os
import pprint
import telepot
import pytz
from tzwhere import tzwhere
import sqlite3
from telepot.loop import MessageLoop

# print = pprint.PrettyPrinter().pprint

HINT = '''
Send location to set your timezone
可以向我發送地點設置時區喔
'''

SET_SUCCESS = '''Timezone has been set to {0}
時區已經設置為 {0}
'''

DEFAULT_TIMEZONE_STR = 'America/Toronto'

def doit(chat_id, timezone):
    temp = " 已經\n "
    
    temp += datetime.datetime.now(timezone).strftime("%H:%M")
    
    temp += "\n 了!!\n"
    
    print (temp)
    
    with open('temp.txt', 'w') as fout:
        fout.write(temp)
        
    os.system('soffice --convert-to jpg temp.txt')
    os.system('convert temp.jpg -crop 125x300+50+0 temp.jpg')
    os.system('convert temp.jpg -resize 200% temp.jpg')
    os.system('convert temp.jpg -crop 125x300+40+50 temp.jpg')
    os.system('montage temp.jpg bot.jpg -tile 1x2 -geometry +0+0 temp.jpg')
    os.system('montage left.jpg temp.jpg -tile 2x1 -geometry +0+0 temp.jpg')

    fout = open('temp.jpg', 'rb')
    print ('sending photo...')
    bot.sendPhoto(chat_id, fout)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    # print ('Content type: %s' % content_type)
    print (content_type, chat_type, chat_id)

    if chat_type == 'private':
        conn = sqlite3.connect('timezone.db')
        c = conn.cursor()
        
        timezone_str = ''
        if content_type == 'location':
            where = tzwhere.tzwhere()
            loc_data = msg['location']
            print (loc_data['longitude'], loc_data['latitude'])
            timezone_str = where.tzNameAt(loc_data['latitude'], loc_data['longitude'])
            
            c.execute('''select * from timezone where chatid=?''', (chat_id,))
            if c.fetchone() is None:
                c.execute('''insert into timezone values(?, ?)''', (chat_id, timezone_str))
            else:
                c.execute('''update timezone set timezone=? where chatid=?''', (timezone_str, chat_id))
                
            bot.sendMessage(chat_id, SET_SUCCESS.format(timezone_str, timezone_str))
            
        if timezone_str == '':
            c.execute('''select * from timezone where chatid=?''', (chat_id,))
            result = c.fetchone()
            if result is not None:
                timezone_str = result[1]
                print (timezone_str)
            else:
                timezone_str = DEFAULT_TIMEZONE_STR
                bot.sendMessage(chat_id, HINT)
            
        
        conn.commit()
        conn.close()

        timezone = pytz.timezone(timezone_str)
        doit(chat_id, timezone)
    elif content_type == 'text' and '@time_image_bot' in msg['text']:
        doit(chat_id, DEFAULT_TIMEZONE_STR)
    
api_key = ''
with open('key_file.txt', 'r') as fin:
    api_key = fin.readlines()[0].strip()
    print (api_key)

bot = telepot.Bot(api_key)

MessageLoop(bot, handle).run_as_thread()
print ('I am listening ...')

while 1:
    time.sleep(10)
