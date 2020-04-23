import os
import re
import json

import lib.sql
import lib.formatter

try:
    raw_input
except:
    raw_input = input


# the path to the home folder
HOME = "{}/.ipbase".format(os.path.expanduser("~"))
# the path to the configuration file
CONFIG_FILE = "{}/config.json".format(HOME)
# the URL to get all the information about the IP
IP_REP_REQUEST_URL = "https://endpoint.apivoid.com/iprep/v1/pay-as-you-go/?key={}&ip={}"
# the URL to check how many credits are left on the API token
TOKEN_VALID_CHECK_URL = "https://endpoint.apivoid.com/iprep/v1/pay-as-you-go/?key={}&stats"
# the path to the database
IP_DATABASE_PATH = "{}/ipbase.sqlite".format(HOME)
# names of databases that are available
AVAILABLE_IP_DATABASE_NAMES = (
    "Anti-Attacks BL", "Backscatterer", "BlockList_de", "Brukalai_DNSBL", "CBL_AbuseAt",
    "Hostkarma_Junkemail", "IPsum", "JustSpam_org", "LAPPS Grid Blacklist", "LashBack UBL",
    "Mailspike", "NiX_Spam", "PSBL", "Redstout Threat IP lis...", "S5hbl", "SORBS", "SpamCop",
    "SpamEatingMonkeyBL", "SpamRATS", "WPBL", "AlienVault Reputation", "AntiSpam_by_CleanTalk",
    "BadIPs", "Bambenek Consulting", "Barracuda_Reputation", "BBcan177 (pfBlockerNG)",
    "BinaryDefense Ban List", "Blacklists_co", "BlockedServersRBL", "Blocklist.net.ua",
    "BloggingFusion BL", "Bogons_Team_Cymru", "Botvrij.eu", "Brute Force Blocker", "Bytefarm_ch IP BL",
    "C-APT-ure", "CERT.gov.ge", "CERT-PA", "Charles Haley", "CI Army List", "CruzIT Blocklist",
    "CSpace Hostings IP BL", "Cybercrime-tracker.net", "CyberCure", "Darklist.de", "DataPlane.org",
    "DNSBL_AbuseCH", "DroneBL", "EFnet_RBL", "EmergingThreats", "Ens160 SSH BL", "Etnetera BL",
    "Feodo Tracker", "FSpamList", "GBUdb", "GPF DNS Block List", "GreenSnow Blocklist", "HoneyDB",
    "ImproWare_DNSRBL", "InterServer IP List", "IPSpamList", "Ip-finder.me", "ISX.fr DNSBL",
    "Log.Onoh.Info", "Malc0de", "MalwareDomainList", "Matapala_org FW Log", "MaxMind High Risk IPs",
    "MegaRBL", "MKXT_NET SSH BL", "Migniot SSH Bullies", "Ms-ds-violation-ips", "Myip.ms Blacklist",
    "NEU SSH Black list", "NoIntegrity BL", "NordSpam", "NoThink.org", "Olegon Blocked IPs",
    "Organized Villainy", "Peter-s NUUG IP BL", "PlonkatronixBL", "PhishTank", "Pofon_foobar_hu",
    "ProjectHoneypot", "Reuteras Scanning List...", "Roquesor BL", "Rutgers Drop List", "S.S.S.H.I.A",
    "SANYALnet Labs Mirai I...", "Sblam", "Scientific_Spam_BL", "SCUMWARE", "Shinmura BL",
    "Snort IPFilter", "SSL Blacklist", "St Dominics Priory", "StopForumSpam", "Suomispam_RBL",
    "SURBL", "Swinog_DNSRBL", "Taichung Education", "TalosIntel IPFilter", "Threat Crowd", "Threat Sourcing",
    "Turris Greylist", "URIBL", "URLVir", "USTC IP BL", "VirBL", "VXVault", "Websworld.org", "Woody SMTP Blacklist",
    "Yeuxdelibad BL", "ZeroDot1 Bad IPs"
)


def initialize():
    """
    initialize everything so that it wont crash first run
    """
    if not os.path.exists(HOME):
        os.makedirs(HOME)
    if not os.path.exists(IP_DATABASE_PATH):
        pass
    if not os.path.exists(CONFIG_FILE):
        done = False
        config = {}
        while not done:
            api_token = raw_input("enter your API key: ")
            if not api_token.isspace() and api_token != "":
                config["api_key"] = api_token
                done = True
            else:
                lib.formatter.warn("you did not enter a valid API key, try again")
        with open(CONFIG_FILE, 'a+') as conf:
            json.dump(config, conf)
        return config
    else:
        with open(CONFIG_FILE) as conf:
            return json.load(conf)


def configure_hide_list(to_hide):
    """
    if you choose to hide some results, configure the list that will be used for the hiding URL
    :param to_hide:
    """
    if to_hide is not None:
        retval = "&exclude_engines="
        for i, item in enumerate(to_hide, start=1):
            if any(s == item for s in AVAILABLE_IP_DATABASE_NAMES):
                to_add = item.strip()
            else:
                lib.formatter.warn(
                    "database named '{}' doesn't appear to be in use by IPVoid, adding anyways".format(item)
                )
                to_add = item.strip()
            if i == len(to_hide):
                retval += "{}".format(to_add)
            else:
                retval += "{},".format(to_add)
        return retval
    return None


def test_if_enough_credits(total_ips, total_credits):
    """
    test if you have enough credits to perform the request, if not max out at a certain number
    """
    max_to_be_used = 0
    total_credits_used = total_ips * 0.08
    if total_credits_used > total_credits:
        total_that_can_be_tested = total_credits - 1 / 0.08
        lib.formatter.warn(
            "you do not have enough credits, and will only be able to parse a total of {} IP addresses "
            "which will leave you with 1 credit".format(
                round(total_that_can_be_tested)
            )
        )
        max_to_be_used += total_that_can_be_tested
    elif total_credits_used == total_credits:
        lib.formatter.warn(
            "running all these IP addresses will leave you with exactly 0 credits"
        )
        max_to_be_used += total_ips
    else:
        lib.formatter.info(
            "you have enough credits to continue successfully"
        )
        max_to_be_used += total_ips
    return max_to_be_used


def check_real_ip(ip):
    """
    verify that the IP is legit
    """
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)


def build_output(results, cursor, **kwargs):
    """
    build the output and print it
    """
    is_json = kwargs.get("is_json", False)
    is_yaml = kwargs.get("is_yaml", False)
    is_csv = kwargs.get("is_csv", False)

    output = "-" * 35 + "\n"
    if is_json:
        output = {"results": []}
    if is_yaml:
        output += "results:\n"
    if is_csv:
        output += "ip,detection_rate,total_engines,detection_percentage\n"
    for i, item in enumerate(results, start=1):
        ip, detection_rate, total_engines, detection_percentage = item[0], item[1], item[2], item[3]
        insert_string = "{} {}/{} ({})".format(ip, detection_rate, total_engines, detection_percentage)
        lib.sql.insert(insert_string, cursor)
        if is_json or is_yaml:
            if is_json:
                output["results"].append(insert_string)
            if is_yaml:
                output += "  - {}\n".format(insert_string)
        elif is_csv:
            output += "{},{},{},{}\n".format(ip, detection_rate, total_engines, detection_percentage)
        else:
            output += "{} {}/{} ({})\n".format(ip, detection_rate, total_engines, detection_percentage)
    if not is_json:
        output += "-" * 35
    if is_json:
        print("{sep}\n{j}\n{sep}".format(sep="-" * 35, j=json.dumps(output, indent=4, sort_keys=True)))
    else:
        print(output.strip())
