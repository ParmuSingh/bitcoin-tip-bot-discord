#discord.__version__ = 1.0.0a
client_id_file 		= open("./private_data/client_id.txt", "r")
token_file 			= open("./private_data/token.txt", "r")
server_id_file 		= open("./private_data/my_server_id.txt", "r")

client_id 		= int(client_id_file.read())
server_id 		= int(server_id_file.read())

token 			= token_file.read()
permissions 	= 68608

# https://discordapp.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions={PERMISSIONSINT}
add_to_server_url = f"https://discordapp.com/oauth2/authorize?client_id={client_id}&scope=bot&permissions={permissions}"

import discord
import currency_mongo
import helpers

helpers.log(add_to_server_url)

# initiates client
client = discord.Client()
mongo_currency = currency_mongo.Currency()

@client.event 	# decorator/wrapper
async def on_ready():
	pass
	#global mongo_currency

	#mongo_currency = currency.Currency()

@client.event
async def on_message(message):
	#print(f"{message} : #{message.channel} : {message.author} : {message.content}")
	server_id = message.guild.id
	server_name = message.guild.name
	member_id = message.author.id
	member_name = message.author.name

	if "!btctip" not in message.content:
		return

	helpers.log(f"\n-> message: {message.content} |||| server_id: {server_id} | server_name: {server_name} | member_id: {member_id} | member_name: {member_name}\n")

	mongo_currency.check(server_id, server_name, member_id, member_name)

	if "!btctip xxstop" in message.content.lower():
		helpers.log("byeeee", 'critical')
		await client.close()
		return
	elif "!btctip show my balance" in message.content.lower() and message.author.name!="bitcoin-tip-bot":
		#member_id = message.author.id

		bal = mongo_currency.get_balance(member_id)
		await message.channel.send(f"you have {bal}sats")	
		return
	elif "!btctip help" in message.content.lower() and message.author.name!="bitcoin-tip-bot" :
		await message.channel.send("hey hey heyyyyy I'm a bitcoin bot you can use to tip people within this server with some bitcoin.\n\nTo send money:`!btctip <mention-username-of-receiver> <amt-in-satoshi>`\nExample: `!btctip @ParmuSingh#5099 50` This will send 50 satoshis from your wallet to ParmuSingh's wallet.\n\nTo see your balances:\n`!btctip show my balance`\n\n\nps: 1 satoshi is 0.00000001 bitcoin 		|		 I may not be online all the time.\n\nbeep beep boop boop - created by a smart ass.")
		return

	elif "!btctip withdraw" in message.content.lower() and message.author.name!="bitcoin-tip-bot":
		#try:

		withdrawer_id = member_id
		withdrawer_name = member_name

		words = message.content.lower().split(' ')
		for i in range(len(words)):
			if words[i] == "!btctip" and words[i+1] == "withdraw":
				pay_req = words[i+2]
				break
				# not returning if invalid after invoke command cuz it raises exception and program goes on

		#result = mongo_currency.get_amount_from_payreq(pay_req)
		result = mongo_currency.withdraw_pay_invoice(server_id, server_name, withdrawer_id, withdrawer_name, pay_req)

		await message.channel.send(result)

		#except ValueError as e:
		#	print(e)
		#	await message.channel.send("ay check again")
		#	return

	elif "!btctip deposit" in message.content.lower() and  message.author.name!="bitcoin-tip-bot":
		try:

			depositor_id = member_id
			depositor_name = member_name

			words = message.content.lower().split(' ')
			for i in range(len(words)):
				if words[i] == "!btctip" and words[i+1] == "deposit":
					amount = words[i+2]
					break
					# not returning if invalid after invoke command cuz it raises exception and program goes on

			invoice = mongo_currency.deposit_get_payreq(server_id, server_name, depositor_id, depositor_name, amount)
			await message.channel.send(invoice)

		except ValueError as e:
			helpers.log(e, 'error')
			await message.channel.send("ay check again")
			return

	elif "!btctip" in message.content.lower() and message.author.name!="bitcoin-tip-bot":
		try:
			words = message.content.lower().split(' ')

			for i in range(len(words)):
				if words[i] == "!btctip":
					recipient = words[i+1]
					amount = words[i+2]
					if amount == '': # sometimes mentioning user adds another empty char which could fuck things up so I'm removing any empty chars registered as words
						amount = words[i+3]
					break
					# not returning if invalid after invoke command cuz it raises exception and program goes on

			sender_id = member_id
			sender_name = member_name
			recipient_id = int(recipient.split('!')[1][:len(recipient.split('!')[1]) - 1])
			recipient_name = await client.fetch_user(recipient_id)
			recipient_name = str(recipient_name).split('#')[0]

			mongo_currency.check(server_id, server_name, recipient_id, recipient_name)

			helpers.log(f"sender_name = {sender_name} | sender_id = {sender_id} | recipient_name = {recipient_name} | recipient_id = {recipient_id}")

			if int(amount) <= 0:
				await message.channel.send("niiggaa... no.")
				return

			if sender_id == recipient_id:
				await message.channel.send("why would you tip yourself...?")
				return

			result = mongo_currency.send_money(sender_id, recipient_id, amount)

			if result == "not enough balance":
				await message.channel.send(result)
				return

			if result:
				await message.channel.send(f"hey heyy heyyy\n{amount} satoshis sent to {recipient_name}")
			else:
				await message.channel.send(f"problem: {result}")

		except ValueError as e:
			helpers.log(e)
			await message.channel.send("ay check again")

client.run(token)
