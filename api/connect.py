import requests


class IpVoidApiConnection(object):

    """
    IPVoid API class, requires and API key
    """

    def __init__(self, api_key, ip_address, req_url, to_exclude=None):
        self.api_key = api_key
        self.ip_address = ip_address
        self.to_exclude = to_exclude
        self.req_url = req_url

    def make_request(self):
        """
        make the request and get the JSON data
        """
        if self.to_exclude is not None:
            self.req_url = "{}{}".format(self.req_url, self.to_exclude)
        self.req_url = self.req_url.format(self.api_key, self.ip_address)
        try:
            req = requests.get(self.req_url)
            return req.json()
        except:
            return None
