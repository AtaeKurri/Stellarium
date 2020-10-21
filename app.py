# Stellarium
# Fait pour tourner en version 1.4.1 du module discord.

import discord, asyncio, datetime, json, random, time, os, requests, aiohttp
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle
from discord import *
from discord.ext.commands import has_permissions
from termcolor import colored

from cogs.config import get_lang, get_prefix, get_default_prefix, debug, get_bot_version, get_bot_owner

client = commands.Bot(command_prefix=get_prefix)
client.remove_command('help')

# # # Variables # # #

LienInvitation = "https://discordapp.com/oauth2/authorize?client_id=746348869574459472&scope=bot&permissions=2012740695"
#status = cycle(['by Atae Kurri#6302 | ;help', f'{versionBot} | ;help', ';help for help'])
cmds = ["guildes", "infos", "roll", "setLang", "moderation", "prefixGestion", "danbooru", "SCP", "meteo", "broadcast", "template"]
os.system('color')
os.system('cls')

# # # Defs et classes # # #

#@tasks.loop(seconds=20)
#async def change_status():
#    await client.change_presence(activity=discord.Game(next(status)))

# # # console # # #

@client.command()
async def console(ctx):
    if ctx.message.author.id != get_bot_owner():
        raise commands.CheckFailure
    if not debug():
        raise commands.CheckFailure
    else:
        print(colored("Que voulez-vous faire ? (help pour la liste des commandes)", "yellow"))
        cmd = input("> ")
        if cmd.upper() == "HELP":
            print(colored("say, help, listservs, exit", "yellow"))
            await console(ctx)
        elif cmd.upper() == "SAY":
            print(colored("Quel serveur voulez-vous ?", "yellow"))
            for servs in list(client.guilds):
                print(f"{servs.name} -> {servs.id}")
            serv = int(input("> "))
            
            print(colored("Quel channel voulez-vous ?", "yellow"))
            get_serv = client.get_guild(serv)
            for chans in get_serv.text_channels:
                print(f"{chans.name} -> {chans.id}")
            chan = int(input("> "))

            get_chan = client.get_channel(chan)
            await console_send_msg(get_chan, ctx)

        elif cmd.upper() == "LISTSERVS":
            for servs in list(client.guilds):
                print(f"{servs.name} -> {servs.id}")
            await console(ctx)
        elif cmd.upper() == "EXIT":
            os.system('cls')
            on_ready_print()
            
async def console_send_msg(chan, ctx):
    print(colored("Que voulez-vous envoyer ? (S = stop)", "yellow"))
    msg = input("> ")
    if msg.upper() == "S":
        await console(ctx)
    else:
        await chan.send(msg)
        await console_send_msg(chan, ctx)


# # # Events # # #

def on_ready_print():
    print(colored('------', "red"))
    print(colored('Bot lancé sous', "green"))
    print(colored(client.user.name, "yellow"))
    print(colored(client.user.id, "green"))
    print(f'module discord en version {colored(discord.__version__, "green")}')
    print('Version actuelle du bot : ' + colored(f"{get_bot_version()}", "green"))
    print(f'Dans {len(list(client.guilds))} serveurs.')
    print(colored('------', "red"))
    print(f"Commandes : {', '.join(cmds)}")
    print(f'Command Prefix : {colored(";", "yellow")}')
    print(colored('------', "red"))
    print(' ')

@client.event
async def on_ready():
    os.system('cls')
    on_ready_print()

    await client.change_presence(activity=discord.Game(f'{get_bot_version()} | ;help'))
    #change_status.start()

@client.event
async def on_guild_join(guild):
    conf = json.load(open("json/serverconfig.json", 'r'))
    Iguild = str(guild.id)
    conf[Iguild] = {}
    conf[Iguild]["lang"] = "en"
    conf[Iguild]["creator"] = guild.owner.id
    conf[Iguild]["prefix"] = get_default_prefix()

    with open('json/serverconfig.json', 'w') as sConfSave:
        json.dump(conf, sConfSave, indent=2)

@client.event
async def on_guild_remove(guild):
    conf = json.load(open("json/serverconfig.json", 'r'))
    conf.pop(str(guild.id))

    with open('json/serverconfig.json', 'w') as sConfSave:
        json.dump(conf, sConfSave, indent=2)

@client.event #Easter eggs
async def on_message(message):
    if "True Administrator" in message.content:
        await message.channel.send("Nani ?! Miko ?! O-O'")
    if "Cute Devil" in message.content:
        await message.channel.send("Raep time incomming!")
    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    """ Handling errors """

    if isinstance(error, commands.CheckFailure): # Si une permission d'une has_permissions n'est pas remplie
        await ctx.send(get_lang(str(ctx.guild.id), "CheckFailure"))
    if isinstance(error, commands.BadArgument): # Une commande a un mauvais argument.
        await ctx.send(get_lang(str(ctx.guild.id), "BadArgument"))
    if isinstance(error, commands.CommandNotFound): # Une commande n'est pas trouvée.
        await ctx.send(f'{get_lang(str(ctx.guild.id), "CommandNotFound")} : `{ctx.message.content}`')
    if isinstance(error, RuntimeError):
        pass
    print(error)

# # # Commandes # # #

@client.command(aliases=["aide", "Aide", "Help"])
async def help(ctx, page=""):
    hpage = page or "1"
    guild = str(ctx.guild.id)
    embed = discord.Embed(colour=ctx.author.top_role.colour.value)
    embed.set_footer(text=f"help page {hpage}/2")
    c = json.load(open("json/serverconfig.json", 'r'))
    p = c[str(ctx.guild.id)]["prefix"]

    if hpage == "1":
        embed.add_field(name=f'{p}setPrefix <prefix>', value="Change prefix", inline=True)
        embed.add_field(name=f"{p}userinfo", value=f'{get_lang(guild, "help_01")}', inline=True)
        embed.add_field(name=f"{p}roll <valeur>d<valeur>", value=f'{get_lang(guild, "help_02")}', inline=True)
        embed.add_field(name=f"{p}setLang <prefix>", value=f'{get_lang(guild, "help_03")}', inline=True)
        embed.add_field(name=f"{p}serverinfo", value=get_lang(guild, "help_04"), inline=True)
        embed.add_field(name=f"{p}ban/{p}kick <user>", value=get_lang(guild, "help_05"), inline=True)
        embed.add_field(name=f'{p}CreateGuild "name" [-d "Description"] [-p]', value=get_lang(guild, "help_06"), inline=True)
        embed.add_field(name=f"{p}GuildInfo <name>", value=get_lang(guild, "help_07"), inline=True)
        embed.add_field(name=f'{p}EditGuildDesc "name" "description"', value=get_lang(guild, "help_08"), inline=True)
        embed.add_field(name=f"{p}JoinGuild/{p}LeaveGuild <guild>", value=get_lang(guild, "help_09"), inline=True)
        embed.add_field(name=f"{p}DeleteGuild <GuildID>", value=get_lang(guild, "help_10"), inline=True)
        embed.add_field(name=f"{p}GuildLink <GuildID>", value=get_lang(guild, "help_11"), inline=True)
        embed.add_field(name=f"{p}TogglePrivate <GuildID>", value=get_lang(guild, "help_12"), inline=True)
        embed.add_field(name=f"{p}leaderboard", value=get_lang(guild, "help_13"), inline=True)
        embed.add_field(name=f"{p}GuildShop <name>", value=get_lang(guild, "help_14"), inline=True)
        embed.add_field(name=f"{p}SCP <[1234567890]>", value=get_lang(guild, "help_15"), inline=True)
        embed.add_field(name=f"{p}weather city", value=get_lang(guild, "help_16"), inline=True)
        await ctx.send(embed=embed)
    elif hpage == "2":
        embed.add_field(name=f'{p}create_template [name]', value=get_lang(guild, "help_17"), inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(get_lang(guild, "PageDontExists"))

@client.command()
async def changelog(ctx, version=""):
    if not version:
        version = get_bot_version()
    changelogs = json.load(open("json/changelogs.json", 'r'))
    c = json.load(open("json/serverconfig.json", 'r'))

    embed = discord.Embed(colour=ctx.author.top_role.colour.value)
    embed.set_author(name=f"Changelog Stellarium {version}")
    embed.set_thumbnail(url=client.get_user(746348869574459472).avatar_url)

    embed.add_field(name="+", value=changelogs[version][c[str(ctx.guild.id)]["lang"]]["+"], inline=False)
    embed.add_field(name="-", value=changelogs[version][c[str(ctx.guild.id)]["lang"]]["-"], inline=False)

    await ctx.send(embed=embed)


for cmd in cmds:
    client.load_extension(f"cogs.{cmd}")



client.run(open("token.txt", "r").read())
