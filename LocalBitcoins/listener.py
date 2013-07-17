'''
Created on 15 Jul 2013

@author: jamie@botsofbitcoins.com
'''
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
 
import cgi
from requests import Request, Session
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import csv
from lb_api import LocalBitcoinsAPI
from okpay_api import OkPayAPI

import logging 
logging.basicConfig(level=logging.DEBUG)

class OKPay_handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            ctype, _pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                self.postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                self.postvars = {}
            
            response = handle_POST(self.postvars)    
    
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Content-type: text/html<BR><BR>");
            self.wfile.write("<HTML>%s<BR></HTML>" % response);
        except :
            pass

def handle_POST(postvars):
    response = check_validity(postvars)
    if  response == 'VERIFIED':
        if is_ok_to_release(postvars):
            client = LocalBitcoinsAPI()
            response = client.release_escrow(postvars['ok_txn_id'])
            logging.info(response['message'])
    else:
        log_response('%s, %s\n' % (response, postvars))
    return response
    
def is_ok_to_release(postvars):
    if (is_status_complete(postvars['ok_txn_status']) and
        is_transaction_unique(postvars['ok_txn_id']) and
        is_receiver_email_correct(postvars['ok_receiver_email']) and
        is_transaction_details_ok(postvars)):
        return True
    
def is_status_complete(status):
    return status == 'completed'

def is_transaction_unique(transaction_id):
    with open('existing_transactions.csv', 'rb') as f:
        existing_transactions = csv.reader(f)
    print existing_transactions
    return transaction_id not in existing_transactions    

def is_receiver_email_correct(email):
    valid_receiver_emails = ['sales@botsofbitcoin.com'] 
    return email in valid_receiver_emails    

def is_transaction_details_ok(postvars):
    # Check price, currency and amount from the escrow release API
    lb_client = LocalBitcoinsAPI()
    escrows = lb_client.get_escrows()
    lb_transaction = {escrow for escrow in escrows
                        if escrow['data']['reference_code'] == postvars['transaction_id']}
    ok_client = OkPayAPI()
    ok_transaction = ok_client.get_transaction('transaction_id')
    # TODO: Compare the two sets of transactions to ensure price and quantity match
    return False

def log_response(response):
    with open('okpay_log.txt', 'ab') as log:
        log.write(response)

def check_validity(data):
    # Make a post request  to OKPay
    verify_url = 'http://okpay.com/ipn-verify.html'
    s = Session()
    body = data + {'ok_verify': 'true'}
    prepped = Request('POST', verify_url, data=body).prepare()
    r = s.send(prepped)
    return r.text
    

def main():
    try:
        server = HTTPServer(('', 8080), OKPay_handler)
        print 'Started HTTP server...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '<Ctrl-C> received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

