from dotenv import dotenv_values
from sys import exit
from logging import error, basicConfig as logConfig, INFO

logConfig(level=INFO)

config = dotenv_values(".env")
LB_TTL = int(config["LB_CACHE_TTL"])
if LB_TTL < 60:
    error("Leaderboard cache TTL is too low!")
    exit(1)
