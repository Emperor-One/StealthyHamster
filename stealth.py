import random
import sys
import urllib3
import json
import httpx
import h11
from datetime import datetime
from uuid import uuid4
from time import time, sleep
from rich.progress import Progress

BASE_URL = "https://api.gamepromo.io"
TIMEOUT = 60
REINSTALL_TIME = 100

verbose = True
all_games = False
last_game = False
chosen_game = 0
key_count = 0
total_keys = 0
level_count = 1

client_token = ""
client_id = ""

GAMES = {
    1 : {
        "name": "Chain Cube 2048",
        "event_delay": 120,
        "headers" : httpx.Headers([
            ("Host", BASE_URL[8:]),
            ("User-Agent", "UnityPlayer/2022.3.20f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"),
            ("Accept-Encoding", "deflate, gzip"),
            ("Accept", "application/json"),
            ("Authorization", ""),
            ("Content-Type", "application/json; charset=utf-8"),
            ("X-Unity-Version", "2022.3.20f1")
        ]),
        "login_data" : {
            "appToken" : "d1690a07-3780-4068-810f-9b5bbf2931b2",
            "clientOrigin" : "android",
            "clientId" : "",
            "clientVersion" : "1.78.30"
        },
        "register_data" : {
            "promoId" : "b4170868-cef0-424f-8eb9-be0622e8e8e3",
            "eventId" : "",
            "eventOrigin" : "undefined",
            "eventType" : "cube_sent"
        }
    },
    2 : {
        "name" : "Train Miner",
        "event_delay" : 600,
        "headers" : httpx.Headers([
            ("Host", BASE_URL[8:]),
            ("User-Agent", "UnityPlayer/2022.3.20f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"),
            ("Accept", "*/*"),
            ("Accept-Encoding", "gzip, deflate, br"),
            ("Content-Type", "application/json"),
            ("Authorization", ""),
            ("X-Unity-Version", "2022.3.20f1")
        ]),
        "login_data" : {
            "appToken" : "82647f43-3f87-402d-88dd-09a90025313f",
            "clientOrigin" : "android",
            "clientId" : "",
            "clientVersion" : "2.4.9"
        },
        "register_data" : {
            "promoId" : "c4480ac7-e178-4973-8061-9ed5b2e17954",
            "eventId" : "",
            "eventOrigin" : "undefined",
            "eventType" : "hitStatue"
        }
    },
    3 : {
        "name" : "Merge Away! (insufficient data)",
        "event_delay" : 50,
        "headers" : httpx.Headers([
            ("Host", BASE_URL[8:]),
            ("Authorization", "")
        ]),
        "login_data" : {
            "appToken" : "8d1cc2ad-e097-4b86-90ef-7a27e19fb833",
            "clientId" : ""
        },
        "register_data" : {
            "promoId" : "dc128d28-c45b-411c-98ff-ac7726fbaea4",
            "eventId" : ""
        }
    },
    4 : {
        "name" : "Twerk Race 3D",
        "event_delay" : 60,
        "headers" : httpx.Headers([
            ("Host", BASE_URL[8:]),
            ("User-Agent", "UnityPlayer/2021.3.15f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)"),
            ("Accept", "*/*"),
            ("Accept-Encoding", "deflate, gzip"),
            ("Content-Type", "application/json"),
            ("Authorization", ""),
            ("X-Unity-Version", "2021.3.15f1")
        ]),
        "login_data" : {
            "appToken" : "61308365-9d16-4040-8bb0-2f4a4c69074c",
            "clientOrigin" : "android",
            "clientId" : ""
        },
        "register_data" : {
            "promoId" : "61308365-9d16-4040-8bb0-2f4a4c69074c",
            "eventId" : "StartLevel",
            "eventOrigin" : "undefined"
        }
    },
    5 : {
        "name" : "Polysphere: Art Puzzle Game",
        "event_delay" : 30,
        "headers" : httpx.Headers([
            ("Host", BASE_URL[8:]),
            ("User-Agent", "UnityPlayer/2021.3.39f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"),
            ("Accept-Encoding", "deflate, gzip"),
            ("Accept", "application/json"),
            ("Authorization", ""),
            ("Content-Type", "application/json; charset=utf-8"),
            ("X-Unity-Version", "2021.3.39f1")
        ]),
        "login_data" : {
            "appToken" : "2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71",
            "clientOrigin" : "android",
            "clientId" : "",
            "clientVersion" : "1.15.21"
        },
        "register_data" : {
            "promoId" : "2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71",
            "eventId":"",
            "eventOrigin" : "undefined",
            "eventType" : "test"
        }
    },
    6 : {
        "name" : "Mow and Trim (insufficient data)",
        "event_delay" : 50,
        "headers" : httpx.Headers([
            ("Host", BASE_URL[8:]),
            ("Authorization", "")
        ]),
        "login_data" : {
            "appToken" : "ef319a80-949a-492e-8ee0-424fb5fc20a6",
            "clientId" : ""
        },
        "register_data" : {
            "promoId" : "ef319a80-949a-492e-8ee0-424fb5fc20a6",
            "eventId" : ""
        }
    }
}


def current_time(date=False):
    if date:
        return datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    return datetime.now().strftime('[%H:%M:%S]')


def progress_bar(delay_time, reinstall=False):
    with Progress() as progress:
        if reinstall: 
            task = progress.add_task(f"[cyan]Reinstalling: ", total=1000)
        else:
            task = progress.add_task(f"[cyan]Level {level_count}: ", total=1000)

        while not progress.finished:
            progress.update(task, advance=1)
            sleep(delay_time / 1000)


def sleep_handler(reinstall=False):
    if reinstall:
        if verbose: 
            print(f"{current_time()} Sleeping for {REINSTALL_TIME} seconds till next login...")
            sleep(REINSTALL_TIME + random.uniform(0, 0.2) * 1)
        else:
            print(f"{current_time()} Simulating Application Reinstall Time...")
            progress_bar(REINSTALL_TIME, reinstall=True)

    else:
        delay_time = GAMES[chosen_game]["event_delay"] * (1 + random.uniform(0, 0.3))
        if verbose: 
            print(f"{current_time()} Sleeping for {delay_time} seconds.")
            sleep(delay_time)
        else:
            print(f"{current_time()} Simulating Gameplay...")
            progress_bar(delay_time=delay_time)


def write_headers(headers, write):
    """put the Host header at the specified place, not at the top"""
    raw_items = headers._full_items
    for raw_name, name, value in raw_items:
        write(b"%s: %s\r\n" % (raw_name, value))
    write(b"\r\n")


def send_http_request(url, headers, data, proxies=None, client_token=None):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    h11._writers.write_headers = write_headers

    http1 = False
    if chosen_game == 1:
        http1 = True

    with httpx.Client(proxies=proxies, verify=False, http1=http1, timeout=TIMEOUT) as client:
        sent_headers = headers
        sent_headers["Content-Length"] = str(len(data))

        if client_token:
            sent_headers["Authorization"] = f"Bearer {client_token}"
        else:
            del sent_headers["Authorization"]
    
        request = client.build_request(
            method="POST", 
            url=url,
            data=data
        )
        request.headers = sent_headers
        
        response = client.send(request)
        response.raise_for_status()
        return response


def generate_client_id():
    global chosen_game
    global client_id

    if chosen_game == 1 or chosen_game == 6:
        suffix_1 = [str(random.randint(0,9)) for _ in range(3)]
        suffix_1 = ''.join(suffix_1)

        suffix_len = 18 if chosen_game == 1 else 19
        suffix_2 = [str(random.randint(0,9)) for _ in range(suffix_len)]
        suffix_2 = ''.join(suffix_2)

        client_id = f"{str(int(time()))}{suffix_1}-{suffix_2}"
    else:
        client_id = str(uuid4())
        if chosen_game == 2 or chosen_game == 4:
            client_id = client_id.replace("-","")
    
    GAMES[chosen_game]["login_data"]["clientId"] = client_id


def login_client():
    global client_token

    generate_client_id()

    # Convert the data to json string and remove all white spaces.
    # This is the only way to match the original string as using json directly
    # creates white spaces.
    json_string = json.dumps(GAMES[chosen_game]["login_data"]).replace(" ", "")

    try:
        if verbose: print(f"{current_time()} Sending Login request...")
        response = send_http_request(
            f"{BASE_URL}/promo/login-client", 
            headers=GAMES[chosen_game]["headers"],
            data=json_string,
            # proxies={"https://":"http://127.0.0.1:8000"}
        )
        response.raise_for_status()
        client_token = response.json()['clientToken']

        if verbose: 
            print(f"{current_time()} Logged in with Client Token: {client_token}")
            print(f"{current_time()} Client ID: {client_id}")
            print(f"{current_time()} Response HTTP Version: {response.http_version}")
            # print(f"{current_time()} Response Headers: {response.headers}")

    except Exception as e:
        print(f"{current_time()} An Error Occured while trying to login as a client:\n\t{e}")
        if verbose: 
            print(f"{current_time()} Response received: {response.text}")
            print(f"{current_time()} Response Headers: {response.headers}")
            print(f"{current_time()} HTTP Version: {response.http_version}")

        input("\nPress Enter to Exit.")
        sys.exit()


def register_event():
    global client_token

    if chosen_game != 6:
        GAMES[chosen_game]["register_data"]["eventId"] = str(uuid4())

    json_string = json.dumps(GAMES[chosen_game]["register_data"]).replace(" ", "")
    
    sleep_handler()

    try:
        response = send_http_request(
            f"{BASE_URL}/promo/register-event", 
            headers=GAMES[chosen_game]["headers"], 
            data=json_string,
            client_token=client_token,
            # proxies={"https://":"http://127.0.0.1:8080"}
        )

        if verbose: 
            print(f"{current_time()} Response received: {response.json()}")

        has_code = response.json()['hasCode']

        if has_code:
            print(f"{current_time()} Code is ready!")
        else:
            print(f"{current_time()} Code is not ready, yet.")

        return has_code

    except httpx.HTTPStatusError as e:
        print(f"{current_time()} An HTTP Error Occured while trying to register an event:\n\t{e}")
        pass

    except Exception as e:
        print(f"{current_time()} An Error Occured while trying to register an event:\n\t{e}")
        if verbose:
            print(f"{current_time()} Response received: {response.json()}")
            print(f"{current_time()}Response Headers: {response.headers}")
            print(f"{current_time()} HTTP Version: {response.http_version}")

        input("\nPress Enter to Exit.")
        sys.exit()


def create_code():
    json_string = json.dumps({"promoId": GAMES[chosen_game]["register_data"]["promoId"]}).replace(" ", "")

    try:
        response = send_http_request(
            f"{BASE_URL}/promo/create-code",
            headers=GAMES[chosen_game]["headers"],
            data=json_string,
            client_token=client_token,
            # proxies={"https://":"http://127.0.0.1:8080"}
        )

        key = response.json()['promoCode']

        # Write the Key to a file
        if key:
            print(f"{current_time()} Key Generated: {key}")
            with open("keys.txt", 'a') as file:
                file.write(f"`{key}` \n")
        
        # Update Generated Key for use with the bot
        generated_key = key

    except Exception as e:
        print(f"{current_time()} An Error Occured while trying to create the code:\n\t{e}")
        if verbose: 
            print(f"{current_time()} Response received: {response.text}")
            print(f"{current_time()} Response Headers: {response.headers}")
            print(f"{current_time()} HTTP Version: {response.http_version}")


        input("\nPress Enter to Exit.")
        sys.exit()


def play_the_game():
    global chosen_game
    global key_count
    global level_count

    print(f"{current_time()} Generating \"{GAMES[chosen_game]['name']}\" key No. {key_count+1}:")
    while True:
        has_code = register_event()
        level_count += 1

        if has_code:
            key_count += 1
            create_code()
            return


def generate_keys():
    global chosen_game
    global key_count
    global total_keys
    global all_games
    global last_game
    global level_count

    with open("keys.txt", "a") as file:
        file.write(f"{current_time(date=True)}\n")

    while key_count < total_keys:
        # if chosen_game == 5 or chosen_game == 9:
        #     print(f"{current_time()} Game is not supported yet.")
        #     break
        login_client()
        if not chosen_game == 4:
            create_code()
        play_the_game()
        level_count = 1
        # Sleep to simulate reinstall if you still need other keys
        if key_count != total_keys or ((all_games == True) and (last_game == False)):
            sleep_handler(reinstall=True)
            

def main():
    global chosen_game
    global verbose
    global key_count
    global total_keys
    global all_games
    global last_game
    global generated_key

    print("Available Games:")
    for key, value in GAMES.items():
        print(f"{key}. {value['name']}")

    set_all_games = input("Generate for all games? (N/y): ").lower()

    if set_all_games == 'y':
        all_games = True
    elif set_all_games == 'n'  or not set_all_games:
        pass
    else:
        print(f"{current_time()} Invalid input.")
        input("\nPress Enter to Exit.")
        return 

    if not all_games: 
        chosen_game = int(input(f"Enter the game number (1-{len(GAMES)}): "))
        total_keys = int(input("Enter the number of keys to generate: "))
    else:
        total_keys = int(input("Enter the number of keys to generate (per game): "))
    verbosity = input("Enable verbose mode? (N/y): ").lower()

    if verbosity == "n" or not verbosity:
        verbose = False 
    elif verbosity == "y":
        pass
    else:
        print(f"[{current_time()}] Invalid input. Verbose mode will be enabled.")
        

    if all_games:
        working_games = [1,2,4,5]
        random.shuffle(working_games)
        for i, game in enumerate(working_games):
            chosen_game = game
            if i == len(working_games) - 1:
                last_game = True
            generate_keys()
            key_count = 0
    else:
        generate_keys()
  
    input("\nPress Enter to Exit.")


if __name__ == '__main__':
    main()
