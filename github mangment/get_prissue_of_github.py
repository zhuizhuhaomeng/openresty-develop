import urllib.request
import sys
import json

from datetime import date
from datetime import datetime
from datetime import timedelta

today = date.today()

offset = (today.weekday() - 4) % 7
offset = offset or 7
friday = today - timedelta(days=offset)
last_friday_secs = int(friday.strftime("%s"))
last_time=friday.strftime("%Y-%m-%dT%H:%M:%S")


#url=curl -H 'Accept: application/vnd.github.v3+json' https://api.github.com/repos/openresty/openresty/issues?since=2021-07-15T00:00:00


def get_pulls(repo):
    url="https://api.github.com/repos/openresty/" + repo + "/pulls?sort=update&direction=desc"
    print(url)
    req = urllib.request.Request(url)
    req.add_header("Accpet", "application/vnd.github.v3+json")
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        #print(the_page.decode("utf-8"))
        pulls = json.loads(the_page)

        prs = []
        for pr in pulls:
            sec = datetime.strptime(pr["updated_at"], '%Y-%m-%dT%H:%M:%SZ')
            update_secs = sec.timestamp()
            if sec.timestamp() < last_friday_secs:
                continue

            prs.append({"title": pr["title"], "html_url": pr["html_url"]})

        if len(prs) == 0:
            return

        print("**{}**".format(repo))
        print("| title | url | desc |")
        print("| ----- | --- | -------- |")
        for pr in prs:
            print("| ", pr["title"], " | ", pr["html_url"], " | |", end='\n')

        print("\n\n")

def get_issues(repo):
    url="https://api.github.com/repos/openresty/" + repo + "/issues?since=" + last_time
    req = urllib.request.Request(url)
    req.add_header("Accpet", "application/vnd.github.v3+json")
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        #print(the_page.decode("utf-8"))
        issues = json.loads(the_page)
        if len(issues) == 0:
            return

        print("**{}**".format(repo))
        print("| title | url | desc |")
        print("| ----- | --- | -------- |")
        for issue in issues:
            print("| ", issue["title"], " | ", issue["url"], " | |", end='\n')

        print("\n\n")


get_pulls("openresty")
get_pulls("lua-nginx-module")
get_pulls("stream-lua-nginx-module")
get_pulls("lua-resty-core")
get_pulls("lua-resty-string")
get_pulls("lua-resty-mysql")
get_pulls("lua-resty-balancer")
get_pulls("lua-cjson")
get_pulls("lua-resty-limit-traffic")
get_pulls("lua-resty-lock")
get_pulls("lua-resty-lrucache")
get_pulls("lua-resty-upload")
get_pulls("lua-resty-websocket")
get_pulls("lua-upstream-nginx-module")

get_issues("openresty")
get_issues("lua-nginx-module")
get_issues("stream-lua-nginx-module")
get_issues("lua-resty-core")
get_issues("lua-resty-string")
get_issues("lua-resty-mysql")
get_issues("lua-resty-balancer")
get_issues("lua-cjson")
get_issues("lua-resty-limit-traffic")
get_issues("lua-resty-lock")
get_issues("lua-resty-lrucache")
get_issues("lua-resty-upload")
get_issues("lua-resty-websocket")
get_issues("lua-upstream-nginx-module")
