#discord.__version__ = 1.0.0a
client_id_file 	= open("./private_data/client_id.txt", "r")
token_file 		= open("./private_data/token.txt", "r")
server_id_file 	= open("./private_data/my_server_id.txt", "r")
client_id 		= int(client_id_file.read())
server_id 		= int(server_id_file.read())
token 			= token_file.read()
permissions 	= 68608

# https://discordapp.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions={PERMISSIONSINT}
add_to_server_url = f"https://discordapp.com/oauth2/authorize?client_id={client_id}&scope=bot&permissions={permissions}"
print(add_to_server_url)

import discord
import currency

# initiates client
client = discord.Client()
currency_lastbench = None

@client.event 	# decorator/wrapper
async def on_ready(currency=currency):

	global currency_lastbench

	server = client.get_guild(id=server_id) # Eishhtimulation
	
	currency_lastbench = currency.Currency(server)
	# currency_lastbench.show_balance()


@client.event
async def on_message(message):
	print(f"#{message.channel} : {message.author} : {message.author.name} : {message.content}")

	if "!btctip xxstop" in message.content.lower():
		print("byeeee")
		currency_lastbench.close_file()
		await client.close()
		return
	if "!btctip show all balances" in message.content.lower() and message.author.name!="bitcoin-tip-bot":
		await message.channel.send(currency_lastbench.show_balance())
		return
	if "!btctip help" in message.content.lower() and message.author.name!="bitcoin-tip-bot" :
		await message.channel.send("hey hey heyyyyy I'm a bitcoin bot you can use to tip people within this server with some bitcoin. My creator has envisoned me to work with bitcoin's lightning network so you can do microtransaction instantly.\n\nRight now you can only send to people within this server but my creator will soon add the feature to withdraw your bitcoin which you can receive on any bitcoin wallet.\n\nTo send money:\n\n!btctip <username-of-receiver> <amt-in-satoshi>\n 	Example: !btctip arpan 50\n 			This will send 50 satoshis from your wallet to arpan's wallet.\n\nTo see all balances:\n\n!btctip show all balances\n\n\nps: 1 satoshi is 0.00000001 bitcoin 		|		 I may not be online all the time.\n\nbeep beep boop boop - created by a smart ass.")
		return
	if "!btctip" in message.content.lower() and message.author.name!="bitcoin-tip-bot":
		try:
			words = message.content.lower().split(' ')

			sender = message.author.name
			for i in range(len(words)):
				if words[i] == "!btctip":
					recipient = words[i+1]
					amount = words[i+2]
					# not returning if invalid after invoke command cuz it raises exception and program goes on
			if sender.lower() == recipient.lower():
				await message.channel.send("why do would you tip yourself...?")
				return
			# sender_tag = message.author.tag
			# recipient = words[1]
			# amount = words[2]
			success, err = currency_lastbench.do_transaction(sender, recipient, amount)
			if success:
				await message.channel.send(f"hey heyy heyyy\n{amount} satoshis sent to {recipient} from {sender}\n\n1 satoshi = 0.00000001 bitcoin")
			else:
				await message.channel.send(f"uh there's some problem: {err}")

		except ValueError as e:
			print(e)
			await message.channel.send("ay check again")

client.run(token)

