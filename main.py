import os
import re
import json
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

dir_ulauncher = "UlauncherFiles"
file_infojson = "info.json"


class ProlarExtension(Extension):
    def __init__(self):
        super(ProlarExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or str()

        path = extension.preferences["path"].replace("~",os.environ['HOME'])

        apps = {}

        for i in os.listdir(path):
            fullpath = os.path.join(path, i)
            if not os.path.isdir(fullpath): continue

            ulhrpath = os.path.join(fullpath, dir_ulauncher)
            if not os.path.exists(ulhrpath): continue

            infopath = os.path.join(ulhrpath, file_infojson)
            if not os.path.exists(infopath): continue

            with open(infopath) as json_file:
                data = json.load(json_file)
                data["path"] = os.path.join(fullpath, data.get("path"))
                data["icon"] = os.path.join(ulhrpath, "icon.png")
                apps[data["name"]] = data

        query_apps = []
        for i in apps.keys():
            if len(query_apps) >= int(extension.preferences["count"]): break
            re1 = ""
            for t in query.lower():
                if t in [" ", "\n", "\t"]:
                    re1 +=  ".*"
                    continue
                re1 += t + "+.?" 
            re2 = apps[i]["name"].lower() + apps[i]["labl"].lower()
            if len(query) > 0 and not re.search(re1, re2): continue
            print( apps[i]["path"])
            query_apps.append(apps[i])

        items = [ExtensionResultItem(icon=i["icon"],
                                     name=i["name"],
                                     description=i["desc"],
                                     on_enter=RunScriptAction(i["path"]) #OpenAction()  # if f_name != "Blender" else RunScriptAction
                                     )
                 for i in query_apps
                 ]
        return RenderResultListAction(items)


if __name__ == '__main__':
    ProlarExtension().run()
