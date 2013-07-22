'''
Created on 15 Jul 2013

@author: jamie@botsofbitcoins.com
'''
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import urlparse
import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import csv
from lb_api import LocalBitcoinsAPI
from okpay_api import OkPayAPI

import logging 
logging.basicConfig(level=logging.DEBUG)

class OKPay_handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self.send_response(200)
            self.end_headers()
            ctype, _pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                self.postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=True)
            else:
                self.postvars = {}
            handle_POST(self.postvars)
            print "Back in handler."
        except :
            pass

def handle_POST(postvars):
    logging.info("Received message")
    creds = get_creds()
    ok_to_release, release_url = is_ok_to_release(postvars)
    if ok_to_release:
        logging.debug("Getting LB client")
        client = LocalBitcoinsAPI(creds['lb_client_id'], creds['lb_client_secret'],
                                  creds['lb_username'], creds['lb_password'])
        logging.debug("Got LB client")
        
        ad_no = release_url.split('/')[-2]
        ad_url = ('https://localbitcoins.com/escrow_seller/' + ad_no)
        client.send_message(ad_url, 'Automated response: Thanks for your order - your coins will now be released.')

        response = client.release_escrow(release_url)
        logging.info("Released transaction")
        logging.info("Transaction reference %s" % postvars['ok_txn_comment'][0])
        logging.info(response['data']['message'])
    else:
        print ad_url
        client.send_message(ad_url, 'Automated response: There was a problem with your payment. Please email sales@botsofbitcoin.com for human intervention.')

def is_ok_to_release(postvars):
    logging.debug("Checking if ok to release")
    if (is_status_complete(postvars['ok_txn_status'][0]) and
        is_transaction_unique(postvars['ok_txn_comment'][0]) and
        is_receiver_email_correct(postvars['ok_receiver_email'][0])):
        
        ok_to_release, release_url = is_transaction_details_ok(postvars)

    return ok_to_release, release_url
    
def is_status_complete(status):
    logging.debug("Checking if status is complete")
    return status == 'completed'

def is_transaction_unique(transaction_id):
    logging.debug("Checking if transaction is unique")
    with open('existing_transactions.csv', 'rb') as f:
        existing_transactions = csv.reader(f)
        transactions = [line for line in existing_transactions]
        
    response = transaction_id not in transactions
    with open('existing_transactions.csv', 'ab') as f:
        f.write('%s\n' % transaction_id)
    
    return response

def is_receiver_email_correct(email):
    logging.debug("Checking receiver email address is correct")
    valid_receiver_emails = ['sales@botsofbitcoin.com'] 
    
    return email in valid_receiver_emails    

def is_transaction_details_ok(postvars):
    logging.debug("Checking transaction details match")
    creds = get_creds()    
    # Check currency and amount from the escrow release API
    lb_client = LocalBitcoinsAPI(creds['lb_client_id'], creds['lb_client_secret'],
                                 creds['lb_username'], creds['lb_password'])
    escrows = lb_client.get_escrows()
    for escrow in escrows['data']['escrow_list']:
        if escrow['data']['reference_code'] == postvars['ok_txn_comment'][0]:
            lb_transaction = escrow
    logging.debug("Got LB transaction")
    if (lb_transaction['data']['currency'] == postvars['ok_txn_currency'][0] and
        lb_transaction['data']['amount'] == postvars['ok_txn_amount'][0]):
        return True, lb_transaction['actions']['release_url']
    else:
        return False, ''
    
def get_creds():
    logging.debug("Getting stored credentials")
    with open('creds.txt', 'rb') as f:
        creds = {}
        for line in f:
            creds[line.split(',')[0]] = line.split(',')[1].rstrip()
    return creds

def set_creds(lb_username, lb_password, lb_client_id, lb_client_secret,
              okpay_wallet, okpay_email, okpay_key, okpay_client):
    logging.debug("Storing credentials")
    with open('creds.txt', 'wb') as f:
        f.writeline('lb_username,%s' % lb_username)
        f.writeline('lb_password,%s' % lb_password)
        f.writeline('lb_client_id,%s' % lb_client_id)
        f.writeline('lb_client_secret,%s' % lb_client_secret)
        f.writeline('okpay_wallet,%s' % okpay_wallet)
        f.writeline('okpay_email,%s' % okpay_email)
        f.writeline('okpay_key,%s' % okpay_key)
        f.writeline('okpay_client,%s' % okpay_client)
    f.close()
    
    
def main():
    # Check for credentials
    try:
        creds = open('creds.txt', 'rb')
        creds.close()
    except IOError, e:
        print e
        print ("Set up your credentials file in creds.txt or by calling \
                set_creds(lb_username, lb_password, lb_client_id, lb_client_secret, \
                okpay_wallet, okpay_email, okpay_key, okpay_client)")
        return(0)       
    # Start the server
    try:
        server = HTTPServer(('', 8080), OKPay_handler)
        print 'Started HTTP server...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '<Ctrl-C> received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

