"""
Place items.

This module handles the placement of food and toys in the yard.
"""

from lib import printer

try:
    input = raw_input
except NameError:
    pass


def menu(data):
    """Display yard menu."""
    data["prefix"] = "[The Yard]".format(printer.PColors, printer.PColors)
    list_yard_items(data)
    data["in_yard"] = True
    #TODO add a picture taking option
    actions = {"list owned items": list_owned_items,
               "examine yard": list_yard_items,
               "cats": cats,
               "place toy": place,
               "place food": food,
               "leave yard": exit}
    while data["in_yard"]:
        data["completer"].set_actions(actions.keys())
        printer.prompt(data["prefix"], actions.keys())
        inp = input("{.YARD}{}{.ENDC} What do you want to do? ".format(
            printer.PColors, data["prefix"], printer.PColors))
        if inp in actions:
            actions[inp](data)
            continue
        else:
            printer.invalid(data["prefix"])


def compute_space(data):
    """Compute available yard space."""
    return data["space"] - sum([item["size"] for item in data["yard"]])


def exit(data):
    """Cancel item placement."""
    data["in_yard"] = False


def list_owned_items(data):
    """Display a list of owned items."""
    owned_items = [item["name"] for item in data["items"].values() if "owned" in item["attributes"]]
    if len(owned_items) == 0:
        printer.warn(data["prefix"], "You don't own any items, better go buy some in the shop~!")
    else:
        printer.yard(data["prefix"], "You currently own a {0}".format(", and a ".join(owned_items)))


def list_yard_items(data):
    """Display list of items placed in yard."""
    if len(data["yard"]) > 0:
        items = [item for item in data["yard"]]
        for item in items:
            cats = "no one"
            if item["occupied"]:
                cats = ", and ".join([cat for cat in item["occupant"]])
            printer.yard(data["prefix"], "Your yard currently has a {0} in it, occupied by {1}".format(item["name"], cats))
        cat_activities(data)
    # TODO: add cat descriptions
    else:
        printer.warn(data["prefix"], "You currently have nothing in your yard, how sad")
    check_food(data)


def cat_activities(data):
    """Display cat activities."""
    yard_items = [(obj, obj["occupant"]) for obj in data["yard"] if obj["occupied"]]
    for item in yard_items:
        cats = item[1]
        for cat in cats:
            printer.yard(data["prefix"], "{0} is playing with a {1}".format(cat, item[0]['name']))

def cats(data):
    """Allow you to look at the cats in your yard"""
    cats_in_yard = []
    [cats_in_yard.extend(obj["occupant"]) for obj in data["yard"] if obj["occupied"]]
    cat_names = [cat for cat in cats_in_yard]
    data["completer"].set_actions(cat_names)
    printer.yard(data["prefix"], "These are the cats in your yard:")
    for cat in cat_names:
        printer.yard(data["prefix"],cat)
    inp = input("{.YARD}{}{.ENDC} Which cat would you like to look at? ".format(
        printer.PColors, data["prefix"], printer.PColors))
    if inp in cat_names:
        desc_cat(data, [cat for cat in data["cats"] if cat == inp][0])
    else:
        printer.warn(data["prefix"], "I'm sorry that cat isn't in your yard!")

def desc_cat(data, cat):
    printer.yard(data["prefix"], data["cats"][cat]["desc"])


def place(data):
    """Place item in yard."""
    items_list = [item for item in data["items"].values()
                  if "owned" in item["attributes"] and not item["in_yard"]]
    # TODO: this is ultra gross
    placable_items = {}
    for item in items_list:
        #deliniate placable items from things like food
        if item["size"] < 15:
            placable_items[item["name"]] = item
    data["completer"].set_actions(placable_items.keys())
    printer.yard(data["prefix"], "Here are the items that you can put in your yard: {0}".format(", ".join(placable_items.keys())))
    inp = input("{.YARD}{}{.ENDC} Which item would you like to place? ".format(
        printer.PColors, data["prefix"], printer.PColors))
    if inp in placable_items.keys():
        try_to_place(data, placable_items[inp])
    else:
        printer.warn(data["prefix"], "I'm sorry I didn't recognize that item")


def try_to_place(data, item):
    """Attempt item placement in yard."""
    if sum([toy["size"] for toy in data["yard"]]) + item["size"] < data["space"]:
        data["yard"].append(item)
        item["in_yard"] = True
        printer.success(data["prefix"], "Nice! Your yard now consists of a {0}".format(", and a ".join([toy["name"] for toy in data["yard"]])))
    else:
        printer.warn(data["prefix"], "Oops that won't fit in your yard! Would you like to remove an item?")
        offer_replace(data, item)


def offer_replace(data, item):
    """Replace an existing item in yard."""
    yard_items = [toy["name"] for toy in data["yard"]]
    printer.yard(data["prefix"], "Currently in your yard you have: a {0}".format(", and a".join(yard_items)))
    data["completer"].set_actions(yard_items)
    inp = input("{.YARD}{}{.ENDC} Would you like to replace any of the items in your yard? Which one? ".format(printer.PColors, data["prefix"], printer.PColors))
    if inp in yard_items:
        remove_from_yard(data, inp)
        try_to_place(data, item)
    else:
        printer.warn(data["prefix"], "Sorry I don't see that item in your yard")


def remove_from_yard(data, item_name):
    """Remove item from yard."""
    # TODO: god help me
    to_remove = [item for item in data["yard"] if item["name"] == item_name]
    for item in to_remove:
        # TODO: clear cats from this
        data["yard"].remove(item)
        item["in_yard"] = False


def check_food(data):
    """Check food in yard."""
    if data["food_remaining"] == 0:
        printer.warn(data["prefix"], "Your yard currently doesn't have any food in it! No cats will come if there's no food!")
    else:
        printer.success(data["prefix"], "Your yard currently has a {0} in it with {1} time remaining".format(data["food"], data["food_remaining"]))


def food(data):
    """Display food placement options."""
    check_food(data)
    placable_items = {}
    for idx, item in enumerate(data["owned_food"]):
        if item["name"] not in placable_items.keys():
            placable_items[item["name"]] = [1, idx]
        else:
            placable_items[item["name"]][0] += 1
    printer.yard(data["prefix"], "Here's what you can place:")
    for key in placable_items.keys():
        printer.yard(data["prefix"], "A {0} ({1})".format(key, placable_items[key][0]))
    data["completer"].set_actions(placable_items.keys())
    to_place = input("{.YARD}{}{.ENDC} Which would you like to place? (hit ENTER if none) ".format(printer.PColors, data["prefix"], printer.PColors))
    if to_place in placable_items.keys():
        put_food_in_yard(data, placable_items[to_place][1])


def put_food_in_yard(data, arr_idx):
    """Place food in yard."""
    food = data["owned_food"].pop(arr_idx)
    data["food"] = food["name"]
    data["food_remaining"] = food["size"]
    printer.success(data["prefix"], "Sweet! Your yard now has a {0} set out, and {1} of food remaining".format(data["food"], data["food_remaining"]))
