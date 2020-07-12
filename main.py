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

dir_ulauncher = "0K"
file_infojson = "mal.json"


class ProlarExtension(Extension):
    def __init__(self):
        super(ProlarExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # Sorgu varsa, girilen yazıyı getir
        query = event.get_argument() or str()
        
        # Uzantı Ayarlarda belirtilen Yolu (~/Prolar) getir
        path = extension.preferences["path"].replace("~",os.environ['HOME'])
        
        # Uygulamaları burada biriktir
        apps = {}
        
        # Prolar Klasörünü listele
        for i in os.listdir(path):

            fullpath = os.path.join(path, i)
            if not os.path.isdir(fullpath): continue

            ulhrpath = os.path.join(fullpath, dir_ulauncher)
            if not os.path.exists(ulhrpath): continue

            infopath = os.path.join(ulhrpath, file_infojson)

            if not os.path.exists(infopath): continue
            
            try:
                # mal.json dosyası varsa, bu bir uygulama klasörüdür.
                with open(infopath) as json_file:
                    data = json.load(json_file)
                    if "aplist" in data.keys():
                        for ic_data in data.get("aplist"):
                            ic_data["patika"] = os.path.join(fullpath, ic_data.get("patika"))
                            if "simge" not in ic_data.keys():
                                ic_data["simge"] = os.path.join(ulhrpath, "simge.png")
                            else:
                                ic_data["simge"] = os.path.join(ulhrpath, ic_data.get("simge"))
                        
                            apps[ic_data["baslik"]] = ic_data.copy()
                    else:
                        data["patika"] = os.path.join(fullpath, data.get("patika"))
                        data["simge"] = os.path.join(ulhrpath, "simge.png")
                        apps[data["baslik"]] = data
            except:
                continue
                
        query_apps = []
        for i in apps.keys():
            if len(query_apps) >= int(extension.preferences["count"]): break
            re1 = ""
            for t in query.lower():
                if t in [" ", "\n", "\t"]:
                    re1 +=  ".*"
                    continue
                re1 += t + "+.?" 
            re2 = apps[i]["baslik"].lower() + apps[i]["etiket"].lower()
            if len(query) > 0 and not re.search(re1, re2): continue
            print(apps[i]["patika"])
            query_apps.append(apps[i])

        items = [ExtensionResultItem(icon=i["simge"],
                                     name=i["baslik"],
                                     description=i["anlati"],
                                     on_enter=RunScriptAction(i["patika"]) #OpenAction()  # if f_name != "Blender" else RunScriptAction
                                     )
                 for i in query_apps
                 ]
        return RenderResultListAction(items)


if __name__ == '__main__':
    ProlarExtension().run()
