from lib.cmd import Parser
from lib.sql import init_sql
from api.connect import IpVoidApiConnection
from lib.settings import (
    initialize,
    check_real_ip,
    build_output,
    test_if_enough_credits,
    configure_hide_list,
    TOKEN_VALID_CHECK_URL,
    IP_REP_REQUEST_URL
)
from lib.formatter import (
    info,
    warn,
    error
)


def main():
    opts = Parser().optparse()
    config = initialize()
    cursor = init_sql()
    Parser().check_args(opts, cursor)
    ip_addresses_to_check = set()
    info("sorting by unique IP addresses")
    if opts.singleIp is not None:
        for item in opts.singleIp.split(","):
            if check_real_ip(item.strip()):
                ip_addresses_to_check.add(item)
    if opts.ipAddressList is not None:
        with open(opts.ipAddressList) as data:
            for line in data.readlines():
                line = line.strip()
                if check_real_ip(line):
                    ip_addresses_to_check.add(line)
    if len(ip_addresses_to_check) == 0:
        error("there aren't any IP addresses to check, did you pass valid IP addresses?")
        exit(1)
    ip_addresses_to_check = list(ip_addresses_to_check)
    total_ip_addresses = len(ip_addresses_to_check)
    total_credits_left = int(round(
        IpVoidApiConnection(config["api_key"], None, TOKEN_VALID_CHECK_URL).make_request()["credits_remained"]
    ))
    info("testing if you have enough credits to run a total of {} unique IP address(es)".format(total_ip_addresses))
    amount_to_be_run = test_if_enough_credits(total_ip_addresses, total_credits_left)
    if opts.hideResults is not None:
        to_hide = configure_hide_list(opts.hideResults.split(","))
    else:
        to_hide = None
    output_results = {"results": []}
    for i, ip in enumerate(ip_addresses_to_check, start=1):
        try:
            res = IpVoidApiConnection(config["api_key"], ip, IP_REP_REQUEST_URL, to_exclude=to_hide).make_request()
            detection_percentage = res["data"]["report"]["blacklists"]["detection_rate"]
            total_engines = res["data"]["report"]["blacklists"]["engines_count"]
            decimal_percent = float("." + detection_percentage.split("%")[0])
            detection_rate = total_engines * decimal_percent
            output_results["results"].append((ip, detection_rate, total_engines, detection_percentage))
        except KeyError:
            warn("IP address {} caused an issue, skipping".format(ip))
            i -= 1
        if i == amount_to_be_run:
            break
    build_output(
        output_results["results"], cursor, is_json=opts.jsonOutput, is_csv=opts.csvOutput, is_yaml=opts.yamlOutput
    )
    credits_left = IpVoidApiConnection(config["api_key"], None, TOKEN_VALID_CHECK_URL).make_request()["credits_remained"]
    warn("you have a total of {} credits left".format(credits_left))