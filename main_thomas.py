import unicodedata
import httplib2
import time
import json
import logging
import urllib
from pprint import pprint
import urllib2
import random

from card import Card
from hand_evaluator import HandEvaluator

logging.basicConfig(filename='logs.log',level=logging.DEBUG)


BOTNAME = 'lolwut'
DEV = 'api'
KEY = '9a30facc-fb32-4d0c-b35e-8f8f8160e8b3'

#BOTNAME = 'Bill16'
#DEV = 'sandbox'
#KEY = 'deal-phase-key'

def rankCard(c):
    if c == 't' or c == 'T':
        rank = 10
    elif c == 'j' or c == 'J':
        rank = 11
    elif c == 'q' or c == 'Q':
        rank = 12
    elif c == 'k' or c == 'K':
        rank = 13
    elif c == 'a' or c == 'A':
        rank = 14
    elif c >= '2' and c <= '9':
        rank = ord(c) - ord('0')
    else:
        rank = 10
    return rank



def rankHand(hand):
    return rankCard(hand[0][0]) + rankCard(hand[1][0])


def str_to_suit(l):
    type(l)
    if l == u'S':
        return int(1)
    elif l == u"H":
        return int(2)
    elif l == u"D":
        return int(3)
    elif l == u"C":
        return int(4)
    else:
        return 0

def str_to_rank(l):
    if l == u"2":
        return int(1)
    elif l == u"3":
        return int(3)
    elif l == u"4":
        return int(4)
    elif l == u"5":
        return int(5)
    elif l == u"6":
        return int(6)
    elif l == u"7":
        return int(7)
    elif l == u"8":
        return int(8)
    elif l == u"9":
        return int(9)
    elif l == u"T":
        return int(9)
    elif l == u"J":
        return int(10)
    elif l == u"Q":
        return int(12)
    elif l == u"K":
        return int(13)
    elif l == u"A":
        return int(14)
    else:
        return 0



def poker_player():
    while True:
        time.sleep(1)    # sleep .25 seconds to not spam
        resp = json.loads(get())

        players = resp["players_at_table"]

        pot = 0
        for player in players:
            pot += player['current_bet']

        amountToCall = resp["call_amount"]

        #print players['player_name']
        hand = resp["hand"]
        card1 = hand[0]
        card2 = hand[1]

        s11 = str_to_rank(card1[0])
        s12 = str_to_suit(card1[1])
        c1 = Card(s11, s12)

        s21 = str_to_rank(card2[0])
        s22 = str_to_suit(card2[1])

        c2 = Card(s21, s22)

        hole = [c1, c2]

        stack = resp["stack"]
        board = []

        cc = resp["community_cards"]

        if len(cc) != 0:
            for card in cc:
                s11 = str_to_rank(card[0])

                s12 = str_to_suit(card[1])
                print s11, s12
                c = Card(s11, s12)
                board.append(c)
                print board


        score = HandEvaluator.evaluate_hand(hole, board)
        print score

        c = resp["call_amount"]

        potodds = c / (pot + c)

        handrank = rankHand(hand)
        print "hand rank: ", handrank

        if resp['name'] == BOTNAME:
            if resp["your_turn"]:
                action = None
                amount = 0
                betting_phase = resp["betting_phase"]
                if score >= 0.95:
                    action = 'raise'
                    amount = stack * 0.5
                if score >= 0.80:
                    action = 'raise'
                    amount = 0.15 * stack
                elif score >= 0.75: #call
                    action = 'call'
                else:
                    action = 'fold'

                print "action: " + action
                print 'amount: ', amount
                print 'pot odds:', potodds
                #logging.info("action:  ", action)
                #logging.info("bet amount: ", amount)
                post(action, amount)





def get():
    url = 'http://nolimitcodeem.com/' + DEV + '/players/' + KEY
    resp = urllib2.urlopen(url).read()
    print resp
    return resp


def post(action, amount=0):
    url = 'http://nolimitcodeem.com/' + DEV + '/players/' + KEY + '/action'
    if amount != 0:
        data = dict(action_name=action, amount=amount)
    else:
        data = dict(action_name=action)

    data = urllib.urlencode(data)
    req = urllib2.Request(url, data)
    rsp = urllib2.urlopen(req)
    #print rsp
    content = rsp.read()


if __name__ == '__main__':
    h = httplib2.Http()

    poker_player()