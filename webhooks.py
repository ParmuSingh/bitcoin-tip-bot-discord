#######################################################################################################################
# Webhooks are no longer required. balances are kept in lnpay wallet for the user so no need to maintain in database. #
######################################################################################################################

from flask import Flask, request
from pymongo import MongoClient
import json
import helpers

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017")
db = client['btc-discord-bot']

@app.route('/', methods=['POST'])
def webhook():

	request_json = json.loads(request.data.decode('utf-8').replace("'", '"'))

	helpers.log(request)
	helpers.log(request_json)
	created_at = request_json['created_at']
	id = request_json['id']
	event = request_json['event']
	data = request_json['data']['wtx']
	passThru = data['passThru']

	if passThru['app'] != 'discord-bot':
		return

	if data["wtxType"]["name"]=="ln_deposit":
		txData = data["lnTx"]
		txId = txData["id"]
		isSettled = txData["settled"] # 1 for true
		numSatsPaid = txData["num_satoshis"]
		paymentRequest = txData["payment_request"]

		if isSettled == 1:
			server_id = str(passThru['server_id'])
			server_name = str(passThru['server_name'])
			depositor_id = str(passThru['depositor_id'])
			depositor_name = str(passThru['depositor_name'])

			helpers.log(f"\ndeposit confirmed by {depositor_id}: {numSatsPaid} sats")

			check(server_id, server_name, depositor_id, depositor_name)

			user = db['users'].find_one({'user_id': depositor_id})
			user['balance'] += numSatsPaid

			db['users'].update_one({'user_id': depositor_id}, {"$set": user})
	'''
	elif data["wtxType"]["name"]=="ln_withdrawal":
		txData = data["lnTx"]
		txId = txData["id"]
		isSettled = txData["settled"] # 1 for true
		numSatsPaid = txData["num_satoshis"]
		paymentRequest = txData["payment_request"]
		userName = data['passThru']['username']

		if isSettled == 1:
			server_id = str(passThru['server_id'])
			server_name = str(passThru['server_name'])
			withdrawer_id = str(passThru['withdrawer_id'])
			withdrawer_name = str(passThru['withdrawer_name'])

			print(f"\nwithdrawl confirmed by {withdrawer_id}: {numSatsPaid} sats")

			check(server_id, server_name, withdrawer_id, withdrawer_name)

			user = db['users'].find_one({'user_id': withdrawer_id})
			user['balance'] -= numSatsPaid

			db['users'].update_one({'user_id': withdrawer_id}, {"$set": user})
	'''
	return "success"

def check(server_id, server_name, member_id, member_name):
	server_id = str(server_id)
	member_id = str(member_id)

	# check if server is new
	servers_dbcol = db['servers']
	if servers_dbcol.find_one({'server_id': server_id}) == None:
		# insert server to collection
		helpers.log(f"adding new server: {server_id}\n")

		# data to be inserted
		server = {'server_id': server_id, 'name': server_name}

		# adds data to collection
		servers_dbcol.insert_one(server)

	# check if user is new
	users_dbcol = db['users']
	if users_dbcol.find_one({'user_id': member_id}) == None:
		# insert user to collection
		helpers.log(f"adding new user: {member_id}\n")
		# data to be inserted
		user = {'user_id': member_id, 'user_name': member_name, 'balance': 0, 'servers': [server_id]}

		# insert user
		users_dbcol.insert_one(user)


if __name__ == '__main__':
	app.run(host='localhost', port=42069)
