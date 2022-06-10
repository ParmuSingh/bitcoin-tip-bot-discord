from pymongo import MongoClient
import lnpay_py
from lnpay_py.wallet import LNPayWallet
import requests
from requests.auth import HTTPBasicAuth
import json
import logger

class Controller:
    def __init__(self, appConfig):
        self.mongoClient = MongoClient(appConfig['dbConnectionString'])
        self.db = self.mongoClient[appConfig['dbName']]

        self.lnpay_api_key = appConfig['lnpay-api-key']
        self.lnpay_wallet_key_admin = appConfig['lnpay-admin-wallet-key']
        self.lnpay_wallet_key_invoice = appConfig['lnpay-invoice-wallet-key']
        lnpay_py.initialize(self.lnpay_api_key)

    def create_wallet(self, name):
        wallet_params = {
            'user_label': name
        }
        newWallet = lnpay_py.create_wallet(wallet_params)
        logger.log(f'new wallet created: {newWallet}')

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

        return newWallet

    def checkBeforeTransaction(self, server_id, server_name, member_id, member_name):
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
            user = {'user_id': member_id, 'user_name': member_name, 'wallet': self.create_wallet("discord-bot-user-"+member_id)}

            # insert user
            users_dbcol.insert_one(user)


    def getBalance(self, member_id):
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

    def sendBitcoin(self, sender_id, receiver_id, amount):

        sender_id = str(sender_id)
        receiver_id = str(receiver_id)
        amount = int(amount)
        logger.log(f"\ninitiating tx: {sender_id} -> {receiver_id} | amount = {amount}\n")

        # get sender balance
        sender_balance = self.getBalance(sender_id)
        logger.log(f"sender_balance: {sender_balance}. is sender_balance > 0: {sender_balance > 0}")
        # if balance is lower than amount then reject transaction
        if amount > sender_balance or sender_balance <= 0:
            logger.log(f"not enough balance")
            return "not enough balance"

        # get wallets
        sender_wallet = LNPayWallet(self.db['users'].find_one({'user_id': sender_id})['wallet']["access_keys"]["Wallet Admin"][0])
        receiver_wallet_id = self.db['users'].find_one({'user_id': receiver_id})['wallet']["id"]

        # set transfer paramers
        transfer_params = {
            'dest_wallet_id': receiver_wallet_id,
            'num_satoshis': amount,
            'memo': 'internal discord bot transfer'
        }
        transfer_result = sender_wallet.internal_transfer(transfer_params)

        logger.log(f"money transferred\n")
        return True

    def getPaymentRequest(self, server_id, server_name, depositor_id, depositor_name, amount):

        depositor_id = str(depositor_id)
        amount = int(amount)

        # if amount is negative then reject request (lnpay bug)
        if amount <= 0:
            return "no"

        logger.log(f'pay_req requested | amount: {amount}')

        # get depositor's wallet
        depositor_wallet = LNPayWallet(self.db['users'].find_one({'user_id': depositor_id})['wallet']["access_keys"]["Wallet Invoice"][0])
        invoice_params = {
            'num_satoshis': amount,
            'memo': 'depositing sats in discord',
            'passThru': {'server_id': server_id, 'server_name': server_name, 'depositor_id': depositor_id, 'depositor_name': depositor_name, 'app': 'discord-bot'}
        }
        invoice = depositor_wallet.create_invoice(invoice_params)['payment_request']
        return invoice

    def payInvoice(self, server_id, server_name, withdrawer_id, withdrawer_name, payreq):

        withdrawer_id = str(withdrawer_id)
        
        # get withdrawer's wallet
        withdrawer_wallet = LNPayWallet(self.db['users'].find_one({'user_id': withdrawer_id})['wallet']["access_keys"]["Wallet Admin"][0])
        invoice_params = {
            'payment_request': payreq,
            'passThru': {'app': 'discord-bot'}
        }
        logger.log(f'request to pay invoice | invoice_params: {invoice_params}')
        pay_result = withdrawer_wallet.pay_invoice(invoice_params)
        logger.log(pay_result)

        settled = False

        if 'lnTx' in pay_result.keys():
            if pay_result['lnTx']['settled'] == 1:
                settled = True
                helpers.log(f"\nwithdrawl by {withdrawer_id}: {amount} sats")
                self.update_balance(withdrawer_id, -amount)
                return True

        return False

    def getAmountFromPayReq(self, payreq):
        payreq_decoded = requests.get(f'https://lnpay.co/v1/node/default/payments/decodeinvoice?payment_request={payreq}', auth=HTTPBasicAuth(self.lnpay_api_key, ''))
        payreq_decoded = json.loads(payreq_decoded.text)

        amount = payreq_decoded['num_satoshis']

        return amount
