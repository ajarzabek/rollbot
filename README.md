# Dice rolling bot for Discord

Dice rolling bot written in Python. Nothing to boast about, but may be helpful for people
who want to host their own. Intended for a Polish audioence, so instructions are in Polish.

Features:
* Use .r command syntax for easier use with soft keyboards like on mobile devices
* Perform multiple rolls on same command
* Different syntax for when you want dice addded together or when you want to know
  individual dice results (for dice pools etc.)
* Build-in support for Fudge/Fate dice and FitD rolls
* Optional comment to avoid confusion what the roll was about

Python 3.x is needed. Requirements need to be installed with pip from requirements.txt
Before running, place a file called `.env` in the current directory with the following 
contents, substituting your Discord bot token:

    rollbot_token = XXxXxxxXXXxXxxXX


