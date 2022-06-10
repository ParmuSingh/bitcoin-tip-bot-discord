import json
import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType
import logger
# import interactions
import controller

discordClient = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(discordClient, sync_commands=True)

# Inherihit the discord.Client class
class BitcoinTippingBot:
# "botPermissions": 274877908992,
    def __init__(self):
        self.botConfig = json.load(open('./config.json'))
        self.botConfig = self.botConfig[self.botConfig['mode']]

        self.clientId = self.botConfig['clientId']
        self.token = self.botConfig['token']
        self.dbConnectionString = self.botConfig['dbConnectionString']
        self.botPermissions = self.botConfig['botPermissions']
        self.inviteLink = self.botConfig['botInviteLink']

        # self.bot = interactions.Client(token=self.token)
        # self.discordClient = discord.Client(intents=discord.Intents.all())
        # self.slash = SlashCommand(self.discordClient, sync_commands=True)
        global discordClient
        global slash

        self.controller = controller.Controller(self.botConfig)

        logger.log(f'bot initialized. invite link: {self.inviteLink}')
        discordClient.run(self.token)

    @slash.slash(
        name="balance",
        description="Tells you your bitcoin balance"
    )
    async def getBalance(ctx):
        
        if not interaction.guild:
            return # Returns as there is no guild
        guildId = interaction.guild.id
        print(interaction.guild)
        guildName = interaction.guild.name
        userID = interaction.user.id
        userName = interaction.user.name

        self.controller.checkBeforeTransaction(guildId, guildName, userID, userName)

        logger.log(f'\n-> command invoked: getBalance | guildId: {guildId} | guildName: {guildName} | userID: {userID} | userName: {userName}\n')
        userBalance = self.controller.getBalance(userID)

        await ctx.send(content=f"you have {userBalance} satoshis in your wallet")

    @slash.slash(
        name='help',
        description='learn how to use bot'
    )
    async def getHelp(ctx):
        await ctx.send(content="hey hey heyyyyy I'm a bitcoin bot you can use to tip people within this server with some bitcoin.\n\nTo send money use `/send`\nExample: `/send to: @ParmuSingh#5099 amount: 50` This will tip 50 satoshis from your wallet to ParmuSingh's wallet.\n\nTo see your balance:\n`/balance`\n\nTo withdraw your balance:\n`/withdraw invoice: <your-lightning-invoice>`\n\nTo deposit:\n`/deposit amount: 2000`, bot will return a lightning invoice of 2000 satoshis that you can pay to deposit.\n\n\n1 satoshi is 0.00000001 bitcoin")

    @slash.slash(
        name='withdraw',
        description='withdraw your balance',
        options=[
            create_option(
                name="invoice",
                description="paste your lighting payment request",
                option_type=SlashCommandOptionType.STRING,
                required=True
            )
        ]
    )
    async def withdraw(ctx, invoice: str):
        if not interaction.guild:
            return # Returns as there is no guild
        guildId = interaction.guild.id
        print(interaction.guild)
        guildName = interaction.guild.name
        userID = interaction.user.id
        userName = interaction.user.name

        self.controller.checkBeforeTransaction(guildId, guildName, userID, userName)

        logger.log(f'\n-> command invoked: withdraw | guildId: {guildId} | guildName: {guildName} | userID: {userID} | userName: {userName}\n')

        result = controller.payInvoice(guildId, guildName, userID, userName, invoice)

        if result:
            await ctx.send(content="Bitcoin sent!")
        else:
            await ctx.send(content="Transaction failed :( Contact developer for manual withdraw.")

    @slash.slash(
        name='deposit',
        description='deposit bitcoin into this wallet',
        options=[
            create_option(
                name="amount",
                description="satoshis to deposit",
                option_type=SlashCommandOptionType.INTEGER,
                required=True
            )
        ]
    )
    async def deposit(ctx, amount: str):
        if not interaction.guild:
            return # Returns as there is no guild
        guildId = interaction.guild.id
        print(interaction.guild)
        guildName = interaction.guild.name
        userID = interaction.user.id
        userName = interaction.user.name

        self.controller.checkBeforeTransaction(guildId, guildName, userID, userName)

        logger.log(f'\n-> command invoked: deposit | guildId: {guildId} | guildName: {guildName} | userID: {userID} | userName: {userName}\n')

        result = controller.getPaymentRequest(guildId, guildName, userID, userName, amount)
        await ctx.send(content=f'pay this invoice via your lightning wallet to deposit bitcoin:\n\n{result}')


    @slash.slash(
        name="send",
        description="Send bitcoin to another discord user.",
        options=[
            create_option(
                name="to",
                description="user to send bitcoin to",
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name="amount",
                description="Number of satoshis to send",
                option_type=SlashCommandOptionType.INTEGER,
                required=True
            ),
            create_option(
                name="message",
                description="message along with transaction",
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ]
    )
    async def sendBitcoin(ctx, to: str, amount: int, message: str):

        print(to)
        if not interaction.guild:
            return # Returns as there is no guild
        guildId = interaction.guild.id
        print(interaction.guild)
        guildName = interaction.guild.name
        userID = interaction.user.id
        userName = interaction.user.name

        self.controller.checkBeforeTransaction(guildId, guildName, userID, userName)
        logger.log(f'\n-> command invoked: sendBitcoin | guildId: {guildId} | guildName: {guildName} | userID: {userID} | userName: {userName}\n')

        recipient_name = await client.fetch_user(to)
        recipient_name = str(recipient_name).split('#')[0]

        if int(amount) <= 0:
            await ctx.send(content="no.")
            return

        if userID == to:
            await ctx.send(content="why would you tip yourself...?")
            return

        result = controller.sendBitcoin(userID, to, amount)

        if result == "not enough balance":
            await ctx.send(result)
            return

        if result:
            await ctx.send(f"{amount} satoshis sent to {recipient_name}!")
        else:
            await ctx.send(f"problem: {result}")

    async def on_ready(self):
        print('bot is ready to mingle.')

    async def on_message(self, message):
        await ctx.send('moved to / commands')


if __name__ == '__main__':
    bot = BitcoinTippingBot()