'''Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

from netmiko import ConnectHandler
import random, string
import smtplib
import os 
from dotenv import load_dotenv
import time

load_dotenv()

def randomize_psk():
    psk_chars = string.ascii_letters + string.digits
    psk = ''.join(random.choice(psk_chars) for i in range(8))
    return psk


def send_email(output,receiver1,receiver2):
    sender = os.environ['smtp_sender']
    receivers = [receiver1,receiver2]

    message = """
    Subject: AireOS WLC PSK UPDATE:
    """ + output
 
    try:
        smtpObj = smtplib.SMTP(os.environ['smtp_server'], 25)
        smtpObj.sendmail(sender, receivers, message)
        print("Successfully sent email")
    except Exception as e:
        print(e)
        print("Error: unable to send email")


def update_psk():
    WLANs = [
    
    ["wlanId","email1","email2"],
    ["wlanId","email1","email2"]

    ]
  
    for wlan in WLANs:
        NEW_PSK = randomize_psk()
        
        cred = {
        'device_type': 'cisco_wlc_ssh',
        'host': os.environ['aireos_host'],
        'username': os.environ['aireos_username'],
        'password': os.environ['aireos_password']
        }
        try: 
            net_connect = ConnectHandler(**cred)
            commands=["config wlan disable "+ wlan[0], "config wlan security wpa akm psk set-key ascii "+ NEW_PSK+ " "+wlan[0], "config wlan enable "+ wlan[0]]
            
            for cmd in commands:
                send_cmmd=net_connect.send_command_timing(cmd)
                
            if ("ERROR" or "Request failed" or "Incorrect input!") in send_cmmd:
                tm = time.strftime('%a, %d %b %Y %H:%M:%S %Z(%z)')
                output="Update at "+ tm +". Cannot update PSK for WLAN "+ wlan[0]+ " Error Message: "+send_cmmd
                print(output)
                send_email(output,wlan[1],wlan[2])

            else:
                tm = time.strftime('%a, %d %b %Y %H:%M:%S %Z(%z)')
                output="Update at "+ tm +". The new PSK for WLAN "+ wlan[0]+" is: "+ NEW_PSK + " and it's sent to: "+wlan[1] +" and "+ wlan[2] 
                print(output)
                send_email(output,wlan[1],wlan[2])
        except Exception as e:
            tm = time.strftime('%a, %d %b %Y %H:%M:%S %Z(%z)')
            output="Update at "+ tm +". Cannot connect to the controller. "
            print(output)
            send_email(output,wlan[1],wlan[2])



   

update_psk()