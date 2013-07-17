'''
Created on 7 Jun 2013

@author: Jamie
'''

import urllib2
import math
import re
import itertools
import argparse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

markets = {'UK': {'url': 'gb/united%20kingdom/', 'curr': 'GBP'},
           'USA': {'url': 'us/united%20states/', 'curr': 'USD'},
           'GERMANY': {'url': 'de/germany/', 'curr': 'EUR'},
           'ITALY': {'url': 'it/italy/', 'curr': 'EUR'},
           'SPAIN': {'url': 'es/spain/', 'curr': 'EUR'},
           'AUSTRALIA': {'url': 'au/australia/', 'curr': 'AUD'},
           'ARGENTINA': {'url': 'ar/argentina/', 'curr': 'ARS'},
           'NETHERLANDS': {'url': 'nl/netherlands/', 'curr': 'EUR'},           
           'BRAZIL': {'url': 'br/brazil/', 'curr': 'BRL'},           
           'FRANCE': {'url': 'fr/france/', 'curr': 'EUR'},
           'GBP': {'url': 'gbp/', 'curr': 'GBP'},
           'USD': {'url': 'usd/', 'curr': 'USD'},
           'EUR': {'url': 'eur/', 'curr': 'EUR'},
           }

methods = {'NATIONAL_BANK_TRANSFER': 'national-bank-transfer/'}
method = ''

buy_url = 'https://localbitcoins.com/buy-bitcoins-online/'
sell_url = 'https://localbitcoins.com/sell-bitcoins-online/'

def get_ads_dict(soup, buy_sell):
    prices = get_prices(soup)
    users = get_users(soup)
    amounts = get_amounts(soup)
    amounts = [a/p for a,p in zip(amounts, prices)] # To give amount in BTC
    currency = get_currency(soup)
    methods = get_methods(soup)
    lists = set(zip(prices, users, amounts, currency))
    if buy_sell == 'buy':
        sorted_ads = sorted(lists)
    elif buy_sell == 'sell':
        sorted_ads = sorted(lists)[::-1]
    prices = [item[0] for item in sorted_ads]
    users = [item[1] for item in sorted_ads]
    amounts = [item[2] for item in sorted_ads]
    currency = [item[3] for item in sorted_ads]
    depth = get_depth(amounts)
    ads_dict = {'users': users, 'prices': prices, 'amounts': amounts, 
                'depth': depth, 'currency': currency, 'methods': methods}
    return ads_dict

def get_prices(soup):
    ''' Returns a list of prices '''
    prices = soup.find_all('td', attrs={'class':"column-price"})
    prices = [float(re.findall("\d+.\d+", price.get_text())[0]) for price in prices]
    return prices

def get_currency(soup):
    ''' Returns a list of currencies '''
    prices = soup.find_all('td', attrs={'class':"column-price"})
    currencies = [price.get_text().split()[-1] for price in prices]
    return currencies

def get_methods(soup):
    ''' Returns a list of payment methods '''
    methods = soup.find_all('tr', attrs={'class':"clickable"})
    methods = [method.get_text().split('\n')[-7].strip() for method in methods]
    return methods

def get_users(soup):
    ''' Returns a list of users '''
    users = soup.find_all('td', attrs={'class':"column-user"})
    users = [user.get_text().split()[0] for user in users]
    return users

def get_amounts(soup):
    ''' Returns a list of amounts '''
    raw_amounts = soup.find_all('td', attrs={'class':"column-limit"})
    amounts = []
    for amount in raw_amounts:
        try:
            amounts += [float(amount.get_text().split()[2])]
        except:
            amounts += [0.0]
    return amounts

def get_depth(amounts):
    ''' Generates the cumulative amount for each point on the curve '''
    cum_amounts = []
    cum_amount = 0
    for amount in amounts:
        cum_amount += amount
        cum_amounts += [cum_amount]
    return cum_amounts 

def get_buy_curve(market):
    response = urllib2.urlopen(buy_url + market['url'] + method)
    soup = BeautifulSoup(response)
    buy_ads = get_ads_dict(soup, 'buy')
    buy_prices = [i for i,j in zip(buy_ads['prices'], buy_ads['currency']) if j == market['curr']]
    buy_depth = [i for i,j in zip(buy_ads['depth'], buy_ads['currency']) if j == market['curr']]
    buy_prices = double_list(buy_prices)[1:]
    buy_depth = double_list(buy_depth)[:-1]
    return buy_prices[:-2], buy_depth[:-2]
    
def get_sell_curve(market):
    response = urllib2.urlopen(sell_url + market['url'] + method)
    soup = BeautifulSoup(response)
    sell_ads = get_ads_dict(soup, 'sell')
    sell_prices = [i for i,j in zip(sell_ads['prices'], sell_ads['currency']) if j == market['curr']][::-1]
    sell_depth = [i for i,j in zip(sell_ads['depth'], sell_ads['currency']) if j == market['curr']][::-1]
    sell_prices = double_list(sell_prices)[1:]
    sell_depth = double_list(sell_depth)[:-1]
    return sell_prices, sell_depth

def plot_chart(ax, buy, sell):
    ax.plot(buy[0], buy[1], color='r')
    ax.plot(sell[0], sell[1], color='g')

def double_list(list_in):
    iters = [iter(list_in), iter(list_in)]
    return list(it.next() for it in itertools.cycle(iters))

def get_bid(country):
    market = markets[country]
    response = urllib2.urlopen(buy_url + market['url'] + method)
    soup = BeautifulSoup(response)
    buy_ads = get_ads_dict(soup, 'buy')
    bid = buy_ads['prices'][0]
    return bid

def get_ask(country):
    market = markets[country]
    response = urllib2.urlopen(sell_url + market['url'] + method)
    soup = BeautifulSoup(response)
    sell_ads = get_ads_dict(soup, 'sell')
    ask = sell_ads['prices'][0]
    return ask

def make_charts(*args):
    if len(args[0].countries) == 0:
        selection = ['UK','USA','SPAIN','FRANCE','GERMANY','BRAZIL']
    else:
        selection = args[0].countries
    fig = plt.figure()
    dim = math.ceil(len(selection)**0.5)
    for x, s in enumerate(selection):
        market = markets[s]
        # method = methods['NATIONAL_BANK_TRANSFER']
        ax = fig.add_subplot(dim, dim, x+1)
        ax.set_xlabel(market['curr'])
        ax.set_ylabel('BTC')
        ax.set_title('Local Bitcoins online: %s' % s)
        buy_curve = get_buy_curve(market)
        sell_curve = get_sell_curve(market)
        plot_chart(ax, buy_curve, sell_curve)
    plt.tight_layout()
    plt.show()
    

def main():
    parser = argparse.ArgumentParser(description='Display charts of the Local Bitcoin market depth.')
    parser.add_argument('countries', type=str, nargs='*',
                        help='optionally specify any number of country names')
    args = parser.parse_args()
    make_charts(args)

if __name__ == '__main__':
    main()

