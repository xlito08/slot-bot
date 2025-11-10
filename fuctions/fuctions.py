from datetime import datetime, timedelta
import random
import pytz
import string
import json

async def check_channels(ch):
    try:
        with open('./database/slot.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for entry in data:
        if entry["channel"] == ch:
            return "yes"

    return "no"


async def generate_special_code(day):
    current_date = datetime.now()

    target_date = current_date + timedelta(days=day)

    special_code = int(target_date.strftime("%Y%m%d"))

    return special_code


async def check_setup(guild):
    try:
        with open("./database/setup.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for entry in data:
        if entry["guild_id"] == guild:
            return "yes"

    return "no"


async def get_category(guild):
    try:
        with open("./database/setup.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    for entry in data:
        if entry["guild_id"] == guild:
            return entry["category"]

    return None



def get_channel_ids(guild_id):
    try:
        with open('./database/slot.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    filtered_data = [entry["channel"] for entry in data if entry["guild_id"] == guild_id]
    if filtered_data:
        data = [entry for entry in data if entry not in filtered_data]
        with open("./database/slot.json", "w") as f:
            json.dump(data, f, indent=2)

    return filtered_data

async def remove_channel_entries(channel_ids):
    try:
        with open('./database/slot.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    removed_entries = []

    for channel_id in channel_ids:
        filtered_data = [entry for entry in data if entry["channel"] == channel_id]

        if filtered_data:
            data = [entry for entry in data if entry["channel"] != channel_id]
            removed_entries.extend(filtered_data)
    with open("./database/slot.json", "w") as f:
        json.dump(data, f, indent=2)

    return True
    

async def decode_special_code(code):
    code_str = str(code)

    year = int(code_str[:4])
    month = int(code_str[4:6])
    day = int(code_str[6:8])

    decoded_date = datetime(year, month, day).date()

    return decoded_date

async def recovery_code_gen():
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return code

async def rovery_enbale_guilds(guild):
    try:
        with open('./database/setup.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    for entry in data:
        if entry["guild_id"] == guild:
            if entry['recover_slot'] == 'yes':
                return "yes"
    return "no"
        
async def get_ping_alert_enable():
    try:
        with open('./database/setup.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    list_ids = []

    for entry in data:
        if entry.get("ping_reset") == "yes":
            list_ids.append(entry.get("guild_id"))

    return list_ids

async def get_ping_channel():
    try:
        with open("./database/slot.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    ids = await get_ping_alert_enable()
    channals = []
    for entry in data:
        if entry["guild_id"] in ids:
            channals.append(entry["channel"])
    return channals

async def is_valid_timezone(timezone):
    try:
        pytz.timezone(timezone)
        return True
    except pytz.UnknownTimeZoneError:
        return False



    

