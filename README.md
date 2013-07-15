local-bitcoin-api
=================

This package contains:
- a slightly extanded wrapper for the Local Bitcoins API based on that provided by Local Bitcoins
- a complete wrapper for the OKPay API including a facility for Bitcoin payments
- a listener to receive payment notifications from OKPay and release escrows on Local Bitcoins

_WARNING_
This is still a work in progress until OKPay have provided a test account for development. Until then this should be considered as incomplete and not be relied upon. Users beware.

To use the package:
1) Set up Local Bitcoins API [here](https://localbitcoins.com/accounts/api/)
2) Set up OKPay API [here](https://www.okpay.com/en/developers/interfaces/setup.html)
3) Set up OKPay instant payment notifications [- instructions](https://www.okpay.com/en/developers/ipn/setup.html)
4) Start `listener.py` on your server

Requirements:
`suds`
`requests`
