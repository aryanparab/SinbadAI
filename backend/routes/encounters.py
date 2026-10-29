"""Small, deterministic encounters. No model calls and no campaign-turn cost."""
from copy import deepcopy

INTENTS = ["pressing forward", "winding up", "guarding", "overextended"]

def create(spec, turn):
    data = spec.model_dump()
    data.update(id=f"{turn}:{spec.id}", status="active", round=0, health=100, progress=0, focus=0, intent=INTENTS[0], log=[spec.description], reward_claimed=False, used_props=[])
    return data

def resolve(encounter, action, inventory, item_name=None):
    encounter = deepcopy(encounter)
    inventory = deepcopy(inventory)
    if encounter["status"] != "active":
        raise ValueError("This encounter is already resolved.")
    if action not in ("strike", "guard", "exploit", "retreat", "item", "prop"):
        raise ValueError("Choose an available encounter action.")
    health, progress, focus = encounter["health"], encounter["progress"], encounter["focus"]
    if action == "retreat":
        encounter["status"] = "retreated"
        line = "You withdraw. The route remains open, but this mission's opportunity is lost."
    elif action == "prop":
        prop = next((p for p in encounter.get("props", []) if p["id"] == item_name), None)
        if not prop or prop["id"] in encounter.get("used_props", []):
            raise ValueError("That scene object is no longer available.")
        if prop["kind"] == "cache":
            if not prop.get("item"):
                raise ValueError("This cache contains no collectible.")
            found = deepcopy(prop["item"])
            owned = next((i for i in inventory if i["name"].casefold() == found["name"].casefold()), None)
            if owned: owned["quantity"] += found["quantity"]
            else: inventory.append(found)
            focus = min(2, focus + 1)
            line = f"Collected {found['name']} ×{found['quantity']} from {prop['name']}. +1 focus."
        elif prop["kind"] == "cover":
            health = min(100, health + 15)
            focus = min(2, focus + 1)
            line = f"You use {prop['name']}: restore up to 15 resolve and gain 1 focus."
        else:
            progress += 24
            health -= 8
            line = f"You trigger {prop['name']}: +24 progress, −8 resolve."
        encounter["used_props"] = encounter.get("used_props", []) + [prop["id"]]
    elif action == "item":
        item = next((i for i in inventory if i["name"].casefold() == (item_name or "").casefold() and i["quantity"] > 0 and i["durability"] > 0), None)
        if item is None:
            raise ValueError("That item is unavailable or broken.")
        kind = item["item_type"].lower()
        if kind in ("consumable", "food", "potion", "medical"):
            item["quantity"] -= 1
            health = min(100, health + 25)
            progress += 4
            line = f"You use {item['name']}: restore up to 25 resolve, +4 progress. One is consumed."
        elif kind in ("weapon", "sword", "ranged"):
            item["durability"] = max(0, item["durability"] - 15)
            progress += 28
            health -= 8
            line = f"You deploy {item['name']}: +28 progress, −8 resolve, −15 durability."
        else:
            wear = 10 if kind in ("artifact", "relic", "collectible") else 20
            item["durability"] = max(0, item["durability"] - wear)
            progress += 18
            focus = min(2, focus + 1)
            health -= 4
            line = f"You use {item['name']} to create an opening: +18 progress, +1 focus, −4 resolve, −{wear} durability."
        inventory = [i for i in inventory if i["quantity"] > 0]
    elif action == "guard":
        progress += 8
        health -= 4
        focus = min(2, focus + 1)
        line = "You steady the situation: +8 progress, −4 resolve, +1 focus."
    elif action == "exploit":
        opening = encounter["intent"] in ("winding up", "overextended") or focus > 0
        gain, damage = (34, 8) if opening else (10, 24)
        progress += gain
        health -= damage
        focus = max(0, focus - 1)
        line = f"{'You seize the opening' if opening else 'You act before an opening appears'}: +{gain} progress, −{damage} resolve."
    else:
        gain, damage = (14, 18) if encounter["intent"] == "guarding" else (24, 14)
        progress += gain
        health -= damage
        line = f"You commit to the advance: +{gain} progress, −{damage} resolve."
    encounter.update(round=encounter["round"] + 1, health=max(0, health), progress=min(100, progress), focus=focus)
    if encounter["status"] == "active":
        if health <= 0:
            encounter["status"] = "defeated"
            line += " You are forced to yield. This outcome will change the next story beat."
        elif progress >= 100:
            encounter["status"] = "won"
            line += " Objective secured."
        elif encounter["round"] >= 8:
            encounter["status"] = "defeated"
            line += " The opportunity closes. The story continues with the consequences."
    encounter["intent"] = INTENTS[encounter["round"] % len(INTENTS)]
    if encounter["status"] == "won" and encounter.get("reward") and not encounter["reward_claimed"]:
        reward = deepcopy(encounter["reward"])
        owned = next((i for i in inventory if i["name"].casefold() == reward["name"].casefold()), None)
        if owned:
            owned["quantity"] += reward["quantity"]
        else:
            inventory.append(reward)
        encounter["reward_claimed"] = True
        line += f" Collected {reward['name']} ×{reward['quantity']}."
    encounter["log"] = (encounter["log"] + [line])[-10:]
    return encounter, inventory
