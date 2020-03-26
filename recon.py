import requests
import time
import socket
import urllib3
import sys
import threading

from queue import Queue
socket.setdefaulttimeout(0.9)
print_lock = threading.Lock()

d = Queue()
q = Queue()
direct = Queue()

list_port=""
list_subdomain = ""
def parse_args():
    import argparse
    parse = argparse.ArgumentParser()
    parse.add_argument('-u', '--url', type=str,required=True,help="Target url.")
    parse.add_argument('-t', '--threads', type=int,required=False,default=10,help="Number threads.")
    parse.add_argument("-l", "--wordlist", help="File that contains all subdomains to scan, line by line. Default is subdomains.txt",default="subdomains.txt")
    parse.add_argument('-s', "--scan",type=str,required=True, help="Mode scan(subdomains,directory,port)",default="subdomains")
    return parse.parse_args()

def banner():
    print('''
 ____               ____ ____  ____  
/ ___| _   _ _ __  / ___/ ___||  _ \ 
\___ \| | | | '_ \| |   \___ \| |_) |
 ___) | |_| | | | | |___ ___) |  _ < 
|____/ \__,_|_| |_|\____|____/|_| \_\ 

''')


def parse_url(url):
    try:
        host = urllib3.util.url.parse_url(url).host
    except Exception as e:
        print("Invalid target, try again...")
        sys.exit(1)
    return host

def portscan(port):
    global ip
    ip = socket.gethostbyname(target_url)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((ip, port))
        with print_lock:
            print(port, 'is open')
        con.close()
    except:
        pass

def threader():
    while True:
        worker = q.get()
        portscan(worker)
        q.task_done()

def scan_subdomains(domain):
    global d,list_subdomain
    while True:
        subdomain = d.get()
        url = f"http://{subdomain}.{domain}"
        try:
            res = requests.get(url)
        except requests.ConnectionError:
            pass
        else:
            if res.status_code == 200:
                with print_lock:
                    # list_subdomain+=url+"\n"
                    print("[+] Discovered subdomain:", url)
        d.task_done()

# def dirsearch(target_url):
#     global direct
#     while True:
#         page = direct.get()
#         url = f"http://{target_url}/{page}"
#         try:
#             res = requests.get(url)
#         except requests.ConnectionError:
#             pass
#         else:
#             if res.status_code != 404:
#                 print(f"[{res.status_code}]: {url}")

#         direct.task_done()

def mutil_scan_subdomain(target_url,subdomains):
    global d
    for subdomain in subdomains:
        d.put(subdomain)
    for thread in range(number_threads):
        t = threading.Thread(target=scan_subdomains, args=(target_url,))
        t.daemon = True
        t.start()
def mutil_scan_port(target_url):
    global q
    for port in range(500):
        q.put(port)
    for x in range(100):
        t = threading.Thread(target = threader)
        t.daemon = True
        t.start()

# def mutil_scan_directory(target_url,directorys):
#     global direct
#     for directory in directorys:
#         direct.put(directory)
#     for thread in range(number_threads):
#         t = threading.Thread(target=dirsearch, args=(target_url,))
#         t.daemon = True
#         t.start()
def main(target_url,number_threads, word_list,mode_scan):
    if mode_scan == "subdomains":
        mutil_scan_subdomain(target_url=target_url,subdomains=word_list)
    # elif mode_scan == "directory":
    #     mutil_scan_directory(target_url=target_url,directorys=word_list)
    elif mode_scan == "port":
        mutil_scan_port(target_url=target_url)
    else:
        mutil_scan_subdomain(target_url=target_url,subdomains=word_list)
        mutil_scan_port(target_url=target_url)
if __name__ == "__main__":
    import time
    banner()
    args = parse_args()
    target_url = parse_url(args.url)
    wordlist = args.wordlist
    number_threads = args.threads
    mode_scan = args.scan
    main(target_url=target_url,number_threads=number_threads,word_list=open(wordlist).read().splitlines(),mode_scan=mode_scan)
    d.join()
    q.join()
    direct.join()
    # list_subdomain = list_subdomain.splitlines()