import re 
import requests
from typing import List


class MaxMindClient:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self._get_csrf_token()

    def _get_csrf_token(self):
        response = self.session.get('https://www.maxmind.com/en/geoip-web-services-demo')
        match = re.search(r'<input[^>]*value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token["\']', response.text)
        self.csrf_token = match.group(1)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.maxmind.com/en/geoip-web-services-demo',
            'Origin': 'https://www.maxmind.com'
        })
        
    def _get_bearer_token(self) -> str:
        self.session.headers.update({'X-CSRF-Token': self.csrf_token})
        r = self.session.post("https://www.maxmind.com/en/geoip2/demo/token")
        return r.json().get("token", "")

    def get_timezone_by_ip(self, ip: str) -> str:
        token = self._get_bearer_token()
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        r = self.session.get(f"https://geoip.maxmind.com/geoip/v2.1/city/{ip}?demo=1")
        return r.json()["location"]["time_zone"]

def get_my_ip() -> str:
    r = requests.get('https://2ip.io/', headers={'User-Agent': 'curl/7.64.1'})
    return r.text.strip()

def get_matching_timezones(target_timezone: str) -> List[str]:
    r = requests.get(
        "https://gist.githubusercontent.com/jmaicaaan/263611546fbbff498367d1bbb3347289/raw/05cc31999d7a1573445b885d0392b71751fb52a6/timezone.json"
    )
    timezones = r.json()
    matching = []
    for tz in timezones:
        label = tz.get("label")
        if target_timezone.split("/")[1].lower() in label.lower():
            matching.append(label)

    return matching

def save_results(my_timezone: str, matching_timezones: List[str], filename: str = "timezones.txt"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{my_timezone}\n")
        if matching_timezones:
            f.write(", ".join(matching_timezones) + "\n")
        else:
            f.write("No matching timezones found\n")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    try:
        ip = get_my_ip()
        print(f"My IP: {ip}")
    
        client = MaxMindClient()
        timezone = client.get_timezone_by_ip(ip)
        print(f"My Timezone: {timezone}")
    
        matching = get_matching_timezones(timezone)
        print(f"Matching Timezones ({len(matching)}):")
        
        save_results(timezone, matching)
        
    except Exception as e:
        print(f"Error: {e}")