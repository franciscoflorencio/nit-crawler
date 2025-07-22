from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError


class Command(ScrapyCommand):
    """
    A custom command to run all spiders in the project.
    """

    requires_project = True

    def syntax(self):
        return ""

    def short_desc(self):
        return "Runs all spiders in the project"

    def run(self, args, opts):
        if args:
            raise UsageError("No arguments are accepted.", print_help=False)

        for spider_name in self.crawler_process.spider_loader.list():
            self.crawler_process.crawl(spider_name)

        self.crawler_process.start()
