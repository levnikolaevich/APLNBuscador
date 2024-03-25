from typing import Any
import scrapy
import os
from bs4 import BeautifulSoup
import json

K_MIN_WORDS = 300
K_MAX_PAGES = 500

class APLNSpider(scrapy.Spider):
    name = 'apln_spider'

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.max_pages = K_MAX_PAGES
        self.visited_urls = set()

    def start_requests(self, urls=None):
        if urls is None:
            urls = ["https://www.ua.es"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        # Inicialmente el nombre de la página es el final de la URL
        url_parts = response.url.split("/")
        page_name = url_parts[-1]

        # Si la URL es la de la HOME, se establece el nombre de la página como 'index'
        if response.url == 'https://www.ua.es':
            page_name = 'index'
        else:
            # Si la URL termina con ".html" se elimina la extensión
            if page_name.endswith('.html'):
                page_name = os.path.splitext(page_name)[0]
            else:
                # En caso contrario se obtiene el índece anterior
                page_name = url_parts[-2]

        # Ficheros para guardar el contenido de las páginas
        save_path = 'rag-faiss/page_contents.txt'
        save_path_json = 'rag-faiss/page_contents.json'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Obtenemos el código HTML de la página
        soup = BeautifulSoup(response.text, 'html.parser')

        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        main_content = soup.find('main')
        text = main_content.get_text(separator='\n', strip=True) if main_content else ''
        word_count = len(text.split())

        # Tratamos páginas con contenido y con un mínimo de palabras
        if len(text) > 0 and word_count >= K_MIN_WORDS:
            # Guardamos el contenido de las páginas en texto plano con un formato específico
            with open(save_path, 'a', encoding='utf-8') as f:
                f.write(f"Page Name: {page_name} url: {response.url} | Content:\n{text}\n\n")
                f.write(f"=============================================================\n\n")
            self.log(f'Added content of {page_name} to {save_path}')

            # Guardamos el contenido de las páginas en un archivo JSON
            data = {
                "page_name": page_name,
                "url": response.url,
                "content": text
            }

            # Si el archivo no existe, lo creamos y guardamos el contenido
            if not os.path.isfile(save_path_json):
                with open(save_path_json, 'w', encoding='utf-8') as f:
                    json.dump([data], f, ensure_ascii=False, indent=4)
            else:
                # Si el archivo ya existe, añadimos el contenido
                with open(save_path_json, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                content.append(data)

                with open(save_path_json, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)

            self.log(f'Added content of {page_name} to {save_path_json}')

            # Marcamos la página como visitada
            self.visited_urls.add(response.url)

            # Compobamos si hemos alcanzado el número máximo de páginas visitadas
            if len(self.visited_urls) >= self.max_pages:
                self.log(f'Number of visited pages reached maximum ({self.max_pages}). Stopping crawler.')
                raise scrapy.exceptions.CloseSpider('Maximum pages reached')

            # Obtenemos los enlaces de la página y los visitamos
            for next_page in response.css('a::attr(href)').getall():
                # Ignoramos los enlaces externos
                if 'web.ua.es' not in next_page:
                    continue
                next_url = response.urljoin(next_page)

                # Si la página no ha sido visitada, la visitamos
                if next_url not in self.visited_urls:
                    yield scrapy.Request(url=next_url, callback=self.parse)
