#!/usr/bin/env python3
import os
import discord
from random import randint
import re
import sys
import logging
from dotenv import load_dotenv

help_text = """Cześć, jestem botem do rzucania kośćmi.
Można wydawać mi polecenia na kanałach publicznych albo na chacie.
Polecenia:
.h                                Pomoc (ten tekst)
.r rzut [rzut...] [-- komentarz]
Format rzutów:
    d{k}        - kość k-ścienna, np. d6, d12, d16
    {n}d{k}     - n kości k-ściennych, zsumowane, np. 2d8, 3d6
    {n}db       - rzut pulą n kości wg zasad Blades in the Dark, np. 0db, 4db
    {n}df       - rzut kością Fudge np. 4df
    {n}dt       - rzut pulą kości d20 i wybranie największej, np. 2dt+3
    {n}d{k}+{m} - modyfikacja wyniku o stałą wartość, może być też z '-', np 2d6+3, d8-1
    {p}x{rzut}  - wykonaj p rzutów i podaj wyniki oddzielnie, np. 2xd20, 7xd10
Można pisać wielkimi albo małymi literami, np.:
.R 3D6
Komentarz (opcjonalny) można wykorzystać do oznaczenia na co się rzuca, np.:
.r d20 -- na trafienie
.r 6d6 -- fireball
.r 7xd10 -- rzucam ciężarówką
"""

console_mode = '--console' in sys.argv

log_file_name = 'rollbot.log' if not console_mode else 'rollbot_console.log'

logging.basicConfig(filename=log_file_name, level=logging.INFO)

load_dotenv()

token = os.environ.get('rollbot_token')

client = discord.Client()

dice_pattern = re.compile('^(?:(\d+)x)?(\d*)[dD]([1-9]\d*|[bBfFtT])([+-]\d+)?$')

async def on_leave():
    logging.info("Disconnecting.");
    for guild in client.guilds:
        for channel in guild.text_channels:
            await channel.send('Pa pa!')
            await client.change_presence(status = discord.Status.offline)

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
#    for guild in client.guilds:
#        for channel in guild.text_channels:
#            print(f'Got channel {channel.name} in guild {guild.name}')
#            await channel.send('Jestem!')

def blades_acc(a, b):
    if a == 'cr':
        return 'cr'
    if a == 6 and b == 6:
        return 'cr'
    return max(a, b)

def get_response(channel, author, line):
    parts = line.split(maxsplit=1)
    if(len(parts) == 0):
        return None
    command = parts[0].lower()
    if command == '.h':
        return help_text
    if command == '.r':
        if len(parts) != 2:
            return None
        logging.info('got request from %s on channel %s: %s', author, channel, line)
        parts = parts[1].split('--', maxsplit=1)
        if(len(parts)>1):
            comment = parts[1]
        else:
            comment = None
        line = parts[0]
        parts = line.split();
        response = author
        for spec in parts:
            match = dice_pattern.match(spec)
            if match:
                print("spec matched")
                times = match.group(1)
                number = match.group(2)
                die = match.group(3)
                modifier = match.group(4)
                if die.lower() == 'b':
                    faces = [1, 6]
                    strategy = 'blades'
                    acc = blades_acc
                elif die.lower() == 't':
                    faces = [1, 20]
                    strategy = 'acc0'
                    acc = max
                else:
                    strategy = 'acc0'
                    acc = lambda a, b : a + b
                    if die.lower() == 'f':
                        faces = [-1, 1]
                    else:
                        faces = [1, int(die)]
                if not times:
                    times = 1
                else:
                    times = int(times)
                if not number:
                    number = 1
                else:
                    number = int(number)
                if not modifier:
                    modifier = 0
                else:
                    modifier = int(modifier)
                response += f' {spec}:'
                for _ in range(times):
                    if strategy == 'blades' and number == 0:
                        result = min(randint(*faces), randint(*faces))
                    else:
                        result = 0
                        for _ in range(number):
                            result = acc(result, randint(*faces))
                    result += modifier
                    response += f' {result}'
            else:
                response += f' {spec}: nie rozumiem'
        if comment is not None:
            response += f' --{comment}'
        logging.info('responding: %s', response)
        return response
    else:
        return None

@client.event
async def on_message(message):
    response = get_response(message.channel, message.author.name, message.content)
    if response is not None:
        await message.channel.send(response)

if console_mode: 
    line = None
    while line != 'quit':
        line = input('>')
        response = get_response('Console_Test_Cahnnel','Console_Tester', line)
        if response is not None:
            print(response)
else:
    client.run(token)

#try:
#    client.loop.run_until_complete(client.run(token))
#finally:
#    client.loop.run_until_complete(on_leave());
#    client.loop.close()
