import requests
import json
import os
import re

BASE = """---
id: default_repositories
title: Default repositories
description: "Default repositories in HACS"
custom_edit_url: null
---
Dedicated unofficial website to browse repositories: <a href='https://hacs-repositories.web.app/' target='_blank'>hacs-repositories.web.app</a>
<!-- The content of this file is autogenerated during build with script/generate_default_repositories.py -->
"""

REPOSITORY_BASE = """---
id: {id}
title: "{name}"
description: "{description}"
custom_edit_url: null
---
<!-- The content of this file is autogenerated during build with script/generate_default_repositories.py -->

"""

NOTE_INTEGRATION = """

:::info
This repository is included in HACS by default and you can download it by clicking the "Explore & Download Repositories" button in the bottom right corner on the "Integrations" tab inside HACS.

![explore_download_button](/img/explore_download_button.png)
:::

"""

NOTE_PLUGIN = """

:::info
This repository is included in HACS by default and you can download it by clicking the "Explore & Download Repositories" button in the bottom right corner on the "Frontend" tab inside HACS.

![explore_download_button](/img/explore_download_button.png)
:::

"""

NOTE_THEME = """

:::info
This repository is included in HACS by default, but before you can download it you need to configure themes, [inscrutctions on that can be found here.](/docs/categories/themes#enable-themes-in-home-assistant)
Once you have restarted Home Assistant after enabling themes you can download it by clicking the "Explore & Download Repositories" button in the bottom right corner on the "Frontend" tab inside HACS.

![explore_download_button](/img/explore_download_button.png)
:::

"""

NOTE_PYTHON_SCRIPT = """

:::info
This repository is included in HACS by default, but before you can download it you need to configure `python_script`, [inscrutctions on that can be found here.](/docs/categories/python_scripts#enable-python-scripts-in-home-assistant)
Once you have restarted Home Assistant after enabling `python_script` you can download it by clicking the "Explore & Download Repositories" button in the bottom right corner on the "Automation" tab inside HACS.

![explore_download_button](/img/explore_download_button.png)
:::

"""

NOTE_APPDAEMON = """

:::info
This repository is included in HACS by default, but before you can download it you need to configure HACS for AppDaemon, [inscrutctions on that can be found here.](/docs/categories/appdaemon_apps#enable-appdaemon-apps-in-hacs)
Once you have enabled AppDaemon Apps in HACS you can download it by clicking the "Explore & Download Repositories" button in the bottom right corner on the "Automation" tab inside HACS.

![explore_download_button](/img/explore_download_button.png)
:::

"""

NOTE_NETDAEMON = """

:::info
This repository is included in HACS by default, but before you can download it you need to configure HACS for NetDaemon, [inscrutctions on that can be found here.](/docs/categories/netdaemon_apps#enable-netdaemon-apps-in-hacs)
Once you have enabled NetDaemon Apps in HACS you can download it by clicking the "Explore & Download Repositories" button in the bottom right corner on the "Automation" tab inside HACS.

![explore_download_button](/img/explore_download_button.png)
:::

"""

NOTES = {
    "integration": NOTE_INTEGRATION,
    "plugin": NOTE_PLUGIN,
    "theme": NOTE_THEME,
    "python_script": NOTE_PYTHON_SCRIPT,
    "appdaemon": NOTE_APPDAEMON,
    "netdaemon": NOTE_NETDAEMON,
}

resp = requests.get("https://raw.githubusercontent.com/hacs/integration/main/custom_components/hacs/utils/default.repositories")
repositories = resp.json()

data = {"integration": [], "plugin": [], "theme": [],"appdaemon": [], "netdaemon": [], "python_script": []}

for repository in repositories.values():
    if repository["full_name"] == "hacs/integration":
        continue
    data[repository["category"]].append(repository)

BASE += f"There are currently {sum(len(category) for category in data.values())} default repositories in HACS in {len(data.keys())} categories."

def gen_authors(authors):
    links = []
    for author in authors:
        links.append(f"<a href='https://github.com/{author.replace('@', '')}' target='_blank'>{author.replace('@', '')}</a>")
        return f"<p style={{{{marginBottom: 0}}}}>Author{'s' if len(links) != 1 else ''}: <i>{', '.join(links)}</i></p>"

def gen_brands_icon(entry):
    if not entry["domain"] or not isinstance(entry["domain"], str):
        return ""
    return f"<img style={{{{maxHeight: 48, maxWidht: 48, marginRight: 8}}}} src='https://brands.home-assistant.io/_/{entry['domain']}/icon.png' />"

for category, entries in data.items():
    title = category.replace("_", " ").title() + 's' 
    if category == 'appdaemon':
        title = 'AppDaemon Apps'
    elif category == 'netdaemon':
        title = 'NetDaemon Apps'
    elif category == 'plugin':
        title = 'Dashboard Plugins'

    os.makedirs(f"documentation/repositories/{category}", exist_ok=True)

    BASE += f"\n## {title}\n\n"
    BASE += f"_{len(entries)} Repositories in total._\n\n"
    for entry in sorted(entries, key=lambda entry: entry["full_name"].lower()):
        repository_id = entry['full_name'].replace("/", "_").replace("-", "_").lower()

        BASE += f"<li><a href='/docs/repositories/{entry['category']}/{repository_id}'>{entry['full_name']}</a></li>\n"

        repository_manifest = entry.get("repository_manifest", {})
        name = repository_manifest.get("name") or entry['name'] or entry['full_name']
        if repository_manifest.get("country"):
            name = entry['name'] or entry['full_name']
        description = ""
        try:
            description = entry['description'].encode(encoding='utf-8').decode('ascii').replace('"', "'")
        except:
            pass

        REPOSITORY_CONTENT = REPOSITORY_BASE.format(id=repository_id, name=name, description=description)
        REPOSITORY_CONTENT += f"<div style={{{{display: 'flex', marginBottom: 4, alignItems: 'center'}}}}>\n {gen_brands_icon(entry)} \n<i>{description}</i>\n</div>\n"
        REPOSITORY_CONTENT += gen_authors(entry["authors"] or [entry['full_name'].split("/")[0]])
        REPOSITORY_CONTENT += f"<p style={{{{marginBottom: 0}}}}>\nRepository: <a href='https://github.com/{entry['full_name']}' target='_blank'>{entry['full_name']}</a>\n</p>\n"
        if entry["topics"]:
            REPOSITORY_CONTENT += f"<p>Topics: \n{''.join(f'<li style={{{{marginLeft: 24}}}}>{topic}</li>' for topic in entry['topics'])}</p>\n"


        REPOSITORY_CONTENT += NOTES.get(category)

        with open(f"documentation/repositories/{entry['category']}/{repository_id}.md", "w") as mdfile:
            mdfile.write(REPOSITORY_CONTENT)

BASE += "<sub>The content here is updated on each build of this site, so some date might be missing or outdated.</sub>"
with open("documentation/default_repositories.md", "w") as mdfile:
    mdfile.write(BASE)

