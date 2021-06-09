import os
import operator
import random
import discord.utils
import asyncio

from discord.ext import commands
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='.')

#GLOBALS
players = []
contestants = []
aBets = []
bBets = []
reactMessageid = 0
closeMessageId = 0
AmountOfContestants = 0
aOdds = 1
bOdds = 1
underdog_mode = True
current_underdog = ''
underdog_engaged = False
closed = False

@bot.event
async def on_ready():
    print("Bot is online.")

@bot.command(name='signup')
async def player_signup(ctx):

    global players

    if not players:
        with open('playerList.txt', 'r') as filehandle:
            for line in filehandle:
                players.append(line.split())

    found = False

    for player in players:
        if player[0] == ctx.author.name:
            response = "\nYou've already joined The Big Bet, " + ctx.author.name + "!"
            found = True
            break

    if not found:
        response = "\nWelcome to The Big Bet " + ctx.author.name + "!"
        players.append([ctx.author.name, 2000.00])
        with open('playerList.txt', 'w') as filehandle:
            for second_list in players:
                for item in second_list:
                    filehandle.write('%s ' % item)         
                filehandle.write('\n')
    
    sorted_list = sorted(players, key=lambda x: int(x[1]), reverse=True)
    playersList = ""
    for player in sorted_list:
        playersList += player[0] + " - $" + str(player[1]) + "\n"

    await ctx.send(response + "\nHere is a list of players and their money: \n" + playersList)

@bot.command(name='play')
async def play_round(ctx):
    global players
    global reactMessageid

    if not players:
        with open('playerList.txt', 'r') as filehandle:
            for line in filehandle:
                players.append(line.split())

    message = "\nIt's time to play The Big Bet! Get your wallets ready.\n\n"

    #sort players by money amount
    sorted_list = sorted(players, key=lambda x: float(x[1]), reverse=True)

    playersList = ""
    for player in sorted_list:
        playersList += player[0] + " - $" + str(player[1]) + "\n"

    message += "Current leaderboard: \n" + playersList

    message += "\nWho will be dueling? React to this message to become a contestant"
    message += "\nThe winner of the contestants will receive $2,000 and the loser $500 for participating."

    reactMessage = await ctx.send(message)
    reactMessageid = reactMessage.id
    await reactMessage.add_reaction("🅰")
    await reactMessage.add_reaction("🅱")

@bot.event
async def on_raw_reaction_add(payload):
    global AmountOfContestants
    global closeMessageId
    global reactMessageid
    global aBets
    global bBets
    global aOdds
    global bOdds
    global contestants
    global underdog_engaged
    global current_underdog
    global players
    global closed

    payout = 0

    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g : g.id == guild_id, bot.guilds)
    channel = discord.utils.get(guild.channels, name="the-big-bet")

    message = "something went wrong"

    #check to see if it is the bot
    if payload.member.name != "The Big Bet Bot":
        if payload.message_id == closeMessageId:
            if AmountOfContestants >= 2:
                # -- A winner --
                if payload.emoji.name == "🅰":
                    message = "Contestant 🅰 is the winner! Congratulations. Payouts are as follows:\n\n"

                    # get the player list
                    if not players:
                        with open('playerList.txt', 'r') as filehandle:
                            for line in filehandle:
                                players.append(line.split())

                    #--Underdog Payouts--
                    if underdog_engaged:
                        if current_underdog == 'a':
                            # contestant winnings
                            # A wins $2000 fight
                            payout = 2000
                            # A wins bets placed against him
                            for better in bBets:
                                payout += better[1]
                            for player in players:
                                if contestants[0] == player:
                                    player[1] = round(float(player[1]) + payout, 2)
                                # B wins $500
                                if contestants[1] == player:
                                    player[1] = float(player[1]) + 500.00
                            # Betters lose all bets
                            for better in bBets:
                                for player in players:
                                    if better[0] == player[0]:
                                        payout = float(better[1])
                                        player[1] = round(float(player[1]) - payout, 2)

                            # display payouts
                            message += "🅰 {} +$2000 + {}\n".format(contestants[0], payout - 2000)
                            message += "🅱 {} +$500\n".format(contestants[1])
                            for better in bBets:
                                message += "{} -${}\n".format(better[0], better[1])
                                
                        elif current_underdog == 'b':
                            # contestant winnings
                            for player in players:
                                # A wins $2000
                                if contestants[0] == player[0]:
                                    player[1] = float(player[1]) + 2000.00
                                # B wins $500
                                if contestants[1] == player[0]:
                                    player[1] = float(player[1]) + 500.00

                            # betters win a flat $750
                            for better in aBets:
                                for player in players:
                                    if better[0] == player[0]:
                                        payout = 750.00
                                        player[1] = round(float(player[1]) + payout, 2)
                            
                            # display payouts
                            message += "🅰 {} +$2000\n".format(contestants[0])
                            message += "🅱 {} +$500\n".format(contestants[1])
                            for better in aBets:
                                message += "{} +$750\n".format(better[0])

                        # update file
                        with open('playerList.txt', 'w') as filehandle:
                            for second_list in players:
                                for item in second_list:
                                    filehandle.write('%s ' % item)         
                                filehandle.write('\n')

                    else:
                        #--Normal Payouts--
                        # make payouts
                        # contestants
                        # winner A
                        for player in players:
                            if contestants[0] == player[0]:
                                payout = 2000.00
                                player[1] = round(float(player[1]) + payout, 2)
                        # loser B
                        for player in players:
                            if contestants[1] == player[0]:
                                payout = 500.00
                                player[1] = round(float(player[1]) + payout, 2)



                        # betting winners
                        for better in aBets:
                            for player in players:
                                if player[0] == better[0]:
                                    payout = float(better[1]) * aOdds
                                    player[1] = round(float(player[1]) + payout, 2)
                                    break
                        # betting losers
                        for better in bBets:
                            for player in players:
                                if player[0] == better[0]:
                                    payout = float(better[1])
                                    player[1] = round(float(player[1]) - payout, 2)
                                    break

                        # update file
                        with open('playerList.txt', 'w') as filehandle:
                            for second_list in players:
                                for item in second_list:
                                    filehandle.write('%s ' % item)         
                                filehandle.write('\n')


                        # display payouts
                        if not underdog_engaged:
                            message += "🅰 {} +$2000\n".format(contestants[0])
                            message += "🅱 {} +$500\n".format(contestants[1])
                            for better in aBets:
                                message += "{} +${}\n".format(better[0], better[1] * aOdds)
                            for better in bBets:
                                message += "{} -${}\n".format(better[0], better[1])

                        message += "Type .play to start another round\n"

                # # -- B winner --        
                elif payload.emoji.name == "🅱":
                    message = "Contestant 🅱 is the winner! Congratulations. Payouts are as follows:\n\n"

                    # get the player list
                    if not players:
                        with open('playerList.txt', 'r') as filehandle:
                            for line in filehandle:
                                players.append(line.split())

                    #--Underdog Payouts--
                    if underdog_engaged:
                        if current_underdog == 'b':
                            # contestant winnings
                            # A wins $2000 fight
                            payout = 2000
                            # A wins bets placed against him
                            for better in bBets:
                                payout += better[1]
                            for player in players:
                                if contestants[1] == player:
                                    player[1] = round(float(player[1]) + payout, 2)
                                # B wins $500
                                if contestants[0] == player:
                                    player[1] = float(player[1]) + 500.00
                            # Betters lose all bets
                            for better in bBets:
                                for player in players:
                                    if better[0] == player[0]:
                                        payout = float(better[1])
                                        player[1] = round(float(player[1]) - payout, 2)
                            
                            # display payouts
                            message += "🅰 {} +$500\n".format(contestants[0])
                            message += "🅱 {} +$2000 + {}\n".format(contestants[1], payout - 2000)
                            for better in bBets:
                                message += "{} -${}\n".format(better[0], better[1])
                            
                        elif current_underdog == 'a':
                            # contestant winnings
                            for player in players:
                                # B wins $2000
                                if contestants[1] == player[0]:
                                    player[1] = float(player[1]) + 2000.00
                                # A wins $500
                                if contestants[0] == player[0]:
                                    player[1] = float(player[1]) + 500.00

                            # betters win a flat $750
                            for better in aBets:
                                for player in players:
                                    if better[0] == player[0]:
                                        payout = 750.00
                                        player[1] = round(float(player[1]) + payout, 2)

                            # display payouts
                            message += "🅰 {} +$500\n".format(contestants[0])
                            message += "🅱 {} +$2000\n".format(contestants[1])
                            for better in bBets:
                                message += "{} +$750\n".format(better[0])
                            
                            

                        # update file
                        with open('playerList.txt', 'w') as filehandle:
                            for second_list in players:
                                for item in second_list:
                                    filehandle.write('%s ' % item)         
                                filehandle.write('\n')

                    #--Normal payouts--
                    else:
                        # get the player list
                        if not players:
                            with open('playerList.txt', 'r') as filehandle:
                                for line in filehandle:
                                    players.append(line.split())

                        # make payouts
                        # contestants
                        # winner B
                        for player in players:
                            if contestants[1] == player[0]:
                                payout = 2000.00
                                player[1] = round(float(player[1]) + payout, 2)
                        # loser A
                        for player in players:
                            if contestants[0] == player[0]:
                                payout = 500.00
                                player[1] = round(float(player[1]) + payout, 2)



                        # betting winners
                        for better in bBets:
                            for player in players:
                                if player[0] == better[0]:
                                    payout = float(better[1]) * bOdds
                                    player[1] = round(float(player[1]) + payout, 2)
                                    break
                        # betting losers
                        for better in aBets:
                            for player in players:
                                if player[0] == better[0]:
                                    payout = float(better[1])
                                    player[1] = round(float(player[1]) - payout, 2)
                                    break

                        # update file
                        with open('playerList.txt', 'w') as filehandle:
                            for second_list in players:
                                for item in second_list:
                                    filehandle.write('%s ' % item)         
                                filehandle.write('\n')


                        # display payouts
                        if not underdog_engaged:
                            message += "🅰 {} +$500\n".format(contestants[0])
                            message += "🅱 {} +$2000\n".format(contestants[1])
                            for item in bBets:
                                message += "{} +${}\n".format(item[0], item[1] + item[1] * bOdds)
                            for item in aBets:
                                message += "{} -${}\n".format(item[0], item[1])
                
                # reset globals and send message
                AmountOfContestants = 0
                aBets = []
                bBets = []
                reactMessageid = 0
                closeMessageId = 0
                contestants = []
                aOdds = 1
                bOdds = 1
                underdog_engaged = False
                closed = False
                current_underdog = ''
                await channel.send(message)

        elif AmountOfContestants < 2:
            if reactMessageid == payload.message_id:
                contestant = payload.member.name
                if contestant is not None:
                    if not contestants:
                        print("Contestant " + contestant)
                        contestants.append(contestant)
                        AmountOfContestants += 1
                    else:
                        if contestant != contestants[0]:
                            contestants.append(contestant)
                            AmountOfContestants += 1
                            message = "\nThe contestants are in!\n\n\n🅰 " + contestants[0] + "    vs.    🅱 " + contestants[1] + "\n\n\nPlace your bets by DMing the bot with \"bet a 1234\""
                            await channel.send(message)
                            
                            # Wait 30 seconds for bets before closing automatically
                            secondInt = 30
                            timerMessage = await channel.send("Timer: {}".format(secondInt))
                            while True:
                                secondInt -= 1
                                if closed:
                                    break
                                if secondInt == 0:
                                    await channel.send("Times up! Someone type .close")
                                    break
                                await timerMessage.edit(content="Timer: {}".format(secondInt))
                                await asyncio.sleep(1)

@bot.event
async def on_message(ctx):
    global aBets
    global bBets
    global players

    #check message if formatted correctly
    try:
        if not ctx.content.startswith("."):
            if ctx.author.name != "The Big Bet Bot":
                if ctx.content.startswith('bet'):
                    # get the player list
                    if not players:
                        with open('playerList.txt', 'r') as filehandle:
                            for line in filehandle:
                                players.append(line.split())
                    # did they sign up?
                    found = False
                    for player in players:
                        if player[0] == ctx.author.name:
                            found = True
                            break
                    if found:
                        if ctx.author.name not in contestants:
                            # betting is open (2 contestants)
                            if AmountOfContestants >= 2:
                                # bet_list: ['bet', 'a', '200']
                                bet_list = ctx.content.split()
                                better = ctx.author.name
                                bet = float(bet_list[2])
                                target_contestant = bet_list[1]
                                # Did they put in anything besides 'a' or 'b'
                                if (target_contestant == 'a') or (target_contestant == 'b'):
                                    # Did they bet too much?
                                    betTooMuch = False
                                    betTooLittle = False
                                    for player in players:
                                        if player[0] == ctx.author.name:
                                            if bet > float(player[1]):
                                                betTooMuch = True
                                                break
                                            if bet <= 0:
                                                betTooLittle = True
                                                break
                                    if (not betTooMuch) and (not betTooLittle):
                                        # check if they have already bet
                                        if not any(better in i for i in aBets):
                                            if not any(better in i for i in bBets):
                                                if target_contestant == 'a':
                                                    aBets.append([better, bet])
                                                if target_contestant == 'b':
                                                    bBets.append([better, bet])
                                                await ctx.reply("Your bet is locked in!")
                                                print("New bet!\n")
                                                print("aBets: {} bBets: {}".format(aBets, bBets))
                                            else:
                                                await ctx.reply("You've already bet, ass-wipe.")
                                        else:
                                            await ctx.reply("You've already bet, ass-wipe.")
                                    else:
                                        if betTooMuch:
                                            await ctx.reply("You bet more than you have! No borrowing money, moocher")
                                        elif betTooLittle:
                                            await ctx.reply("You bet $0 or less")
                                else:
                                    await ctx.reply("You didn't put in 'a' or 'b' for your bet.")
                            else:
                                await ctx.reply("Betting is not open at this time.")              
                        else:
                            await ctx.reply("You're already a contestant")
                    else:
                        await ctx.reply("You need to .signup first before placing a bet.")
            
                else:
                    await ctx.reply("I did not understand that command and I won't reply to it.")
    except:
        await ctx.reply("Something went wrong. Did you try the format \"bet a 200\"?")

    await bot.process_commands(ctx)

# close the bets, show bets, calculate odds
@bot.command(name='close')
async def close_betting(ctx):
    global underdog_mode
    global current_underdog
    global underdog_engaged
    global aBets
    global bBets
    global aOdds
    global bOdds
    global AmountOfContestants
    global closeMessageId
    global closed

    #check if .play happened
    if not AmountOfContestants < 2:
        closed = True
        message = "Bets are now closed!\n" + "React to this message with 🅰 or 🅱 to choose the winner\n\n"

        if underdog_mode:
            if not aBets:
                current_underdog = 'a'
                message += "Contestant 🅰 is the underdog! No bets were made on him and the following rules apply:\n"
                message += "1. If the underdog loses, betters will win a flat $750, Regardless of what they bet.\n"
                message += "2. If the underdog wins, the underdog will win all bets placed against him IN ADDITION to the normal prize winnings\n\n"
                underdog_engaged = True
            elif not bBets:
                current_underdog = 'b'
                message += "Contestant 🅱 is the underdog! No bets were made on him and the following rules apply:\n"
                message += "1. If the underdog loses, betters will win a flat $750, Regardless of what they bet.\n"
                message += "2. If the underdog wins, the underdog will win all bets placed against him IN ADDITION to the normal prize winnings\n\n"
                underdog_engaged = True


        aSum = 0
        bSum = 0

        #calculate odds
        for item in aBets:
            aSum += float(item[1])
        for item in bBets:
            bSum += float(item[1])

        if not underdog_engaged:
            if (bSum != 0) and (aSum != 0):
                aOdds = bSum / aSum
                bOdds = aSum / bSum
            else:
                message += "Bets do not exist on both sides, odds are set to 1.5x and money will be borrowed from loan shark.\n\n"
                aOdds = 1.5
                bOdds = 1.5

        #show sums and odds
        message += contestants[0] + " $" + str(aSum) + " - " + contestants[1] + " $" + str(bSum) + "\n"
        if not underdog_engaged:
            message += "🅰  {:.2f}/{:.2f}  🅱\n\n".format(aOdds, bOdds)
        elif current_underdog == 'a':
            message += "🅰  0/$500  🅱\n\n"
        else:
            message += "🅰  $500/0  🅱\n\n"


        #show current bets
        message += "Current bets:\n--🅰--\n"
        for better in aBets:
            message += str(better[0]) + " $" + str(better[1]) + "\n"
        message += "\n--🅱--\n"
        for better in bBets:
            message += str(better[0]) + " $" + str(better[1]) + "\n"


        closeMessage = await ctx.send(message)
        closeMessageId = closeMessage.id
        await closeMessage.add_reaction("🅰")
        await closeMessage.add_reaction("🅱")

    else:
        await ctx.reply("We haven't chosen contestants or even bet yet")

# toggle underdog mode
@bot.command(name='underdog')
async def toggle_underdog(ctx):
    global underdog_mode

    if underdog_mode:
        underdog_mode = False
        message = "Underdog mode has been disabled"
    else:
        underdog_mode = True
        message = "Underdog mode has been enabled"
    
    await ctx.send(message)


bot.run(TOKEN)