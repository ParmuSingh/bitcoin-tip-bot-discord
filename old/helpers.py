import logging
import lnpay_py
lnpay_api_key = open('./private_data/lnpay_api_key.txt', 'r').read().split('\n')[0]
lnpay_py.initialize(lnpay_api_key)

def log(msg, type='info'):
	print(msg)
	if type=='info':
		logging.info(msg)
	elif type=='error':
		logging.error(msg)
	elif type=='debug':
		logging.debug(msg)
	elif type=='critical':
		logging.critical(msg)

def create_wallet(name):
	wallet_params = {
	    'user_label': name
	}
	new_wallet = lnpay_py.create_wallet(wallet_params)
	log("new wallet created: ")
	print(new_wallet)

	example_value_of_new_wallet = {
		'id': 'wal_', 'created_at': 1611472924, 'updated_at': 1611472924,
		'user_label': 'test-wallet-created-from-lnpay-py', 'balance': 0,
		'statusType': {
			'type': 'wallet',
			'name': 'active',
			'display_name': 'Active'
		},
		'access_keys': {
			'Wallet Admin': ['waka_'],
			'Wallet Invoice': ['waki_'],
			'Wallet Read': ['wakr_']
		}
	}


	return new_wallet
