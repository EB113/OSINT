#!/usr/bin/python3

import xml.dom.minidom, itertools
import argparse, argcomplete
import requests,json, string
import os,sys,time

config = {}

registrar = {
    "namecheap": {
        "api_key" : "",
        "username":"",
        "ip" : "",
        "url" : ""
    },
    "domain_tools" : {
        "username" : "",
        "url":""
    }
}
config = {
    "throttle" : "1.0",
    "bulk_size" : "1",
    "min_size" : 3,
    "max_size" : 4,
    "top_level_domains" : ["com","ai","io","cc","co","org"]
    }
args = ""
domains = []

def namecheap():
    try:
        for jump in range(0,len(domains),int(config["bulk_size"])):
            for sub_jump in range(jump,jump+int(config["bulk_size"])):
                r = requests.get(registrar["namecheap"]["url"]+"?ApiUser="+registrar["namecheap"]["username"]+"&ApiKey="+registrar["namecheap"]["api_key"]+"&UserName="+registrar["namecheap"]["username"]+"&ClientIp="+registrar["namecheap"]["ip"]+"&Command=namecheap.domains.check&DomainList="+domains[sub_jump])
                xml_parsed = xml.dom.minidom.parseString(r.content)
                xml_parsed_nodes = xml_parsed.getElementsByTagName("DomainCheckResult")
                for elem in xml_parsed_nodes:
                    if elem.getAttribute("Available") == "false":
                        continue
                    print("[*] "+ domains[sub_jump])
                time.sleep(float(config["throttle"]))
    except Exception as e:
        print("Bad Request! {}".format(e))

switcher = {
    "namecheap" : namecheap,
}

def load_config():
    if os.path.isfile(args.load_config):
        try:
            with open(args.load_config,"r") as json_file:
                registrar["namecheap"] = json.load(json_file)
        except Exception as e:
            print("Invalid JSON file format! {}".format(e))

def smart():
    # Less 1 character
    if args.url is None:
        print("Smart mode require target URL definition. Please use either of the following flag '-u' or '--url'.")
        exit()
    #Do Others
    frobber = list(str(args.url))
    for i in range(0,len(frobber)):
        if frobber[i] == ".":
            continue
        tmp = frobber[:]
        del tmp[i]
        for tld in config["top_level_domains"]:
            domains.append("".join(tmp)+"."+tld)
    return

def wordlist():
    if os.path.isfile(args.wordlist):
        try:
            with open(args.wordlist,"r") as fd:
                for line in fd:
                    for tld in config["top_level_domains"]:
                        domains.append(line.rstrip()+"."+tld)
        except Exception as e:
            print("Invalid JSON file format! {}".format(e))
    return

def auto():
    # Add Auto configuration
    for r in range(config["min_size"],config["max_size"]):
        tmp = ["".join(elem) for elem in itertools.permutations(string.ascii_letters, r)]
        for perm in [list(zip(tmp, p)) for p in itertools.permutations(config["top_level_domains"])]:
            for elem in [".".join(elem) for elem in perm]:
                domains.append(elem)
    return

def configure():
    if args.min_size is not None:
        config["min_size"] = args.min_size
    if args.max_size:
        config["max_size"] = args.max_size
    if args.throttle:
        config["throttle"] = args.throttle
    if args.bulk_size:
        config["bulk_size"] = args.throttle
    return

def search():
    switcher.get("namecheap", "The specified Domain Registrar is not implemented!")()
    return


parser = argparse.ArgumentParser(description="Domain Name Hunter")
    
groupA = parser.add_argument_group('Tuning')
groupA.add_argument("-t_ms","--min_size", help="Minimum domain length.")
groupA.add_argument("-t_Ms","--max_size", help="Max domain length.")
groupA.add_argument("-t_t","--throttle", help="Request time interval using pythons time.sleep syntax in seconds (1,1.5,0.5,2,...).")
groupA.add_argument("-t_bs","--bulk_size", help="Number of domains requested per HTTP request.")
groupA.add_argument("-t_tld","--top_level_domain", help="Comma-seperated list for top-level domains.")
groupB = parser.add_argument_group('Modes')
groupB.add_argument("-m_s", "--smart", action="store_true", help="Phishing domain searcher based on special goodies for provided target URL.")
groupB.add_argument("-m_wl", "--wordlist", help="Search based on provided wordlist.")
groupB.add_argument("-m_a", "--auto_wordlist", action="store_true", help="Creates domain name list based on provided lengths.")
groupC = parser.add_argument_group('Endpoints')
groupC.add_argument("-e_u", "--url", help="Target URL.")
groupC.add_argument("-e_dr", "--domain_registrar", help="Desired Domain Registrar API. Some require python file parameter configuration. Defaults to using NameCheap.")
groupD = parser.add_argument_group('Others')
groupD.add_argument("-o_l", "--load_config", help="Load Configs from json file.")

args = parser.parse_args()

if len(sys.argv)==1:
    parser.print_help()
    exit()

configure()

if args.load_config:
    load_config()
if args.wordlist:
    wordlist()
if args.smart:
    smart()
if args.auto_wordlist:
    auto()

print(domains)	
search()
