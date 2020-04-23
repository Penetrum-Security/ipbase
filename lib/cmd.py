import argparse

import lib.sql
import lib.formatter


class Parser(argparse.ArgumentParser):

    """
    pretty class so that it looks nice and the arguments are in their own little world
    """

    def __init__(self):
        super(Parser, self).__init__()

    @staticmethod
    def optparse():
        """
        holder function that creates the arguments themselves
        """
        parser = argparse.ArgumentParser()
        mandatory = parser.add_argument_group("mandatory", "at least one of these arguments must be provided")
        mandatory.add_argument(
            "-i", "--ip", default=None, dest="singleIp", metavar="IP-ADDY[,IP-ADDY[,...]]",
            help="Pass a single IP address to scan, or a list of IP addresses split by a comma (IP,IP,...)"
        )
        mandatory.add_argument(
            "-l", "--list", default=None, dest="ipAddressList", metavar="FILE-PATH",
            help="Pass a file containing a list of IP addresses (one per line)"
        )

        output = parser.add_argument_group("output", "arguments that control the output type")
        output.add_argument(
            "-j", "--json", default=False, dest="jsonOutput", action="store_true",
            help="Output into JSON format"
        )
        output.add_argument(
            "-y", "--yaml", default=False, dest="yamlOutput", action="store_true",
            help="Output into YAML format"
        )
        output.add_argument(
            "-c", "--csv", default=False, dest="csvOutput", action="store_true",
            help="Output into CSV format"
        )

        sql = parser.add_argument_group("database", "arguments that pertain to ipbase database")
        sql.add_argument(
            "-s", "--show", default=False, action="store_true", dest="showDatabase",
            help="Output all the IP addresses currently stored in the database"
        )

        misc = parser.add_argument_group("misc", "arguments that don't fit in with anywhere else")
        misc.add_argument(
            "-H", "--hide", default=None, dest="hideResults", metavar="DATABASE[,DATABASE[,...]]",
            help="Pass the name of a database search with IPVoid to hide the results from the output (case sensitive)"
        )
        return parser.parse_args()

    @staticmethod
    def check_args(opts, cursor):
        """
        check the arguments to see if anything that was invalid was passed
        """
        output = [opts.jsonOutput, opts.yamlOutput, opts.csvOutput]
        if opts.showDatabase:
            database_cache = lib.sql.fetch(cursor)
            if len(database_cache) == 0:
                lib.formatter.error("there are no items in the database")
                exit(1)
            else:
                for item in database_cache:
                    _, data = item
                    print(data)
            exit(1)
        if opts.singleIp is None and opts.ipAddressList is None:
            lib.formatter.error("you must pass a single IP address or an IP address list (run `-h` for help)")
            exit(1)
        if opts.ipAddressList is not None:
            try:
                open(opts.ipAddressList).close()
            except IOError:
                lib.formatter.error("provided file containing IP addresses didn't open, doest it exist?")
                exit(1)
        if opts.singleIp is not None and opts.ipAddressList is not None:
            lib.formatter.error("unable to parse both a single IP and a list of IP's, choose one")
            exit(1)
        if any(output):
            amount = 0
            for status in output:
                if status:
                    amount += 1
            if amount != 1:
                lib.formatter.error("ipbase can only process one type of output at a time")
                exit(1)
