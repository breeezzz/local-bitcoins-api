'''
Created on 10 Jul 2013

@author: jamie@botsofbitcoin.com
'''
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

""" 
Copyright (c) 2013, LocalBitcoins Oy
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the LocalBitcoins Oy nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL LOCALBITCOINS OY BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import requests
import json

import logging
logging.basicConfig(level=logging.WARNING)
hdr = {'Referer' : 'https://localbitcoins.com/'}

class LocalBitcoinsAPI():
    def __init__(self, client_id=None, client_secret=None, username=None, password=None):
        ''' Set up your API Access Information
            https://www.okpay.com/en/developers/interfaces/setup.html '''
        if client_id == None:
            self.client_id = "your details here"
        else:
            self.client_id = client_id
        if client_secret == None:
            self.client_secret = "your details here"
        else:
            self.client_secret = client_secret
        if username == None:
            self.username = "your details here"
        else:
            self.username = username
        if password == None:
            self.password = "your details here"
        else:
            self.password = password
            
        self.agent = requests.session()
        self.access_token = self.get_access_token()
        self.agent_login()
        
    def get_access_token(self):
        try:
            token_file = open(".localbitcoins_token%s" % self.username, "r")
            access_token = token_file.read()
            return access_token
        except IOError:
            pass
    
        token_response = requests.post(
            "https://localbitcoins.com/oauth2/access_token/", 
            data={
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password,
                "scope": "read+write"}).json()
        if "access_token" not in token_response:
            exit(1)
        access_token = token_response["access_token"]
        with open(".localbitcoins_token%s" % self.username, "w") as f:
            f.write(access_token)
        return access_token
    
    def get_escrows(self):
        r = requests.post(
                'https://localbitcoins.com/api/escrows/',
                data={'access_token': self.access_token})
        return json.loads(r.text)
        
    def release_escrow(self, escrow):
        release_url = escrow['actions']['release_url']
        r = requests.post(release_url,
                data={'access_token': self.access_token})
        return json.loads(r.text)
    
    def get_ads(self):
        r = requests.get(
                'https://localbitcoins.com/api/ads/',
                params={'access_token': self.access_token})
        return json.loads(r.text)
    
    def edit_ad(self, ad_id, visibility, min_amount, max_amount, price_equation):
        r = requests.get(
                'https://localbitcoins.com/api/ad/%s/' % ad_id,
                params={'visibility': visibility,
                        'min_amount': min_amount,
                        'max_amount': max_amount,
                        'price_equation': price_equation})
        return r.text
    
    def update_prices(self, price_equation, trade_type):
        ''' Pass in a price equation and type of ad you want it to apply to
            and all your ads of that type will be updated. Returns a list of
            responses to the edits '''
        ads = self.get_ads()['data']['ad_list']
        response = []
        for ad in ads:
            data = ad['data']
            if data['trade_type'] == trade_type:
                response += [self.edit_ad(data['ad_id'], data['visibility'],
                             data['min_amount'], data['max_amount'],
                             data['price_equation'])]
                
        return response              
        
    def agent_login(self):
        ''' Added function to log in allowing access to additional functions
            not yet covered by the official API. These functions will be deprecated once
            the official API covers them. '''
        self.agent.get('https://localbitcoins.com/', verify=False)
        csrftoken = self.agent.cookies['csrftoken']
        self.agent.post('https://localbitcoins.com/accounts/login/',
                        data={'username': self.username,
                            'password': self.password,
                            'csrfmiddlewaretoken' : csrftoken},
                            headers=hdr, verify=False)

    def delete_ads(self, start=0, end='inf'):
        ''' Unofficial API function '''
        ads = self.get_ads()['data']['ad_list']
        delete_ids = [ad['data']['ad_id'] for ad in ads
                      if ad['data']['ad_id'] >= start
                      and ad['data']['ad_id'] <= end]
        response = []
        for ad_id in delete_ids:
            response += [self.delete_ad(ad_id)]
        return response
        
    def delete_ad(self, ad_id):
        ''' Unofficial API function '''
        try:
            r = self.agent.get(
                     'https://localbitcoins.com/ads_delete/%s' % ad_id,
                     headers=hdr)
            if "alert alert-success" in r.text:
                response = {'success': 1, 'deleted_id': ad_id}
            else:
                response = {'success': 0}
        except Exception, e:
            response = {'success': 0, 'error': e}

        return response
        
def test():
    with open('C:\Users\Jamie\lba_config.txt') as f:
        creds = {}
        for line in f:
            creds[line.split(',')[0]] = line.split(',')[1].rstrip('\n')

    client1 = LocalBitcoinsAPI(creds['lb_client_id1'], creds['lb_client_secret1'],
                               creds['lb_username1'], creds['lb_password1'])
    client2 = LocalBitcoinsAPI(creds['lb_client_id2'], creds['lb_client_secret2'],
                               creds['lb_username2'], creds['lb_password2'])

    print "Checking get_ads for test account 2",
    print client2.get_ads()    
    print "Checking escrows for test account 2",
    print client2.get_escrows()
    print "Checking escrows for test account 1",
    escrows = client1.get_escrows()
    print escrows
    print "Checking for 'globalcoins' on test account 2 escrows",
    for escrow in escrows['data']['escrow_list']:
        if 'globalcoins' in escrow['data']['buyer_username']:
            print 'OK to release'
    for escrow in escrows['data']['escrow_list']:
        if 'globalcoins' in escrow['data']['buyer_username']:
            print "Releasing escrow",
            print client1.release_escrow(escrow)
    print
    print "Testing complete"

test()