#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import argparse
from config import KNOWN_CONFS
from utils import print_help, list_conferences
from hunter import fetch_papers

# New: Mapping table from common abbreviations to internal keys
COMMON_TO_KNOWN = {
    # CCF 缩写 → DBLP 路径
    "socc": "cloud",
    "ipdps": "ipps",
    "msst": "mss",
    "atc": "usenix",
    "security": "uss",
    "csf": "csfw",
    "neurips": "nips",
    "aamas": "atal",
    "ubicomp": "huc",
    "iss": "tabletop",
    "ijcb": "icb",
    "icme": "icmcs",
    "icmr": "mir",
    "3dv": "3dim",
    "fg": "fgr",
    "lctes": "lctrts",
    "ase": "kbse",
    "idc": "acmidc",
    "scc": "ieeescc",
    "eurovis": "vissym",
    "egsr": "rt",
    "i3d": "si3d",
    "casa": "ca",
    "sstd": "ssd",
    "spm": "sma",
    "icpc": "iwpc",
    "saner": "wcre",
    "icsme": "icsm",
    "dai": "dai2",
    # 向后兼容旧版本缩写
    "iccvw": "iccv",
    "sigkdd": "kdd",
    "fse_esec": "sigsoft",
    "semweb": "iswc",
}

def parse_arguments():
    """Parse and validate command line arguments for different operation modes"""
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['help', 'conference']:
        command = sys.argv[1].lower()
        if command == 'help':
            print_help()
        elif command == 'conference':
            list_conferences()
        sys.exit(0)

    if any(arg.startswith('-') for arg in sys.argv[1:]):
        parser = argparse.ArgumentParser(description='Conference Paper Crawler', add_help=False)
        parser.add_argument('-con', nargs='+', help='Conference abbreviations (use "all" for all conferences)')
        parser.add_argument('-year', help='Single year (e.g., 2023) or year range (e.g., 2020-2023)')
        parser.add_argument('-kw', nargs='*', default=[], help='Keywords (logical OR)')
        parser.add_argument('-kw_all', nargs='*', default=[], help='Keywords (logical AND)')
        parser.add_argument('-help', action='store_true', help='Show detailed help')
        parser.add_argument('-conference', action='store_true', help='List all supported conferences')

        args = parser.parse_args()

        if args.help:
            print_help()
            sys.exit(0)
        if args.conference:
            list_conferences()
            sys.exit(0)

        if not args.con or not args.year:
            print("Error: Both -con and -year parameters are required")
            sys.exit(1)
        if not args.kw and not args.kw_all:
            print("Error: At least one of -kw or -kw_all must be provided")
            sys.exit(1)

        try:
            if '-' in args.year:
                start_year, end_year = map(int, args.year.split('-'))
                if start_year > end_year:
                    print("Error: Start year must be <= end year")
                    sys.exit(1)
                years = list(range(start_year, end_year + 1))
            else:
                years = [int(args.year)]
        except ValueError:
            print("Error: Invalid year format (e.g., 2023 or 2020-2023)")
            sys.exit(1)

        conferences = []
        display_name_map = {}

        if len(args.con) == 1 and args.con[0].lower() == 'all':
            conferences = list(KNOWN_CONFS.keys())
            display_name_map = {c: c for c in conferences}
        else:
            for conf in args.con:
                internal = COMMON_TO_KNOWN.get(conf.lower(), conf.lower())
                conferences.append(internal)
                display_name_map[internal] = conf

        unknown_confs = [c for c in conferences if c not in KNOWN_CONFS]
        if unknown_confs:
            print(f"[!] Unknown conferences: {', '.join(unknown_confs)}")
            print("Use 'conference' command to see all supported conferences")
            sys.exit(1)

        return {
            'mode': 'search',
            'conferences': conferences,
            'years': years,
            'keywords_any': args.kw,
            'keywords_all': args.kw_all,
            'display_names': display_name_map
        }

    else:
        print("Invalid command. Use 'help' to see usage.")
        sys.exit(1)

def main():
    """Main program entry point"""
    args = parse_arguments()

    print(f"[*] Searching {len(args['conferences'])} conferences across years: {', '.join(map(str, args['years']))}")
    if args['keywords_any']:
        print(f"[*] Keywords (at least one required): {', '.join(args['keywords_any'])}")
    if args['keywords_all']:
        print(f"[*] Keywords (all required): {', '.join(args['keywords_all'])}")

    all_results = []
    for conf in args['conferences']:
        for year in args['years']:
            display_conf = args['display_names'].get(conf, conf)
            print(f"\n===== Searching {display_conf.upper()} {year} =====")
            matching_papers = fetch_papers(conf, year, args['keywords_any'], args['keywords_all'])
            all_results.extend([(display_conf, year, title) for title in matching_papers])

    print(f"\n===== FINAL RESULTS ({len(all_results)} papers found) =====")
    if all_results:
        for i, (conf, year, title) in enumerate(all_results, 1):
            print(f"{i}. [{conf.upper()} {year}] {title}")
    else:
        print("No papers matched the specified criteria.")

if __name__ == "__main__":
    main()
