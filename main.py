import requests
import random
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Constants
NAMES = 1000  # Amount of usernames to save
LENGTH = 4  # Length of usernames
FILE = 'valid.txt'  # Automatically creates file
BIRTHDAY = '1999-04-20'  # User's birthday for validation
THREADS = 50  # Number of concurrent threads
WEBHOOK_URL = 'https://discord.com/api/webhooks/1519576610804596926/ZfYmWddK6hK7umvuYY_TMD6nwvpza4YPtJdsJHC1Fs_egjCHnhMn1-CzP50-XpNo1c5g'  # Replace with your webhook URL

# Color formatting for terminal output
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    GRAY = '\033[90m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

found = 0
found_lock = threading.Lock()
checked_count = 0
checked_lock = threading.Lock()

def send_webhook(username):
    """Send webhook notification when username is found"""
    try:
        data = {
            "embeds": [{
                "title": "✅ Valid Username Found!",
                "description": f"**Username:** `{username}`\n**Length:** {len(username)} characters",
                "color": 0x00ff00,
                "footer": {"text": "Roblox Username Checker"}
            }]
        }
        requests.post(WEBHOOK_URL, json=data, timeout=2)
    except:
        pass

def success(username):
    global found
    with found_lock:
        found += 1
        current_found = found
    
    print(f"{bcolors.OKBLUE}[{current_found}/{NAMES}] [+] Found Username: {username} {bcolors.ENDC}")
    with open(FILE, 'a+') as f:
        f.write(f"{username}\n")
    
    # Send webhook notification
    if WEBHOOK_URL != 'YOUR_DISCORD_WEBHOOK_URL':
        send_webhook(username)

def taken(username):
    print(f'{bcolors.FAIL}[-] {username} is taken {bcolors.ENDC}')

def make_username(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def check_username(username):
    global checked_count
    try:
        # Use session for connection pooling
        session = requests.Session()
        url = f'https://auth.roblox.com/v1/usernames/validate?request.username={username}&request.birthday={BIRTHDAY}'
        
        # Headers to simulate real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        
        response = session.get(url, headers=headers, timeout=3)
        
        with checked_lock:
            checked_count += 1
            if checked_count % 100 == 0:
                print(f"{bcolors.GRAY}[*] Checked {checked_count} usernames...{bcolors.ENDC}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:  # Username is available
                success(username)
                return True
            else:
                taken(username)
                return False
        else:
            print(f"{bcolors.WARNING}[!] Rate limited or error. Status: {response.status_code}{bcolors.ENDC}")
            time.sleep(1)
            return False
    except requests.exceptions.Timeout:
        print(f"{bcolors.WARNING}[!] Timeout for {username}{bcolors.ENDC}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"{bcolors.WARNING}[!] Error: {e}{bcolors.ENDC}")
        return False
    except Exception as e:
        print(f"{bcolors.WARNING}[!] Unexpected error: {e}{bcolors.ENDC}")
        return False

def main():
    global found
    print(f"{bcolors.HEADER}[*] Starting username checker...{bcolors.ENDC}")
    print(f"{bcolors.GRAY}[*] Target: {NAMES} usernames, Length: {LENGTH}, Threads: {THREADS}{bcolors.ENDC}")
    print(f"{bcolors.GRAY}[*] Webhook: {'Enabled' if WEBHOOK_URL != 'YOUR_DISCORD_WEBHOOK_URL' else 'Disabled'}{bcolors.ENDC}")
    
    start_time = time.time()
    
    # Generate all usernames first (faster than generating on the fly)
    usernames = [make_username(LENGTH) for _ in range(NAMES * 2)]  # Generate extra to account for duplicates
    
    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        # Submit all tasks
        future_to_username = {executor.submit(check_username, username): username for username in usernames}
        
        # Process as they complete
        for future in as_completed(future_to_username):
            try:
                future.result()  # Just to catch any exceptions
            except Exception as e:
                print(f"{bcolors.WARNING}[!] Thread error: {e}{bcolors.ENDC}")
            
            # Stop if we found enough
            if found >= NAMES:
                print(f"{bcolors.OKBLUE}[*] Found {NAMES} usernames, stopping...{bcolors.ENDC}")
                executor.shutdown(wait=False, cancel_futures=True)
                break
    
    end_time = time.time()
    print(f"{bcolors.HEADER}[*] Completed! Found {found} valid usernames in {end_time - start_time:.2f} seconds{bcolors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{bcolors.WARNING}[!] Stopped by user{bcolors.ENDC}")    response = requests.get(url, timeout=5)  # Set a timeout of 5 seconds
    response.raise_for_status()  # Raise an error for bad responses
    return response.json().get('code')

# Check usernames loop
found = 0
while found < NAMES:
    try:
        username = make_username(LENGTH)
        code = check_username(username)
        
        if code == 0:
            found += 1
            success(username)
        else:
            taken(username)
                
    except requests.exceptions.RequestException as e:
        print('Network error:', e)
    except KeyboardInterrupt:
        print("Script interrupted. Exiting...")
        break
    except Exception as e:
        print('Error:', e)

    time.sleep(0.1)  # Increased sleep time to avoid overwhelming the API

print(f"{bcolors.OKBLUE}[!] Finished {bcolors.ENDC}")
