""" Link Crawler
A link crawling utility that can be used to check all 
links in a domain do not lead to an error or missing page """

from playwright.sync_api import sync_playwright
from time import sleep
from dataclasses import dataclass
import argparse


class Options_Exception(Exception):
    """Generic Exception for if any options are incorrect or
    missing for the link crawler to run"""

    pass


@dataclass
class LinkCrawlerOptions:
    """Data class used for storing the settings for link crawler
    to run with

    Attributes:
        domain: str - Domain for the link crawler to crawl through
        max_link_limit: int - If not set to 0 will stop crawling
            after finding a set amount of unique links
        stay_inside_domain: bool - If true will not travel to links
            outside of the given domain
    """

    domain: str
    max_link_limit: int
    stay_inside_domain: bool


def set_options(args: argparse.Namespace) -> LinkCrawlerOptions:
    """Set options into the link crawler and return the options

    Arguements:
        args: argparse.Namespace - list of command line arguements

    Returns LinkCrawlerOptions
    """
    link_crawl_options = LinkCrawlerOptions(args.domain, 0, True)
    return link_crawl_options


def link_crawl(options: LinkCrawlerOptions):
    """Start crawling through the given domain and all links found there
    Arguements:
        options: LinkCrawlerOptions - Settings for the link crawl"""
    if not options.domain:
        raise Options_Exception("Missing Domain in crawler options")
    with sync_playwright() as playwright:
        firefox = playwright.firefox

        browser = firefox.launch(headless=False)
        # create a new page in a pristine context.
        page = browser.new_page()

        protocole = "https://"
        domain = options.domain

        link_selector = "a"

        page.goto(f"{protocole}{domain}")

        sleep(5)

        links_found = []

        all_links_elements = page.locator(link_selector).all()

        for link_element in all_links_elements:
            link_found = link_element.get_attribute("href")
            if protocole not in link_found:
                links_found.append(f"{protocole}{domain}{link_found}")

        for a_location in links_found:
            if domain in a_location:
                page.goto(a_location)
                sleep(2)

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
