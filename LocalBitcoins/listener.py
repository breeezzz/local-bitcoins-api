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
            print "Received POST"

            ctype, _pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/x-www-form-urlencoded':
                print "Parsing variables"
                length = int(self.headers.getheader('content-length'))
                self.postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=True)
            else:
                self.postvars = {}
            response = handle_POST(self.postvars)
        except :
            pass

def handle_POST(postvars):
    print "Received message"
    creds = get_creds()
    
    if is_ok_to_release(postvars):
        print "Getting LB client"
        client = LocalBitcoinsAPI(creds['lb_client_id'], creds['lb_client_secret'],
                                  creds['lb_username'], creds['lb_password'])
        print "Got LB client"
        response = client.release_escrow(postvars['ok_txn_id'][0])
        print "LB txn id =", response
        logging.info(response['message'])
    
    return response
    
def is_ok_to_release(postvars):
    print "Checking if ok to release"
    if (is_status_complete(postvars['ok_txn_status'][0]) and
        is_transaction_unique(postvars['ok_txn_id'][0]) and
        is_receiver_email_correct(postvars['ok_receiver_email'][0]) and
        is_transaction_details_ok(postvars)):
        print "OK"
        return True
    return False
    
def is_status_complete(status):
    print "Checking if status is complete"
    return status == 'completed'

def is_transaction_unique(transaction_id):
    print "Checking if transaction is unique"    
    with open('existing_transactions.csv', 'rb') as f:
        existing_transactions = csv.reader(f)
        transactions = [line for line in existing_transactions]
        
    response = transaction_id not in transactions
    print "Is unique =", response
    with open('existing_transactions.csv', 'ab') as f:
        f.write('%s\n' % transaction_id)

    return response

def is_receiver_email_correct(email):
    print "Checking receiver email address is correct"
    valid_receiver_emails = ['sales@botsofbitcoin.com'] 
    
    return email in valid_receiver_emails    

def is_transaction_details_ok(postvars):
    print "Checking if transaction details match (code not completed here: return True for test)"
    return True
    creds = get_creds()
    
    # Check price, currency and amount from the escrow release API
    lb_client = LocalBitcoinsAPI(creds['lb_client_id'], creds['lb_client_secret'])
    escrows = lb_client.get_escrows()
    lb_transaction = {escrow for escrow in escrows
                        if escrow['data']['reference_code'] == postvars['transaction_id']}
    
    ok_client = OkPayAPI(creds['okpay_client'], creds['okpay_key'])
    ok_transaction = ok_client.get_transaction('transaction_id')
    # TODO: Compare the two sets of transactions to ensure price and quantity match
    return False

def log_response(response):
    with open('okpay_log.txt', 'ab') as log:
        log.write('%s\n\n' % response)

    
def get_creds():
    with open('creds.txt') as f:
        creds = {}
        for line in f:
            creds[line.split(',')[0]] = line.split(',')[1].rstrip('\n')
    return creds


def main():
    # Check for credentials
    try:
        creds = open('creds.txt', 'rb')
        creds.close()
    except IOError, e:
        print e
        print "Set up your credentials file, creds.txt"
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

