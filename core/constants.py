#Registered Account
MIN_BALANCE = 10 # aprox 18000
UBI_RATE = 100  #qty per day(100)
UBI_AMOUNT = 100  #min size of installment

#Committments/Revelations
TIMEDELTA_1_HOURS = 40  #in seconds   delta
TIMEDELTA_2_HOURS = 220 #in seconds    delta+epsilon

#CreateLinks
NUM_LINKS = 10
LINK_WEIGHTING_PARAMETER = '1.3'  #as a string to be fed to Decimal

#SettleMarkets
MARKET_SETTLEMENT_TIME = 72*60*60 #in seconds
BET_BAD = 1 #200    # x
BET_GOOD = 3 #2000  # 10x

#CreateChallenge
CHALLENGER_BET = 2000
CHALLENGER_REWARD = 2000

#CreateChallengeLinks
NUM_CHALLENGE_LINKS = 5
CHALLENGE_LINK_WEIGHTING_PARAMETER = '2'

#SettleChallenge
CHALLENGE_SETTLEMENT_TIME = 72*60*60 #in seconds
CHALLENGE_BET_BAD = 2 #500
CHALLENGE_BET_GOOD = 2 #500
CHALLENGE_BET_WHO = 2 #500



