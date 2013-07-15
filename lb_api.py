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
import logging
logging.basicConfig(level=logging.INFO)

CLIENT_ID = "add yours here"
CLIENT_SECRET = "add yours here"

class LocalBitcoinsAPI():
    def __init__(self):
        self.access_token = self.get_access_token()

    def get_access_token(self):
        try:
            token_file = open(".localbitcoins_token", "r")
            access_token = token_file.read()
            return access_token
        except IOError, exc:
            self.username = 'botsofbitcoin' #raw_input("Username: ")
            self.password = '4y0hD4aulVbz' #raw_input("Password: ")
    
        token_response = requests.post(
            "https://localbitcoins.com/oauth2/access_token/", 
            data={
                "grant_type": "password",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "username": self.username,
                "password": self.password,
                "scope": "read+write"}).json()
        if "access_token" not in token_response:
            exit(1)
        access_token = token_response["access_token"]
        with open(".localbitcoins_token", "w") as f:
            f.write(access_token)
        return access_token
    
    def get_escrows(self):
        response = requests.get(
                'https://localbitcoins.com/api/escrows/',
                data={'access_token': self.access_token})
        return response.text
    
    def release_escrow(self, escrow):
        release_url = escrow['actions']['release_url']
        response = requests.post(
                 'https://localbitcoins.com/%s' % release_url,
                 data={'access_token': self.access_token})
        return response.text
    
    def get_ads(self):
        response = requests.get(
                'https://localbitcoins.com/api/ads/',
                params={'access_token': self.access_token})
        logging.debug('')
        return response.text
    
    def edit_ad(self, ad_id, visibility, min_amount, max_amount, price_equation):
        response = requests.get(
                'https://localbitcoins.com/api/ad/%s/' % ad_id,
                params={'ad_id': self.access_token,
                        'visibility': visibility,
                        'min_amount': min_amount,
                        'max_amount': max_amount,
                        'price_equation': price_equation})
        return response.text

def test():    
	
    client = LocalBitcoinsAPI()
