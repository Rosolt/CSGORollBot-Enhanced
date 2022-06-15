import random
import sys
import time
from decimal import Decimal


def check_losses(losses: int, LOSS_THRESHOLD: int):
    if losses >= LOSS_THRESHOLD:
        if random.choice([True, False]):
            print('Losses is to high ({}), taking a break for 5 minutes.'.format(losses))
            time.sleep(300)
        else:
            print('Losses is to high ({}), taking a break for 10 minutes.'.format(losses))
            time.sleep(600)
        return True
    else:
        return False


def check_earnings(earnings: Decimal, default_bet: Decimal):
    if earnings >= (default_bet * 10):
        if random.choice([True, False]):
            print('Earnings ({:.2f}) has reached 10x your default bet ({}). Sleeping for 15 minutes.'.format(earnings,
                                                                                                             default_bet))
            time.sleep(900)
        else:
            print('Earnings ({:.2f}) has reached 10x your default bet ({}). Sleeping for 30 minutes.'.format(earnings,
                                                                                                             default_bet))
            time.sleep(1800)
        return True
    else:
        return False


def check_spins(spins: int):
    if spins == 500:
        print('Spins has reached 500, exiting program. Please review the spin log before restarting.')
        sys.exit(1)
    else:
        return False


def check_jackpot(jackpot_counter: int):
    if jackpot_counter == 2:
        print('\tJackpot counter is at 2, prepare for a jackpot!')
        return True
    else:
        return False


def check_colour(choice: str, picked: str):
    if choice == picked:
        return True
    else:
        return False
