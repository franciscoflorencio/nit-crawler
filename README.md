[English](#nit-crawler---funding-opportunities-scraper) | [Português](#nit-crawler---coletor-de-oportunidades-de-financiamento-português)

---

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
│   │   ├── daad_spider.py   # DAAD-brasil.org spider
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
6. Clean the output directory: To delete all generated JSON files and start fresh, run the custom command `scrapy cleanresults`.


## Contribution Guidelines

Contributions are welcome. Please fork the repository and submit pull requests for review.

## License

This project is developed under the auspices of Fiocruz. Please contact NIT/Farmanguinhos for licensing information.

## Acknowledgments

We thank NIT/Farmanguinhos and Fiocruz for supporting this research tool development.

---

# NIT Crawler - Coletor de Oportunidades de Financiamento (Português)

## Visão Geral do Projeto

O NIT Crawler é um projeto de web scraping baseado no framework Scrapy, projetado para coletar dados de oportunidades de financiamento em sites de fomento à pesquisa brasileiros e europeus. Este projeto é desenvolvido sob os auspícios do NIT/Farmanguinhos, uma unidade da Fiocruz (Fundação Oswaldo Cruz).

## Principais Funcionalidades

- Coleta informações de oportunidades de financiamento de múltiplas fontes, incluindo:
  - Agências brasileiras (FAPESP, FAPERJ, FINEP, etc.)
  - Programas europeus (Erasmus, UKRI, etc.)
  - Outras oportunidades internacionais
- Utiliza o Playwright para lidar com sites com alto carregamento de JavaScript
- Estruturação de dados de saída em formato JSON
- Pipelines de processamento customizáveis

## Equipe do Projeto

### Supervisão
- **Orientador**: Jorge Lima de Magalhães ([Google Scholar](https://scholar.google.com.br/citations?user=_YCybrAAAAAJ&hl=pt-BR))
- **Coorientador**: Henrique Koch Chaves ([ORCID](https://orcid.org/0000-0003-3035-6799))

### Desenvolvimento
- **Desenvolvedor Inicial**:
  - Francisco Theodoro Arantes Florencio ([GitHub](https://github.com/franciscoflorencio))
- **Desenvolvedor Atual**:
  - Vitor Hugo Guerra Guimarães de Sousa ([GitHub](https://github.com/GuerraVitor/))

## Estrutura do Projeto

```
nit_crawler/
├── notices/                 # Pacote principal do projeto
│   ├── results_spiders/     # Saída de dados (resultados dos spiders)
│   ├── spiders/             # Implementações dos spiders
│   │   ├── cmp_spider.py    # Spider de financiamento CMP
│   │   ├── daad_spider.py   # Spider do DAAD-brasil.org
│   │   ├── erasmus_spider.py # Spider dos programas Erasmus
│   │   └── ...              # Outros spiders
│   ├── items.py             # Definição das estruturas de dados (Items)
│   ├── pipelines.py         # Pipelines de limpeza e processamento
│   ├── settings.py          # Configurações do projeto
│   └── ...
├── scrapy.cfg               # Configuração geral do Scrapy
└── README.md                # Este arquivo
```

## Instalação e Uso

1. Clone o repositório
2. Configure um ambiente virtual Python
3. Instale as dependências com `pip install -r requirements.txt`
4. Execute os spiders:
   - Para rodar um spider específico: `scrapy crawl <nome_do_spider>`
   - Para rodar todos os spiders de uma vez: `scrapy crawlall`
5. Encontre os resultados: Os dados coletados são salvos automaticamente como arquivos JSON no diretório `results_spiders/`.
6. Limpar o diretório de saída: Para deletar todos os arquivos JSON gerados e começar uma coleta do zero, execute o comando customizado `scrapy cleanresults`.

## Diretrizes de Contribuição

Contribuições são bem-vindas. Por favor, faça um fork do repositório e envie pull requests para revisão.

## Licença

Este projeto é desenvolvido sob os auspícios da Fiocruz. Por favor, entre em contato com o NIT/Farmanguinhos para informações sobre licenciamento.

## Agradecimentos

Agradecemos ao NIT/Farmanguinhos e à Fiocruz pelo apoio ao desenvolvimento desta ferramenta de pesquisa.
