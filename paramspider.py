import argparse
import os
import logging
import colorama
from colorama import Fore, Style
from core import client
import re
import signal
from urllib.parse import unquote

red_color_code = "\033[91m"
reset_color_code = "\033[0m"

colorama.init(autoreset=True)

log_format = '%(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logging.getLogger('').handlers[0].setFormatter(logging.Formatter(log_format))

interrupted = False

def handle_sigint(signum, frame):
    global interrupted
    interrupted = True
    print("\n\u001b[33m[!] Paused. Press 'r' and Enter to resume.\u001b[0m")
    while interrupted:
        try:
            user_input = input()
            if user_input.strip().lower() == 'r':
                interrupted = False
                print("\u001b[32m[+] Resumed\u001b[0m")
        except EOFError:
            continue

signal.signal(signal.SIGINT, handle_sigint)

def param_extract(response, level, placeholder="FUZZ"):
    """
    Extract URLs with parameters.
    """
    parsed = list(set(re.findall(r'.*?:\/\/.*\?.*\=[^$]', response)))
    final_uris = []

    for i in parsed:
        delim = i.find('=')
        second_delim = i.find('=', i.find('=') + 1)
        final_uris.append((i[:delim + 1] + placeholder))
        if level == 'high':
            if second_delim != -1:
                final_uris.append(i[:second_delim + 1] + placeholder)

    return list(set(final_uris))

def fetch_and_extract_params(domain, stream_output, output_dir):
    """
    Fetch URLs related to a domain from Wayback Machine and extract parameters.
    Only parameterized URLs will be saved.
    """
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Fetching URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
    wayback_uri = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=txt&collapse=urlkey&fl=original&page=/"

    response = client.fetch_url_content(wayback_uri)
    if response is None:
        logging.error(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to fetch URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
        return

    urls = response.text.split()

    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(urls)) + Style.RESET_ALL} URLs for {Fore.CYAN + domain + Style.RESET_ALL}")

    final_output = []

    # 🛠 Streaming each URL
    for url in urls:
        url = unquote(url)

        if "?" in url and "=" in url:
            delim = url.find('=')
            second_delim = url.find('=', url.find('=') + 1)
            final_output.append(url[:delim + 1] + "FUZZ")
            if 'high' == "high":
                if second_delim != -1:
                    final_output.append(url[:second_delim + 1] + "FUZZ")

    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(final_output)) + Style.RESET_ALL} parameterized URLs")

    if final_output:
        results_dir = output_dir
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        result_file = os.path.join(results_dir, f"{domain}.txt")
        with open(result_file, "w") as f:
            for url in final_output:
                f.write(url + "\n")
                if stream_output:
                    print(url)

        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Saved extracted URLs to {Fore.CYAN + result_file + Style.RESET_ALL}")
    else:
        logging.info(f"{Fore.RED}[INFO]{Style.RESET_ALL} No parameterized URLs found for {Fore.CYAN + domain + Style.RESET_ALL}, skipping save.")


def main():
    """
    Main function to handle command-line arguments and start URL mining process.
    """
    log_text = """
           
                                      _    __       
   ___  ___ ________ ___ _  ___ ___  (_)__/ /__ ____
  / _ \/ _ `/ __/ _ `/  ' \(_-</ _ \/ / _  / -_) __/
 / .__/\_,_/_/  \_,_/_/_/_/___/ .__/_/\_,_/\__/_/   
/_/                          /_/                    

                              		by @NK           
    """
    colored_log_text = f"{red_color_code}{log_text}{reset_color_code}"
    print(colored_log_text)

    parser = argparse.ArgumentParser(description="Mining URLs from dark corners of Web Archives ")
    parser.add_argument("-d", "--domain", help="Domain name to fetch related URLs for.")
    parser.add_argument("-l", "--list", help="File containing a list of domain names.")
    parser.add_argument("-s", "--stream", action="store_true", help="Stream URLs on the terminal.")
    parser.add_argument("-o", "--output", help="Custom folder to save the results. Default is 'results/'", default="results")
    args = parser.parse_args()

    if not args.domain and not args.list:
        parser.error("Please provide either the -d option or the -l option.")

    if args.domain and args.list:
        parser.error("Please provide either the -d option or the -l option, not both.")

    if args.list:
        with open(args.list, "r") as f:
            domains = [line.strip().lower().replace('https://', '').replace('http://', '') for line in f.readlines()]
            domains = [domain for domain in domains if domain]  # Remove empty lines

        # Correct way to remove duplicates and keep order
        seen = set()
        domains = [x for x in domains if not (x in seen or seen.add(x))]

    else:
        domain = args.domain

    if args.domain:
        fetch_and_extract_params(domain, args.stream, args.output)

    if args.list:
        total_domains = len(domains)
        for idx, domain in enumerate(domains, 1):
            fetch_and_extract_params(domain, args.stream, args.output)

            progress = (idx / total_domains) * 100
            logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Progress: {Fore.GREEN}{idx}/{total_domains} ({progress:.2f}%){Style.RESET_ALL}")

if __name__ == "__main__":
    main()
