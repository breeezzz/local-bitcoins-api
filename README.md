#local-bitcoins-api
==================

This package contains:
- `lb_api.py` slightly extended wrapper for the Local Bitcoins API based on that provided by Local Bitcoins
- `okpay_api.py` a complete wrapper for the OKPay API including a facility for Bitcoin payments
- `listener.py` a listener to receive payment notifications from OKPay and release escrows on Local Bitcoins

#WARNING

This is still a work in progress until testing is completed.

##Tests status

_OKPay API_
- all functions have been tested on live accounts apart from `withdraw_to_ecurrency` and `withdraw_to_BTC` (and given the rates they offer, you're unlikely to want to use them anyway!)

_Local Bitcoins API_
- all functions have been tested on live accounts

_Listener_
- tested locally, however requires hosting on a remote server to test properly with OKPay's IPN simulator

##Local Bitcoins API

The `lb_api.py` module implements all the existing functionality of the official Local Bitcoins API (see docs for details):
- `get_escrows()`
- `release_escrow(escrow)`
- `get_ads()`
- `edit_ad(ad_id, ad_id, visibility, min_amount, max_amount, price_equation)`

In addition the following functions have been added (unofficial and so may be deprecated without warning):
- `update_prices(price_equation, trade_type)` - Updates all price equations for ads of a given type. Returns an array of responses from each call of the `edit_ad` function
- `delete_ad(ad_id)` - Unofficial API function for deleting an ad by passing the ad_id number
- `delete_ads(start, end)` - Unofficial API function for deleting multiple ads from a start ad_id number (default 0) to an end ad_id number (default 'inf'). Returns an array of responses in the form {'success': [1 0][, 'deleted_id': ad_id, 'error': error]}

##Setup
To use the package:
- Set up Local Bitcoins API [here](https://localbitcoins.com/accounts/api/)
- Set up OKPay API [here](https://www.okpay.com/en/developers/interfaces/setup.html)
- Add credentials to the two API files, or alternatively call them using the necessary credentials

_Optional_ if the OKPay IPN function is required
- Set up OKPay instant payment notifications (if required) - [instructions](https://www.okpay.com/en/developers/ipn/setup.html)
- Install the package on your server
- Start `listener.py`

##Requirements
`Python 2.7`
`suds`
`requests`
