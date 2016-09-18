import requests


class EmbedSession:
    API_ENDPOINT = 'https://api.mailmojo.no/v1/embed/'
    TYPE_NEWSLETTERS = 'newsletters'
    TYPES = (
        TYPE_NEWSLETTERS,
    )

    @property
    def header_data(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.access_token),
        }

    @property
    def session_data(self):
        return {
            'session_type': self.session_type,
            'user_ip': self.user_ip,
            'options': self.options,
        }

    def __init__(self, access_token, session_type, user_ip, options):
        assert session_type in self.TYPES
        assert access_token

        self.access_token = access_token
        self.session_type = session_type
        self.user_ip = user_ip
        self.options = options

    def create(self):
        response = requests.post(
            self.API_ENDPOINT,
            headers=self.header_data,
            json=self.session_data,
        )

        # Most likely an expired token
        if response.status_code == 401:
            return False

        # Make sure we raise exceptions for all other status codes than 2xx
        response.raise_for_status()

        return {
            'url': response.headers['Location'],
            'content': response.text,
        }
