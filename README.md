# NIT Crawler - Funding Opportunities Scraper

## Project Overview

The NIT Crawler is a Scrapy-based web scraping project designed to collect funding opportunity data from Brazilian and European research funding websites. This project is developed under the auspices of NIT/Farmanguinhos, a subunit of Fiocruz (Oswaldo Cruz Foundation).

## Key Features

- Scrapes funding opportunity information from multiple sources including:
  - Brazilian agencies (FAPESP, FAPERJ, FINEP, etc.)
  - European programs (Erasmus, UKRI, etc.)
  - Other international opportunities
- Uses Playwright for JavaScript-heavy websites
- Structured data output in JSON format
- Customizable scraping pipelines

## Project Team

### Supervision
- **Orientor**: Jorge Lima de Magalhães ([Google Scholar](https://scholar.google.com.br/citations?user=_YCybrAAAAAJ&hl=pt-BR))
- **Coorientor**: Henrique Koch Chaves ([ORCID](https://orcid.org/0000-0003-3035-6799))

### Development
- **Initial Developers**:
  - Francisco Theodoro Arantes Florencio ([GitHub](https://github.com/franciscoflorencio))
 **Developer**:
  - Vitor Hugo Guerra Guimarães de Sousa ([GitHub](https://github.com/GuerraVitor/))


## Project Structure

```
nit_crawler/
├── notices/                 # Main project package
│   ├── results_spiders/     # Spiders output
│   ├── spiders/             # Spider implementations
│   │   ├── cmp_spider.py    # CMP funding spider
│   │   ├── dead_spider.py   # DEAD.org.br spider
│   │   ├── erasmus_spider.py # Erasmus programs spider
│   │   └── ...              # Other spiders
│   ├── items.py             # Data structure definitions
│   ├── pipelines.py         # Data processing pipelines
│   ├── settings.py          # Project settings
│   └── ...
├── scrapy.cfg               # Scrapy configuration
└── README.md                # This file
```

## Installation & Usage

1. Clone the repository
2. Set up a Python virtual environment
3. Install dependencies with `pip install -r requirements.txt`
-4. Run spiders using `scrapy crawl <spider_name>`
+4. Run spiders:
+   - To run a specific spider: `scrapy crawl <spider_name>`
+   - To run all spiders at once: `scrapy crawlall`
+5. Find the output: Spider results are automatically saved as JSON files in the `results_spiders/` directory.


## Contribution Guidelines

Contributions are welcome. Please fork the repository and submit pull requests for review.

## License

This project is developed under the auspices of Fiocruz. Please contact NIT/Farmanguinhos for licensing information.

## Acknowledgments

We thank NIT/Farmanguinhos and Fiocruz for supporting this research tool development.
