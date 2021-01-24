from pymongo import MongoClient
import lnpay_py
from lnpay_py.wallet import LNPayWallet
import requests
from requests.auth import HTTPBasicAuth
import json
import helpers

class Currency:
	def __init__(self):
		self.client = MongoClient("mongodb://localhost:27017")
		self.db = self.client['btc-discord-bot']

		self.lnpay_api_key = open('./private_data/lnpay_api_key.txt', 'r').read().split('\n')[0]#[2: len(self.lnpay_api_key)-2]
		self.lnpay_wallet_key_invoice = open('./private_data/lnpay_wallet_key_invoice.txt', 'r').read().split('\n')[0]#[2: len(self.lnpay_wallet_key_invoice)-2]
		self.lnpay_wallet_key_admin = open('./private_data/lnpay_wallet_key_admin.txt', 'r').read().split('\n')[0]
		lnpay_py.initialize(self.lnpay_api_key)

		'''
		self.servers = [] #self.db.list_collection_names()
		for server in self.db['servers'].find():
			self.servers.append(server['server_id'])
		print(f"[mongo] Servers in which bot is available are: {self.servers}")
		'''

	def check(self, server_id, server_name, member_id, member_name):
		server_id = str(server_id)
		member_id = str(member_id)

		# check if server is new
		servers_dbcol = self.db['servers']
		if servers_dbcol.find_one({'server_id': server_id}) == None:
			# insert server to collection
			helpers.log(f"adding new server: {server_id}\n")

			# data to be inserted
			server = {'server_id': server_id, 'name': server_name}

			# adds data to collection
			servers_dbcol.insert_one(server)

		# check if user is new
		users_dbcol = self.db['users']
		if users_dbcol.find_one({'user_id': member_id}) == None:
			# insert user to collection
			helpers.log(f"adding new user: {member_id}\n")
			# data to be inserted
			user = {'user_id': member_id, 'user_name': member_name, 'wallet': helpers.create_wallet("discord-bot-user-"+member_id)}

			# insert user
			users_dbcol.insert_one(user)

		'''
		# check if server is linked to user
		users_dbcol = self.db['users']
		user = users_dbcol.find_one('user_id': member_id)
		if server_id not in user['servers']:
			user['server'].append(server_id)
			self.db['users'].update_one({'user_id': member_id}, {"$set": user})
		'''


	def get_balance(self, member_id):
		member_id = str(member_id)
		wallet = self.db['users'].find_one({'user_id': member_id})['wallet']

		wallet = LNPayWallet(wallet["access_keys"]["Wallet Read"][0])
		info = wallet.get_info()

		info_example = {
			'id': 'wal_gC47E2xGyXclhj',
			'created_at': 1611474292,
			'updated_at': 1611474292,
			'user_label': 'discord-bot-user-331840338748506114',
			'balance': 0,
			'statusType': {
				'type': 'wallet',
				'name': 'active',
				'display_name': 'Active'
			}
		}

		return info['balance']
		"""
		member_id = str(member_id)
		return int(self.db['users'].find_one({'user_id': member_id})['balance'])
		"""

	def update_balance(self, member_id, change):

		member_id = str(member_id)

		user = self.db['users'].find_one({'user_id': member_id})
		user['balance'] += change

		self.db['users'].update_one({'user_id': member_id}, {"$set": user})


	def send_money(self, sender_id, receiver_id, amount):

		'''
		receiver_servers = self.db['users'].find_one({'user_id': receiver_id})['server']
		if sender_server_id not in receiver_servers:
			return "inter sever not allowed"
		'''

		sender_id = str(sender_id)
		receiver_id = str(receiver_id)
		amount = int(amount)
		helpers.log(f"\ninitiating tx: {sender_id} -> {receiver_id} | amount = {amount}\n")

		sender_balance = self.get_balance(sender_id)
		print(f"sender_balance: {sender_balance}. is sender_balance > 0: {sender_balance > 0}")
		if amount > sender_balance and sender_balance <= 0:
			helpers.log(f"not enough balance")
			return "not enough balance"

		# transfer
		sender_wallet = LNPayWallet(self.db['users'].find_one({'user_id': sender_id})['wallet']["access_keys"]["Wallet Admin"][0])
		receiver_wallet_id = self.db['users'].find_one({'user_id': receiver_id})['wallet']["id"]

		transfer_params = {
		    'dest_wallet_id': receiver_wallet_id,
		    'num_satoshis': amount,
		    'memo': 'internal discord bot transfer'
		}
		transfer_result = sender_wallet.internal_transfer(transfer_params)

		"""
		# decrease sender balance
		self.update_balance(sender_id, -amount)

		# increase receiver balance
		self.update_balance(receiver_id, amount)
		"""
		helpers.log(f"money transferred\n")
		return True

	def deposit_get_payreq(self, server_id, server_name, depositor_id, depositor_name, amount):

		depositor_id = str(depositor_id)
		amount = int(amount)

		if amount <= 0:
			return "no"

		depositor_wallet = LNPayWallet(self.db['users'].find_one({'user_id': depositor_id})['wallet']["access_keys"]["Wallet Invoice"][0])
		invoice_params = {
			'num_satoshis': amount,
			'memo': 'depositing sats in discord',
			'passThru': {'server_id': server_id, 'server_name': server_name, 'depositor_id': depositor_id, 'depositor_name': depositor_name, 'app': 'discord-bot'}
		}
		invoice = depositor_wallet.create_invoice(invoice_params)['payment_request']
		return invoice

	def withdraw_pay_invoice(self, server_id, server_name, withdrawer_id, withdrawer_name, payreq):

		withdrawer_id = str(withdrawer_id)
		"""
		withdrawer_balance = self.get_balance(withdrawer_id)

		amount = self.get_amount_from_payreq(payreq)

		if amount == None:
			return "Cannot pay any amount invoice. You have to mention amount in invoice."
		amount = int(amount)

		# check if user has the amount
		if amount > withdrawer_balance or withdrawer_balance <= 0:
			helpers.log(f"not enough balance")
			return "Not enough balance"
		"""
		# transfer
		withdrawer_wallet = LNPayWallet(self.db['users'].find_one({'user_id': withdrawer_id})['wallet']["access_keys"]["Wallet Admin"][0])
		invoice_params = {
		    'payment_request': payreq,
			'passThru': {'app': 'discord-bot'}
		}
		print(invoice_params)
		pay_result = withdrawer_wallet.pay_invoice(invoice_params)
		helpers.log(pay_result)

		settled = False

		if 'lnTx' in pay_result.keys():
			if pay_result['lnTx']['settled'] == 1:
				settled = True
				helpers.log(f"\nwithdrawl by {withdrawer_id}: {amount} sats")
				self.update_balance(withdrawer_id, -amount)
				return "sats withdrawn"

		return "payment unsuccessful."

	def get_amount_from_payreq(self, payreq):
		payreq_decoded = requests.get(f'https://lnpay.co/v1/node/default/payments/decodeinvoice?payment_request={payreq}', auth=HTTPBasicAuth(self.lnpay_api_key, ''))
		payreq_decoded = json.loads(payreq_decoded.text)

		amount = payreq_decoded['num_satoshis']

		return amount
