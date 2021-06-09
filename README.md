# bigBet
A discord bot that can function just like the Salty Bet. You have a group of friends that want to play a 1v1 fighting game and additional friends who would like to bet on who would win in the fight. This bot will take care of all of the betting mechanics. 

# Instructions:
  1. Run the bot and have each player type in .signup to any discord server channel (after linking up the bot to the proper server of course). This only has to happen once.
  2. Go to the character selection screen of the game of your choosing and type .play in any discord server channel.
  3. Follow the bots instructions. Contestants will need to react to the message to become contestants.
  4. Once contestants are in, a betting timer will start. Players (who aren't contestants) can dm the bot or message in the channel their bet by typing "bet a 200" or "bet b 200".
  5. Once all bets are in, type .close to close the bets. The bot will then calculate the odds. Note: Underdog mode can be toggle by typing .underdog.
  6. Once the match has finished, react to the message according to who won (a or b)

Note: You must have at least 3 people to play
Note: this won't work on your own machine unless you have an environment file set up. It should be formatted with a file titled ".env" and should have two lines of code that follow this format:

DISCORD_TOKEN=(string of letters and numbers)
DISCORD_GUILD=(Discord Server Name)
