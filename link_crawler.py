""" Link Crawler
A link crawling utility that can be used to check all 
links in a domain do not lead to an error or missing page """

from time import sleep
from dataclasses import dataclass
import argparse

from playwright.sync_api import sync_playwright, Page


class OptionsException(Exception):
    """Generic Exception for if any options are incorrect or
    missing for the link crawler to run"""


@dataclass
class LinkCrawlerOptions:
    """Data class used for storing the settings for link crawler
    to run with

    Attributes:
        domain: str - Domain for the link crawler to crawl through
        max_link_limit: int - If set will stop crawling
            after finding a set amount of unique links
        stay_inside_domain: bool - If true will not travel to links
            outside of the given domain
        custom_link_locator: str|None - If set will use this locator instead
            of default 'a'
        custom_protocole: str|None - If set will use this instead of https
    """

    domain: str
    max_link_limit: int | None
    stay_inside_domain: bool
    custom_link_locator: str | None
    custom_protocole: str | None


def set_options(arguments: argparse.Namespace) -> LinkCrawlerOptions:
    """Set options into the link crawler and return the options

    Arguements:
        args: argparse.Namespace - list of command line arguements

    Returns LinkCrawlerOptions
    """
    link_crawl_options = LinkCrawlerOptions(arguments.domain, None, True, None, None)
    return link_crawl_options


def link_crawl(options: LinkCrawlerOptions):
    """Start crawling through the given domain and all links found there
    Arguements:
        options: LinkCrawlerOptions - Settings for the link crawl"""

    # Check crawling options
    if not options.domain:
        # Domain is critical, make sure its in the options before proceeding
        raise OptionsException("Missing Domain in crawler options")

    protocole = "https"

    if options.custom_protocole:
        protocole = options.custom_protocole

    domain = options.domain

    base_url = f"{protocole}://{domain}"

    link_selector = "a"

    if options.custom_link_locator:
        link_selector = options.custom_link_locator

    # Set up required variables for storing results and progress
    reported_result = {}

    # Start up playwright and crawl
    with sync_playwright() as playwright:
        # setup and start the browsing session
        firefox = playwright.firefox
        browser = firefox.launch(headless=False)
        page = browser.new_page()

        # Start by going to base URL.
        page.goto(base_url)

        sleep(5)

        all_links_elements = page.locator(link_selector).all()

        for link_element in all_links_elements:
            link_found = link_element.get_attribute("href")
            if f"{protocole}://" not in link_found:
                link_found = f"{base_url}{link_found}"
            reported_result[link_found] = None

        # Find links not visited

        next_batch = []

        for url, result in reported_result.items():
            if result is None:
                next_batch.append(url)

        for a_location in next_batch:
            if options.domain in a_location:
                navigate_action = page.goto(a_location)
                sleep(2)
                reported_result["a_location"] = navigate_action.status

        sleep(5)

        page.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Link Crawler", description="Click through all links found on domain"
    )

    parser.add_argument(dest="domain", metavar="domain")

    args = parser.parse_args()

    crawler_options = set_options(args)
    print(crawler_options)

    link_crawl(crawler_options)
