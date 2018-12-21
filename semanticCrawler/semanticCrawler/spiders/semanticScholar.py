# -*- coding: utf-8 -*-
import scrapy
import re


class SemanticscholarSpider(scrapy.Spider):
    name = 'semanticScholar'
    allowed_domains = ['semanticscholar.org']
    max_crawl = 2000
    crawled = 0
    start_urls = ['https://www.semanticscholar.org/paper/Coordinated-actor-model-of-self-adaptive-traffic-Bagheri-Sirjani/45ee43eb193409c96107c5aa76e8668a62312ee8', 
        'https://www.semanticscholar.org/paper/Automatic-Access-Control-Based-on-Face-and-Hand-in-Jahromi-Bonderup/2199cb39adbf22b2161cd4f65662e4a152885bae', 
        'https://www.semanticscholar.org/paper/Fair-Allocation-of-Indivisible-Goods%3A-Improvement-Ghodsi-Hajiaghayi/03d557598397d14727803987982c749fbfe1704b', 
        'https://www.semanticscholar.org/paper/Restoring-highly-corrupted-images-by-impulse-noise-Taherkhani-Jamzad/637cf5540c0fb1492d94292bf965b2c404e42fb4', 
        'https://www.semanticscholar.org/paper/Domino-Temporal-Data-Prefetcher-Bakhshalipour-Lotfi-Kamran/665c0dde22c2f8598869d690d59c9b6d84b07c01', 
        'https://www.semanticscholar.org/paper/Deep-Private-Feature-Extraction-Ossia-Taheri/3355aff37b5e4ba40fc689119fb48d403be288be']

    def parse(self, response):
        if SemanticscholarSpider.crawled >= SemanticscholarSpider.max_crawl:
            return None
        SemanticscholarSpider.crawled += 1
        
        yield {
            'type': 'paper', 
            'id': re.search(r'/paper/([^?]+)', response.url).group(1),
            'title': response.css('[data-selenium-selector=paper-detail-title]::text').extract_first(),
            'authors': response.css('meta[name=citation_author]::attr(content)').extract(),
            'date': response.css('meta[name=citation_publication_date]::attr(content)').extract_first(),
            'abstract': response.css('meta[name=description]::attr(content)').extract_first(),
            'references': [ref[7:] for ref in response.css('#references [data-selenium-selector=title-link]::attr(href)').extract()]
        }

        prefix = 'https://www.semanticscholar.org'
        refs = response.css('#references [data-selenium-selector=title-link]::attr(href)').extract()
        for ref in refs:
            yield scrapy.Request(prefix+ref, callback=self.parse)

        if response.css('#references [data-selenium-selector=inactive-page]').extract():
            page_two_url_suffix = '?citedPapersLimit=10&citedPapersOffset=10'
            yield scrapy.Request(response.url+page_two_url_suffix, callback=self.parse_extra_refs)

    def parse_extra_refs(self, response):
        yield {
            'type': 'extra-references',
            'id': re.search(r'/paper/([^?]+)', response.url).group(1),
            'references': [ref[7:] for ref in response.css('#references [data-selenium-selector=title-link]::attr(href)').extract()]
        }

