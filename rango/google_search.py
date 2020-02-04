import json
import requests


def read_bing_key():
    bing_api_key = None
    try:
        with open('bing.key', 'r') as f:
            bing_api_key = f.readline().strip()
    except:
        try:
            with open('../youtube.key', 'r') as f:
                bing_api_key = f.readline().strip()
        except:
            raise IOError('bing.key not found')

    return bing_api_key


def run_query(search_terms):
    youtube_key = read_bing_key()
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    # headers = {'Ocp-Apim-Subscription-Key': bing_key}
    params = {
        'part': 'snippet',
        'q': search_terms,
        'key': youtube_key,
        # 'maxResults': 9,
        'type': 'video'
    }

    response = requests.get(search_url, params=params)
    print(response)

    # response.raise_for_status()
    # search_results = response.json()
    # print(search_results)
    # results = []
    # for result in search_results['webPages']['value']:
    #     results.append({
    #         'title': result['name'],
    #         'link': result['url'],
    #         'summary': result['snippet']})
    # return results


def main():
    query = input()
    run_query(query)


if __name__ == "__main__":
    main()
