'''
Created on 10 Jul 2013

@author: jamie@botsofbitcoins.com
'''
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from suds.client import Client
from suds import WebFault
import datetime
from hashlib import sha256

import logging
logging.basicConfig(level=logging.INFO)

class OkPayAPI():
    def __init__(self, api_password=None, wallet_id=None):
        ''' Set up your API Access Information
            https://www.okpay.com/en/developers/interfaces/setup.html '''
        if api_password == None:
            self.api_password = "your details here"
        else:
            self.api_password = api_password
        if wallet_id == None:
            self.wallet_id = "your details here"
        else:
            self.wallet_id = wallet_id

        #Generate Security Token
        concatenated = api_password + datetime.datetime.utcnow().strftime(":%Y%m%d:%H")
        self.security_token = sha256(concatenated).hexdigest()    
        #Create proxy client
        self.client = Client('https://api.okpay.com/OkPayAPI?singleWsdl')

    def get_date_time(self):
        ''' Get the server time in GMT.
            Params: None
            Returns: String value - Date (YYYY-MM-DD HH:mm:SS)
                    2010-12-31 10:33:44 '''
        return self.client.service.Get_Date_Time()
    
    def get_balance(self, currency=None):
        ''' Get the balance of all currency wallets or of a single currency.
            Params: currency is a three-letter code from the list at
                        https://www.okpay.com/en/developers/currency-codes.html
                        if no currency is passed then all wallets balances are
                        returned.
            Returns: dictionary in the form {'balance': {'CUR': '0.0', ...}} '''
        try:
            if not currency == None:
                response = self.client.service.Wallet_Get_Currency_Balance(
                            self.wallet_id, self.security_token,
                            currency)
                balance = {response.Currency: response.Amount}
            else:
                response = self.client.service.Wallet_Get_Balance(
                        self.wallet_id, self.security_token)
                balance = {item.Currency: item.Amount for item in response.Balance}
            response = {'success': 1, 'balance': balance}
        except WebFault, e:
            response = {'success': 0, 'error': e}
            
        return response
            
    def send_money(self, destination, currency, amount, comment='', receiver_pays_fees=True):
        ''' Send money to another OKPay account (or an email address, in which case
                the recipient is asked to create an account)
                see https://www.okpay.com/developers/interfaces/functions/send-money.html
            Params: destination is an OKPay wallet ID or email address
                currency is a three-letter code from the list at https://www.okpay.com/en/developers/currency-codes.html
                amount is the amount to send
                - the amount must have two decimal places.
                - the decimal separator must be a period (".")
                - you must not use any thousands separator
                comment is a text string
                receiver_pays_fees is a boolean
            Returns: dict with success code and either the operation ID or the error code '''
        try:
            amount = '%.2f' % amount # this must be given to two decimal places
            response = self.client.service.Send_Money(
                        self.wallet_id, self.security_token,
                        destination, currency, amount,
                        comment, receiver_pays_fees)
            response = {'success': 1, 'operation_id': self._parse_transaction(response)}
        except WebFault, e:
            response = {'success': 0, 'error': e}
            
        return response
           
    def check_account(self, destination):
        ''' Check if a client account exists before sending funds
            Params: destination is an OKPay wallet ID or email address
            Returns: dict with success code and the account ID (0 if it doesn't exist) or the error code '''        
        try:
            response = self.client.service.Account_Check(
                        self.wallet_id, self.security_token,
                        destination)
            response = {'success': 1, 'client_account_id': response}
        except WebFault, e:
            response = {'success': 0, 'error': e}
                        
        return response
    
    def _parse_transaction(self, t):
        ''' Parser to convert a transaction object to a dict for use by the get_transaction,
        withdraw_to_ecurrency and get_history functions '''
        transaction = {'id': t.ID, 'date': t.Date, 'operation': t.OperationName,
                       'status': t.Status, 'net': t.Net, 'amount': t.Amount,
                       'fees': t.Fees, 'currency': t.Currency, 'comment': t.Comment,
                       'sender': self._parse_user(t.Sender), 'receiver': self._parse_user(t.Receiver),
                       'invoice': t.Invoice}
        return transaction
    
    def _parse_user(self, u):
        user = {'account_id': u.AccountID, 'country_iso': u.Country_ISO, 'email': u.Email,
                'name': u.Name, 'verification_status': u.VerificationStatus, 'wallet_id': u.WalletID}
        return user
        
    def get_transaction(self, transaction, invoice=''):
        ''' Get information on a specific transaction ID
                see https://www.okpay.com/en/developers/interfaces/functions/transaction.html
            Params: transaction is a transaction ID
                invoice is a customer invoice number (not required)
            Returns: dict with success code and a large dictionary of details
                see TxnInfo https://www.okpay.com/en/developers/interfaces/functions/data-structures.html '''        
        try:
            response = self.client.service.Transaction_Get(
                        self.wallet_id, self.security_token,
                        transaction,
                        invoice)
            transaction_keys = ['ID', 'Date', 'OperationName', 'Status', 'Net', 'Amount',
                                'Fees', 'Currency', 'Comment', 'Sender', 'Receiver', 'Invoice']
            transaction = {}
            for line in str(response).split('\n'):
                for key in transaction_keys:
                    if key in line:
                        transaction[key] = line.split()[-1]
            response = {'success': 1, 'transaction': transaction}
        except WebFault, e:
            response = {'success': 0, 'error': e}
                        
        return response

    def get_history(self, start=None, end=None, page_size=50, page_num=1, transactions={}):
        if start == None:
            start = '2000-01-01 00:00:00' # Should be before the earliest OKPay transaction
        if end == None:
            end = self.get_date_time()
        try:
            response = self.client.service.Transaction_History(
                        self.wallet_id, self.security_token,
                        start, end,
                        page_size, page_num)
            
            for transaction in response.Transactions:
                for item in transaction[1]:
                    transactions[item.ID] = self._parse_transaction(item)
                    
            # Recursively continue to add to transactions if required
            if response.PageCount > response.PageNumber:
                self.get_history(start, end, page_size, page_num+1, transactions)
            response = {'success': 1, 'transactions': transactions}
            
        except WebFault, e:
            response = {'success': 0, 'error': e}
        except TypeError, e:
            response = {'success': 1, 'transactions': {}}
        except Exception, e:
            response = {'success': 0, 'error': e}    
                        
        return response
            
    def withdraw_to_ecurrency(self,
                            payment_method, pay_system_account,
                            amount, currency,
                            fees_from_amount=True, invoice=''):
        try:
            amount = '%.2f' % amount # this must be given to two decimal places
            response = self.client.service.Withdraw_To_Ecurrency(
                        self.wallet_id, self.security_token,
                        payment_method, pay_system_account,
                        amount, currency,
                        fees_from_amount, invoice)
            response = {'success': 1, 'transaction': self._parse_transaction(response)}
        except WebFault, e:
            response = {'success': 0, 'error': e}
        except Exception, e:
            response = {'success': 0, 'error': e}
        
        return response
    
    def withdraw_to_BTC(self, bitcoin_wallet,
                        amount, currency='BTC',
                        fees_from_amount=True, invoice=''):
        ''' Helper function to simplify withdrawals to Bitcoin
            Defaults to the withdrawal amount being stated in Bitcoins
            The minimum withdrawal amount is 0.25 BTC (on 16/7/2013)'''
        amount = '%.2f' % amount # this must be given to two decimal places
        response = self.withdraw_to_ecurrency('BTC', bitcoin_wallet,
                            amount, currency,
                            fees_from_amount=True, invoice='')
        return response

    def get_withdrawal_fee(self, payment_method, amount, currency, fees_from_amount=True):
        
        try:
            response = self.client.service.Withdraw_To_Ecurrency_Calculate(
                        self.wallet_id, self.security_token,
                        payment_method, amount, currency, fees_from_amount)
            response = {'success': 1, 'fees': response.Fee}
        except WebFault, e:
            response = {'success': 0, 'error': e}
        except Exception, e:
            response = {'success': 0, 'error': e}
        
        return response

def test():
    with open('C:\Users\Jamie\lba_config.txt') as f:
        creds = {}
        for line in f:
            creds[line.split(',')[0]] = line.split(',')[1].rstrip('\n')

    client1 = OkPayAPI(creds['okpay_key1'], creds['okpay_wallet1'])
    print client1.client
    client2 = OkPayAPI(creds['okpay_key2'], creds['okpay_wallet2'])
    
    print "Testing begins at",
    print client2.get_date_time()
    
    print "Checking balance",
    print client2.get_balance()
    print "Checking individual balance - USD",
    print client2.get_balance('USD')

    print "Checking for test account 1 using email address",
    print client2.check_account('sales@botsofbitcoin.com')
    print "Checking for test account 2 using email address",
    print client2.check_account('jamie@botsofbitcoin.com')

    print "Checking for test account 1 using wallet ID",
    print client2.check_account(creds['okpay_wallet1'])
    
    print "Getting history for test account 1",
    print client1.get_history()

    print "Getting history for test account 2",
    print client2.get_history()
    
    print "Getting transaction details for transaction 1998491L",
    print client2.get_transaction(1998491L)
    
    print "Sending money from test account 2 to test account 1",
    print client2.send_money('sales@botsofbitcoin.com', 'USD', 0.01, 'comment goes here', True)
    
    print "Checking withdrawal fee to BTC from test account 2",
    print client2.get_withdrawal_fee('BTC', 0.10, 'USD', True)
    
    print "Withdrawing to BTC from test account 2",
    print client2.withdraw_to_BTC('13aHXq1uvusPrAAtmrrggkckBFC5WLFgXo', 0.25, 'BTC')
    
    print "Tests complete at",
    print client2.get_date_time()

test()