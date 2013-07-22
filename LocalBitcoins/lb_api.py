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
logging.basicConfig(level=logging.DEBUG)

try:
    from bs4 import BeautifulSoup
except:
    logging.warning("BeautifulSoup is required for editing ads using the unofficial HTML API")

hdr = {'Referer' : 'https://localbitcoins.com/'
      }
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
        print "Got creds"
        print "Getting API session"
        self.access_token = self.get_access_token()
        print "Logged on to API session"
        self.agent = requests.session()
        self.agent_login()
        self.csrftoken = self.agent.cookies['csrftoken']
        print "Logged on to HTML session"
        

    def get_access_token(self):
        try:
            logging.debug("Getting stored access token")
            token_file = open("localbitcoins_token%s.txt" % self.username, "rb")
            access_token = token_file.read()
            logging.debug("Got stored access token")
            return access_token

        except IOError:
            logging.debug("Getting new access token")
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

        logging.debug("Posted to oauth2 url")
        
        print "Response", token_response

        if "access_token" not in token_response:
            logging.fatal("No key in response")
            exit(1)

        access_token = token_response["access_token"]
        logging.debug("Got new access token")
        with open("localbitcoins_token%s.txt" % self.username, "wb") as f:
            f.write(access_token)
        logging.debug("Saved access token.")
        
        return access_token
    
    def get_escrows(self):
        logging.debug("Getting escrows")
        r = requests.post(
                'https://localbitcoins.com/api/escrows/',
                data={'access_token': self.access_token})
        return json.loads(r.text)
        
    def release_escrow(self, release_url=None, escrow=None):
        logging.debug('Releasing escrow')
        if not release_url == None:
            pass
        elif not escrow == None:
            release_url = escrow['actions']['release_url']
            
        r = requests.post(release_url,
                data={'access_token': self.access_token})
        response = json.loads(r.text)
        
        return response
    
    def get_ads(self):
        logging.debug('Getting ads')
        r = requests.get(
                'https://localbitcoins.com/api/ads/',
                params={'access_token': self.access_token})
        return json.loads(r.text)
    
    def edit_ad(self, ad_id, visibility, min_amount, max_amount, price_equation):
        logging.debug('Editing ad')
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
        logging.debug('Upating prices')
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

    def send_message(self, ad_url, message):
        ''' Unofficial API function '''
        logging.debug('Sending message')
        try:
            post_data = {'msg': message}
            post_data['csrfmiddlewaretoken'] = self.csrftoken
            self.agent.post(ad_url, data=post_data, headers=hdr)
            response = {'success': 1}
        except Exception, e:
            response = {'success': 0, 'error': e}
            pass
        return response
        
    def delete_ad(self, ad_id):
        ''' Unofficial API function '''
        logging.debug('Deleting ad')
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
    
    def edit_ad_html(self, ad_no, edits_dict=None):
        ''' Unofficial API function '''
        logging.debug('Editing ad')
        ad_url = 'https://localbitcoins.com/ads_edit/%s' % ad_no
        ad = self.agent.get(ad_url, headers=hdr).text
        soup = BeautifulSoup(ad)
        post_data = _get_post_data(soup)
        post_data = dict(post_data.items() + edits_dict.items())

        try:
            post_data['csrfmiddlewaretoken'] = self.csrftoken
            r = self.agent.post(ad_url, data=post_data, headers=hdr)
            if "alert alert-success" in r.text:
                print "Success!"
                response = {'success': 1, 'edited_ad': ad_url}
            elif "alert alert-error" in r.text:
                response = {'success': 0, 'error': 'Failed to upload ad'}
        except Exception, e:
            response = {'success': 0, 'error': e}
            
        return response

def _get_post_data(soup):
    inputs = soup.find_all(_required_inputs)
    inputs_dict = {tag.get('name'): tag.get('value') for tag in inputs}
    controls = soup.find_all('select')
    controls_dict = _add_controls(controls)
    text = soup.find_all('textarea')
    text_dict = _add_text(text)
    
    post_data = inputs_dict
    post_data = dict(post_data.items() + controls_dict.items())
    post_data = dict(post_data.items() + text_dict.items())
    
    return post_data

def _required_inputs(tag):
    discard_tags = ['csrfmiddlewaretoken', 'action_url', 'header', 'msg']
    if tag.get('type') == 'hidden' and tag.get('name') in discard_tags:
        return
    if tag.get('type') == 'radio' and tag.get('checked') != 'checked':
        return
    elif tag.get('type') == 'checkbox' and tag.get('checked') != 'checked':
        return
    else:
        return tag.name == 'input'

def _add_controls(controls):
    controls_dict = {}
    for c in controls:
        if c['name'] == 'ad-online_provider':
            controls_dict[c['name']] = c.find_all('option')[0]['value']
        else:
            controls_dict[c['name']] = c.find_all('option',
                                        attrs={'selected': "selected"})[0]['value']
    return controls_dict

def _add_text(text):
    text_dict = {}
    for t in text:
        text_dict[t['name']] = (t.contents if len(t.contents) > 0 else "")
    return text_dict
