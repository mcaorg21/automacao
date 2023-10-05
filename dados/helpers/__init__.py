from PATHS import ROOT_DIR

path = f"{ROOT_DIR}/dados/database/db_conf/db_data/data.dat"


def open_data(data: str) -> str:
    with open(path, mode="r") as dObj:
        for line in dObj:
            key, val = line.replace("Â", "").replace("\n", "").split(":")
            if data == key:
                return val


def retrieve_data(data: str):
    data = open_data(data)
    dehash = ""
    for cnt, ch in enumerate(data.split("¢"), 2):
        if ch == '' or ch == "":
            continue
        dehash += chr(int(ch) - cnt)

    return dehash