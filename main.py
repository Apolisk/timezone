import requests
from typing import Optional, List

session = requests.Session()

headers = {
    "User-Agent": "curl/7.81.0", 
    "X-CSRF-Token": "0678da1685095d26eef0d62bd690a32c2bd916f4", 
}
cookies = {
    "mm_session": "98bfc36970e52a6db7b165b402c0118b6976a53b--5c8f1a5d53697bc3b9b4cd3e716507107f7d32740612a6b074d0a3f2ce7d71bc"
}
session.headers.update(headers)
session.cookies.update(cookies)

def get_my_ip() -> str:
    
    r = session.get('https://2ip.io/')
    return r.text.strip()

def get_bearer_token() -> str:
    
    r = session.post("https://www.maxmind.com/en/geoip2/demo/token")
    return r.json().get("token", "")

def get_timezone_by_ip(ip: str) -> str:
    
    token = get_bearer_token()
    session.headers.update({
        "Authorization": f"Bearer {token}"
    })
    r = session.get(f"https://geoip.maxmind.com/geoip/v2.1/city/{ip}?demo=1")
    return r.json()["location"]["time_zone"]

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
        
        timezone = get_timezone_by_ip(ip)
        print(f"My Timezone: {timezone}")
        
        matching = get_matching_timezones(timezone)
        print(f"Matching Timezones ({len(matching)}):")
        
        save_results(timezone, matching)
        
    except Exception as e:
        print(f"Error: {e}")