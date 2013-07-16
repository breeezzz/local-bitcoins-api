#local-bitcoins-api
==================

This package contains:
- `lb_api.py` modified wrapper for the Local Bitcoins API based on that provided by Local Bitcoins
- `okpay_api.py` a complete wrapper for the OKPay API including a facility for Bitcoin payments
- `listener.py` a listener to receive payment notifications from OKPay and release escrows on Local Bitcoins

#WARNING

This is still a work in progress until testing is completed.

##Tests status

_OKPay API_
- all functions have been tested on live accounts apart from `withdraw_to_ecurrency` and `withdraw_to_BTC` (and given the rates they offer, you're unlikely to want to use them anyway!)

_Local Bitcoins API_
- all functions have been tested on live accounts apart from `release_escrow` as my `botsofbitcoin` seller account seems to be inactive

_Listener_
- tested locally, however requires a server for complete testing

##Setup
To use the package:
- Set up Local Bitcoins API [here](https://localbitcoins.com/accounts/api/)
- Set up OKPay API [here](https://www.okpay.com/en/developers/interfaces/setup.html)
- Set up OKPay instant payment notifications - [instructions](https://www.okpay.com/en/developers/ipn/setup.html)
- Install the package on your server
- Start `listener.py`

##Requirements
`Python 2.7`
`suds`
`requests`
