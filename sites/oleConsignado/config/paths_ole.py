import os
from pathlib import Path

from sites.oleConsignado.cookies import COOKIES_PATH

PATH_ID_4 = str(Path(COOKIES_PATH + "/cookies-id4.pkl"))
PATH_ID_REFIN = str(Path(COOKIES_PATH + "/cookies-id-refin.pkl"))
PATH_COOKIES_JSON = str(Path(COOKIES_PATH + "/cookies-ole-json.json"))

PATH_ID_4_2 = str(Path(COOKIES_PATH + "/cookies-id4_2.pkl"))
PATH_COOKIES_JSON_2 = str(Path(COOKIES_PATH + "/cookies-ole-json_2.json"))
print(PATH_ID_4)