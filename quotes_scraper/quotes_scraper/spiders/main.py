import scrapy
from scrapy.crawler import CrawlerProcess


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]'):
            author_url = response.urljoin(quote.xpath('span/a/@href').get())
            yield {
                'quote': quote.xpath('span[@class="text"]/text()').get().strip(),
                'author': quote.xpath('span/small[@class="author"]/text()').get().strip(),
                'author_url': author_url,
                'tags': quote.xpath('div[@class="tags"]/a[@class="tag"]/text()').getall(),
            }

            yield response.follow(author_url, self.parse_author)

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):
        yield {
            'fullname': response.xpath('//h3[@class="author-title"]/text()').get().strip(),
            'born_date': response.xpath('//span[@class="author-born-date"]/text()').get().strip(),
            'born_location': response.xpath('//span[@class="author-born-location"]/text()').get().strip(),
            'description': response.xpath('//div[@class="author-description"]/text()').get().strip(),
        }


process = CrawlerProcess(settings={
    'FEEDS': {
        'quotes.json': {
            'format': 'json',
            'encoding': 'utf8',
            'ensure_ascii': False,
            'indent': 4,
            'fields': ['quote', 'author', 'tags']
        },
        'authors.json': {
            'format': 'json',
            'encoding': 'utf8',
            'ensure_ascii': False,
            'indent': 4,
            'fields': ['fullname', 'born_date', 'born_location', 'description']
        },
    }
})

process.crawl(QuotesSpider)
process.start()
