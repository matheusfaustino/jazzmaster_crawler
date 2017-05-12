#!/Users/matheusfaustino/python-env/bin/python
import scrapy
from scrapy.crawler import CrawlerProcess
import os.path

DIR_OUTPUT = os.path.dirname(os.path.abspath(__file__)) + '/../audios/'
REGEX_URL_FILE = r'https?://[^\s/$.?#].+\.mp3'


class JazzmasterSpider(scrapy.Spider):
    name = 'jazzmaster_spider'
    start_urls = ['http://www.alphafm.com.br/programas/jazzmasters']

    custom_settings = {
        'CONCURRENT_ITEMS': 2,
        'CONCURRENT_REQUESTS': 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36',
    }

    def parse(self, response):
        """ Entry point, just for the first page """

        for program in response.css('div.programa'):
            self.logger.info('Accessing Page:' + program.css('a ::attr(href)').extract_first())

            yield scrapy.Request(response.urljoin(program.css('a ::attr(href)').extract_first()),
                                 callback=self.programParse)

    def programParse(self, response):
        for title in response.xpath('//div[@class="dois-tercos"]/div[@class="lista-audio"]'):
            request = scrapy.Request(title.css('iframe ::attr(src)').extract_first(), callback=self.iframeParse)

            # removes "/" => path error
            request.meta['title'] = title.css('h2 ::text').extract_first().replace('/','-')

            self.logger.info('Fetching iFrame:' + request.meta['title'])
            yield request

    def iframeParse(self, response):
        filename = response.meta['title']
        url = response.xpath('normalize-space(/)').re_first(REGEX_URL_FILE)

        self.logger.info('Fetching mp3 ' + url)
        req = scrapy.Request(url, callback=self.savingMp3)
        req.meta['filename'] = os.path.join(DIR_OUTPUT, filename + '.mp3')

        yield req

    def savingMp3(self, response):
        if not os.path.exists(response.meta['filename']):
            self.logger.info('Saving mp3 ' + response.meta['filename'])

            with open(response.meta['filename'], 'wb') as f:
                f.write(response.body)
        else:
            self.logger.info('File already exists ' + response.meta['filename'])


process = CrawlerProcess()

process.crawl(JazzmasterSpider)
process.start()
