from monopyly import *
from collections import defaultdict


# given a property set that is an owned street and a bunch of money, figure out the house buying necessary
def build_stuff(property_set, money, stuff):
    cost = property_set.properties[0].house_price
    c1 = property_set.properties[0].number_of_houses
    c2 = property_set.properties[1].number_of_houses
    if money < cost:
        return money
    if len(property_set.properties) == 3:
        c3 = property_set.properties[2].number_of_houses
    else:
        c3 = -1
    even = max(c1,c2,c3)
    while True:
        if c3 < even and c3 != -1:
            stuff[property_set.properties[2]] += 1
            money -= cost
            if money < cost:
                return money
        if c2 < even:
            stuff[property_set.properties[1]] += 1
            money -= cost
            if money < cost:
                return money
        if c1 < even:
            stuff[property_set.properties[0]] += 1
            money -= cost
            if money < cost:
                return money
        if even == 5:
            return money
        even += 1

def do_build_houses(game_state, player, order_of_sets, money):
    to_build = defaultdict(int)
    for set in order_of_sets:
        for owned_set in player.state.owned_unmortgaged_sets:
            if owned_set.set_enum == set and owned_set.can_build_houses:
                money = build_stuff(owned_set, money, to_build)
    return [(p,q) for p,q in to_build.items()]

def sell_stuff(property_set, money, stuff):
    credit = property_set.properties[0].house_price/2
    c1 = property_set.properties[0].number_of_houses
    c2 = property_set.properties[1].number_of_houses
    if money < 0:
        return money
    if len(property_set.properties) == 3:
        c3 = property_set.properties[2].number_of_houses
    else:
        c3 = -1
    even = min(c1,c2,c3)
    while True:
        if c1 > even and c3 != -1:
            stuff[property_set.properties[2]] += 1
            money -= credit
            if money < 0:
                return money
        if c2 > even:
            stuff[property_set.properties[1]] += 1
            money -= credit
            if money < 0:
                return money
        if c1 > even:
            stuff[property_set.properties[0]] += 1
            money -= credit
            if money < 0:
                return money
        if even == 0:
            return money
        even -= 1

def do_sell_houses(game_state, player, order_of_sets, money):
    to_sell = defaultdict(int)
    for set in reversed(order_of_sets):
        for owned_set in player.state.owned_unmortgaged_sets:
            if owned_set.set_enum == set and type(owned_set.properties[0]) == Street:
                money = sell_stuff(owned_set, money, to_sell)
    selling = [(p,q) for p,q in to_sell.items()]
    return selling
