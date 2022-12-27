import getopt
import pickle
import random
import sys
import time
from decimal import Decimal

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import checks

#################[GLOBAL VARIABLES]#################
SIM_FLAG = False
balance = Decimal('9999999.99')
USERNAME = ''
PASS = ''
LOSS_THRESHOLD = 5
default_bet = Decimal('0.5')
gamble_type = "dice"
cookies = None
#################[GLOBAL VARIABLES]#################
################[ROULETTE DEFAULTS]#################
RAND_CHOICE = False
DEFAULT_COLOUR = 'r'
################[ROULETTE DEFAULTS]#################
##################[DICE DEFAULTS]###################
roll_ratio = 47.5
dice_wait = 3
##################[DICE DEFAULTS]###################

def readArgs():
    global USERNAME, PASS, SIM_FLAG, LOSS_THRESHOLD, RAND_CHOICE, balance, default_bet
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsru:p:b:", ["uname=", "pword=", "bal=", "db=", "lt="])
    except getopt.GetoptError:
        print('GetOpt Error')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Command Line Args: -u <username> -p <password> -b <balance> --db=<default_bet> --lt=<loss_threshold> [-s <- Enables Simulation Mode] [-r <- Enables Random Choice]')
            sys.exit()
        if opt == '-s':
            print('Simulation Mode Activated')
            SIM_FLAG = True
        elif opt in ("-u", "--uname"):
            USERNAME = arg
            print("Username = {}".format(USERNAME))
        elif opt in ("-p", "--pword"):
            PASS = arg
            print('Password = {}'.format(PASS))
        elif opt in ("-b", "--bal"):
            balance = Decimal(arg)
            print('Balance = ${:.2f}'.format(balance))
        elif opt == "--db":
            default_bet = Decimal(arg)
            print('Default Bet = ${:.2f}'.format(default_bet))
        elif opt == "--lt":
            LOSS_THRESHOLD = int(arg)
            print('Loss Threshold = {}'.format(LOSS_THRESHOLD))
        elif opt == "-r":
            RAND_CHOICE = True
            print('Random Choice Enabled')

    if len(USERNAME) == 0 or len(PASS) == 0:
            USERNAME = input('Please enter your steam username: ')
            PASS = input('Please enter your steam pass: ')


def login():
    global cookies
    # Click the login button
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/cw-header/nav/div[2]/div/cw-auth-buttons/div/button'))).click()
    # Find and fill username box
    username_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[2]/div/form[1]/input[4]')))
    username_box.clear()
    username_box.send_keys(USERNAME)
    # Find and fill password box
    pass_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[2]/div/form[1]/input[5]')))
    pass_box.clear()
    pass_box.send_keys(PASS)
    # Click the login button again
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[2]/div/form[1]/div[4]/input'))).click()
    # Get authenticator code
    auth_code = input('Please enter your steam guard authenticator code: ')
    # Find and fill auth code box
    auth_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[3]/div/div/div/form/div[3]/div[1]/div/input')))
    auth_box.clear()
    auth_box.send_keys(auth_code)
    # Click the submit button
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[3]/div/div/div/form/div[4]/div[1]/div[1]'))).click()

    #Wait until we are returned to CS:GO Roll
    time.sleep(3)

    #Grab session cookies to bring to dice page
    pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

    if gamble_type == "dice":
        driver.get('https://www.csgoroll.com/en/dice')
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

def gamble_dice():
    global balance, DEFAULT_COLOUR
    total_spins = 0
    losses = 0
    earnings = Decimal('0.0')
    total_earnings = Decimal('0.0')
    last_bet = Decimal('0.0')
    won_last_round = True
    highest_best = default_bet

    while True:
        # Do Checks
        if checks.check_losses(losses, LOSS_THRESHOLD):
            losses = 0
            last_bet = default_bet
        elif checks.check_earnings(earnings, default_bet):
            total_earnings = total_earnings + earnings
            earnings = 0
        elif checks.check_spins(total_spins):
            sys.exit(1)

        # Set bet amount
        bet_amount_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-dice/section[1]/cw-dice-wager/section[3]/form/div/section[1]/div[1]/cw-amount-input/mat-form-field/div/div[1]/div[3]/div[1]/input')))
        bet_amount_element.clear()
        if won_last_round:
            bet_amount_element.send_keys(str(default_bet))
            last_bet = Decimal(str(default_bet))
        else:
            bet = str(last_bet * Decimal('2.0'))
            bet_amount_element.send_keys(bet)
            last_bet = Decimal(bet)
        
        # Set Roll Ratio Amount
        roll_under_ratio_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-dice/section[1]/cw-dice-wager/section[3]/form/div/div[1]/div[1]/div/mat-form-field/div/div[1]/div[3]/input')))
        roll_under_ratio_element.clear()
        roll_under_ratio_element.send_keys(str(roll_ratio))

        # Press green bet button
        button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-dice/section[1]/cw-dice-wager/section[3]/form/div/section[2]/div[2]/button')))

        if not SIM_FLAG:
            button.click()

        if last_bet > highest_best:
            highest_best = last_bet
        
        total_spins += 1
        print('[Round {}] Dice Roll was created, placed bet of {:.2f} with a ratio of {}'.format(total_spins, last_bet, roll_ratio))

        # Get wager result
        wager_response = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-dice/section[1]/cw-dice-wager/section[3]/form/div/div[3]/cw-pretty-balance"))
        )
        
        while True:
            class_name = wager_response.get_attribute('class')
            if 'text-success' in class_name:
                print('\tWinner!\t')
                won_last_round = True
                losses = 0
                earnings = earnings + last_bet
                balance += last_bet
            elif 'text-danger' in class_name:
                print('\tLoss\t')
                won_last_round = False
                losses += 1
                earnings = earnings - last_bet
                balance -= last_bet
            else:
                pass

            print('\tEarnings = {:.2f}\n\tBalance = {:.2f}\n\tTotal Earnings = {:.2f}'.format(earnings, balance, total_earnings))
            
            if not SIM_FLAG:
                button.click()

            print(f"Completed spin... waiting {dice_wait} seconds")
            
            time.sleep(dice_wait)

            with open('spin_log.txt', 'a+') as file:
                file.write('[Round {}/{} - {}]: Highest Bet = {:.2f}/{:.2f}  -  Total Earnings = {:.2f}  -  Balance = {:.2f}\n'.format(total_spins, DEFAULT_COLOUR, won_last_round, highest_best, last_bet, total_earnings, balance))
                file.close()
            break

def gamble_wheel():
    global balance, DEFAULT_COLOUR
    total_spins = 0
    total_blacks = 0
    total_greens = 0
    total_reds = 0
    losses = 0
    jackpot_counter = 0
    earnings = Decimal('0.0')
    total_earnings = Decimal('0.0')
    last_bet = Decimal('0.0')
    won_last_round = True
    highest_best = default_bet

    # Reset bet amount
    bet_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/cw-amount-input/mat-form-field/div/div[1]/div[3]/div[2]/input')))
    bet_box.clear()

    while True:
        # Do Checks
        if checks.check_losses(losses, LOSS_THRESHOLD):
            losses = 0
        elif checks.check_earnings(earnings, default_bet):
            total_earnings = total_earnings + earnings
            earnings = 0
        elif checks.check_spins(total_spins):
            sys.exit(1)

        # Get the roulette wheel.
        wheel = driver.find_element(By.XPATH,'/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[1]/cw-wheel')
        class_name = wheel.get_attribute('class')
        if 'created' in class_name:
            if checks.check_jackpot(jackpot_counter):
                jackpot = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/header/div/cw-roulette-jackpot/div/div/cw-pretty-balance/span')))
                jackpot_amount = jackpot.text
                print('\tJackpot Amount = {}'.format(jackpot_amount))

            # Fill bet box
            bet_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/cw-amount-input/mat-form-field/div/div[1]/div[3]/div[2]/input')))
            bet_box.clear()
            if won_last_round:
                bet_box.send_keys(str(default_bet))
                last_bet = Decimal(str(default_bet))
            else:
                bet = str(last_bet * Decimal('2.0'))
                bet_box.send_keys(bet)
                last_bet = Decimal(bet)

            # Press red bet button
            button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/div[2]/section/cw-roulette-bet-button[1]/div/button')))
            if RAND_CHOICE:
                DEFAULT_COLOUR = random.choice(['r', 'b', 'g'])
                if DEFAULT_COLOUR == 'g':
                    pass
                elif DEFAULT_COLOUR == 'b':
                    pass

            if not SIM_FLAG:
                button.click()

            if last_bet > highest_best:
                highest_best = last_bet

            total_spins += 1
            print('[Round {}] Wheel was created, placed bet of {:.2f} on {}'.format(total_spins, last_bet, DEFAULT_COLOUR))

            while True:
                class_name = wheel.get_attribute('class')
                if 'started' in class_name:
                    pass
                elif 'finished' in class_name:
                    winning_color = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/header/cw-roulette-game-rolls/section/div/a[1]/img')))
                    color = winning_color.get_attribute('src')
                    if 'black' in color:
                        if checks.check_colour(DEFAULT_COLOUR, 'b'):
                            print('\tWinner: Black\t(Win)')
                            won_last_round = True
                            losses = 0
                            earnings = earnings + last_bet
                            total_blacks += 1
                            balance += last_bet
                        else:
                            print('\tWinner: Black\t(Loss)')
                            won_last_round = False
                            losses += 1
                            earnings = earnings - last_bet
                            total_blacks += 1
                            balance -= last_bet
                        jackpot_counter = 0
                    elif 'red' in color:
                        if checks.check_colour(DEFAULT_COLOUR, 'r'):
                            print('\tWinner: Red\t(Win)')
                            won_last_round = True
                            losses = 0
                            earnings = earnings + last_bet
                            total_reds += 1
                            balance += last_bet
                        else:
                            print('\tWinner: Red\t(Loss)')
                            won_last_round = False
                            losses += 1
                            earnings = earnings - last_bet
                            total_reds += 1
                            balance -= last_bet
                        jackpot_counter = 0
                    else:
                        if checks.check_colour(DEFAULT_COLOUR, 'g'):
                            print('\tWinner: Green\t(Win)')
                            jackpot_counter += 1
                            if jackpot_counter == 3:
                                print('\tJackpot Hit!')
                                jackpot_counter = 0
                            won_last_round = True
                            losses = 0
                            earnings = earnings + (last_bet*14)
                            total_greens += 1
                            balance += last_bet*14
                        else:
                            print('\tWinner: Green\t(Loss)')
                            jackpot_counter += 1
                            if jackpot_counter == 3:
                                print('\tJackpot Hit!')
                                jackpot_counter = 0
                            won_last_round = False
                            losses += 1
                            earnings = earnings - last_bet
                            total_greens += 1
                            balance -= last_bet

                    print('\tEarnings = {:.2f}\n\tBalance = {:.2f}\n\tTotal Earnings = {:.2f}'.format(earnings, balance, total_earnings))
                    with open('spin_log.txt', 'a+') as file:
                        file.write('[Round {}/{} - {}]: Reds = {}  -  Blacks = {}  -  Greens = {}  -  Highest Bet = {:.2f}/{:.2f}  -  Total Earnings = {:.2f}  -  Balance = {:.2f}\n'.format(total_spins, DEFAULT_COLOUR, won_last_round, total_reds, total_blacks, total_greens, highest_best, last_bet, total_earnings, balance))
                        file.close()
                    break


chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.maximize_window()
driver.get('https://www.csgoroll.com/en/roll')
time.sleep(10)
try:
    # driver.get_screenshot_as_file("headless-chrome.png")
    readArgs()
    login()
    time.sleep(10)
    if gamble_type == "wheel":
        gamble_wheel()
    else:
        gamble_dice()
finally:
    driver.quit()
