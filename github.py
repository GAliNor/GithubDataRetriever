from search_enpoints import SearchEndpoints
from config import SOCIAL_MEDIAS, BLACKLISTED_NETLOC
from bs4 import BeautifulSoup as bs
import requests
import re

class Github:

    def __init__(self, access_token=None):
        if access_token is None:
            self.headers = {}
        else:
            self.headers = {'Authorization': f'Token {access_token}'}
        self.github_api_url = 'https://api.github.com'


    def search(self, endpoint, params=None, timeout=15):
        github_search_url = f'{self.github_api_url}/search/{endpoint}'
        if params:
            github_search_url += f'?{params}'
        data = requests.get(github_search_url, headers=self.headers, timeout=timeout).json()
        return data


    def search_users(self, query, page=1, per_page=10, timeout=15):
        try:
            params = f'{query}&per_page={per_page}&page={page}'
            return self.search(SearchEndpoints.USERS.value[0], params, timeout)
        except Exception as e:
            raise ValueError(e)
    

    def get_user_profile_data(self, username, timeout=15):
        try:
            github_search_user_url = f'{self.github_api_url}/users/{username}'
            data = requests.get(github_search_user_url, headers=self.headers, timeout=timeout).json()
            return data
        except Exception as e:
            raise ValueError(e)
    

    def get_user_repos_data(self, username, timeout=15):
        try:
            github_search_user_url = f'{self.github_api_url}/users/{username}/repos'
            data = requests.get(github_search_user_url, headers=self.headers, timeout=timeout).json()
            return data
        except Exception as e:
            raise ValueError(e)


    def get_user_repos_commits_nbr(self, user, repo, timeout=15):
        try:
            commit_nbr_regex = '\d+$'
            github_nbr_commit_url = f'https://api.github.com/repos/{user}/{repo}/commits?per_page=1'
            response = requests.get(github_nbr_commit_url, timeout)
            return re.search(commit_nbr_regex, response.links['last']['url']).group()
        except Exception as e:
            raise ValueError(e)
    

    def get_current_rate_limit_state(self, timeout=15):
        try:
            github_rate_limit_url = 'https://api.github.com/rate_limit'
            response = requests.get(github_rate_limit_url, headers=self.headers, timeout=timeout)
            return response.json()
        except Exception as e:
            raise ValueError(e)


    def get_commits_counts(self, username, timeout=15):
        try:
            params = f'q=author:{username}'
            return self.search(SearchEndpoints.COMMITS.value, params, timeout).get('total_count')
        except Exception as e:
            raise ValueError(e)


    def get_user_overview_read_me_data(self, username):
        try:
            description, useful_links, stars = None, None, None
            github_user_overview_page_url = f'https://github.com/{username}'
            data = requests.get(github_user_overview_page_url)
            soup = bs(data.text, features="html.parser")
            if soup.select('.markdown-body'):
                description = soup.select('.markdown-body')[0].get_text(' ').replace(";", ""),
                useful_links = [a.get('href') \
                                for a in soup.select('.markdown-body')[0].find_all('a', href=True) \
                                if not any(netloc in a.get('href') for netloc in BLACKLISTED_NETLOC)],
            if stars_matches := soup.findAll("a",{"data-tab-item" : "stars"}):
                stars = stars_matches[0].find('span').get_text()
            return dict(
                description = description,
                useful_links = useful_links,
                stars = stars
            )
        except Exception as e:
            print(e)
            return dict(
                description = None,
                useful_links = None,
                stars = None
            )
