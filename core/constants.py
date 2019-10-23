#Registered Account
MIN_BALANCE = 1 # aprox 18000
UBI_RATE = 1000  #qty per day(100)
UBI_AMOUNT = 1  #min size of installment

#Committments/Revelations
TIMEDELTA_1_HOURS = 40  #in seconds   delta
TIMEDELTA_2_HOURS = 220 #in seconds    delta+epsilon

#CreateLinks
NUM_LINKS = 5 #10
LINK_WEIGHTING_PARAMETER = '1.3'  #as a string to be fed to Decimal

#SettleMarkets
MARKET_SETTLEMENT_TIME = 72*60*60 #in seconds
BET_BAD = 200    # x
BET_GOOD = 2000  # 10x

#CreateChallenge
CHALLENGER_BET = 2000
CHALLENGER_REWARD = 2000

#CreateChallengeLinks
NUM_CHALLENGE_LINKS = 5
CHALLENGE_LINK_WEIGHTING_PARAMETER = '2'

#SettleChallenge
CHALLENGE_SETTLEMENT_TIME = 72*60*60 #in seconds
CHALLENGE_BET_BAD = 500
CHALLENGE_BET_GOOD = 500
CHALLENGE_BET_WHO = 500



