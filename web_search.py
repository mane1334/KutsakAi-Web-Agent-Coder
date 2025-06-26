# Busca de código na web
import requests

def search_code(query):
    """
    Busca resultados rápidos na web usando DuckDuckGo.
    """
    url = 'https://api.duckduckgo.com/'
    params = {'q': query, 'format': 'json', 'no_redirect': 1, 'no_html': 1}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        abstract = data.get('AbstractText')
        if abstract:
            return abstract
        related = data.get('RelatedTopics', [])
        if related:
            return related[0].get('Text', 'Sem resultado detalhado.')
        return 'Nenhum resultado encontrado.'
    except Exception as e:
        return f'Erro na busca web: {e}'
