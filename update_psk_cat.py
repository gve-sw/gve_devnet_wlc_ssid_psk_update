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

from ncclient import manager
import smtplib
import random, string
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
    Subject: CAT9800 WLC PSK UPDATE:
    """ + output

    try:
        smtpObj = smtplib.SMTP(os.environ['smtp_server'], 25)
        smtpObj.sendmail(sender, receivers, message)
        print("Successfully sent email")
    except Exception as e:
        print(e)
        print("Error: unable to send email")


def update_psk():

  SSIDs = [
    
    ["ssid name","email1","email2"],
    ["ssid name","email1","email2"]
  ]
  
  for ssid in SSIDs:
    NEW_PSK = randomize_psk()
    UPDATE_PSK = """
        <config>
          <wlan-cfg-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-wlan-cfg">
            <wlan-cfg-entries>
              <wlan-cfg-entry>
                <profile-name>%s</profile-name>
                <psk xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="replace">%s</psk>
              </wlan-cfg-entry>
            </wlan-cfg-entries>
          </wlan-cfg-data>
        </config>
        """ % (ssid[0], NEW_PSK)
    

    device = manager.connect(
        host=os.environ['cat_host'],
        port=830,
        username=os.environ['cat_username'],
        password=os.environ['cat_password'],
        hostkey_verify=False,
        device_params={'name':'iosxe'}
    )

    
    try:
      device.edit_config(target='running', config=UPDATE_PSK, default_operation="merge")
      tm = time.strftime('%a, %d %b %Y %H:%M:%S %Z(%z)')
      output="Update at "+ tm +". The new PSK for SSID '"+ ssid[0]+"' is: "+ NEW_PSK + " and it's sent to: "+ssid[1] +" and "+ ssid[2] 
      print(output)
      send_email(output,ssid[1],ssid[2])
    except Exception as e:
      tm = time.strftime('%a, %d %b %Y %H:%M:%S %Z(%z)')
      output="Update at "+ tm +". Cannot update PSK for SSID '"+ ssid[0]+ "'. This SSID might not be configured on the controller."
      print(output)
      send_email(output,ssid[1],ssid[2])



update_psk()
  

