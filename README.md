local-bitcoins-api
==================

This package contains:
- `lb_api.py` a slightly extanded wrapper for the Local Bitcoins API based on that provided by Local Bitcoins
- `okpay_api.py` a complete wrapper for the OKPay API including a facility for Bitcoin payments
- `listener.py` a listener to receive payment notifications from OKPay and release escrows on Local Bitcoins

_WARNING_

This is still a work in progress until testing is completed. Tests on withdrawal to ecurrency are still outstanding.
Until then this should be considered as incomplete and not be relied upon.

_Tests status_

OKPay API
- all functions have been tested on live accounts apart from `withdraw_to_ecurrency` and `withdraw_to_BTC`

Local Bitcoins API
- untested as yet

Listener
- tested locally but not on a remote server

To use the package:

1) Set up Local Bitcoins API [here](https://localbitcoins.com/accounts/api/)

2) Set up OKPay API [here](https://www.okpay.com/en/developers/interfaces/setup.html)

3) Set up OKPay instant payment notifications [- instructions](https://www.okpay.com/en/developers/ipn/setup.html)

4) Start `listener.py` on your server

Requirements:
`suds`
`requests`
