from pathlib import Path
from time import sleep
import pdb

from PATHS import ROOT_DIR
from selenium.webdriver import Chrome
from sites.core.selenium_actions import SeleniumActions


class FileHandler:
    def __init__(self, path, **kwargs):
        self._path: Path = Path(ROOT_DIR + path)
        self._name: str = self._path.name
        self._extension: str =  self._path.suffix
        self._parents = self._path.parent
        self.src: str = kwargs.get("src")

    @property
    def path(self):
        return str(self._path)

    @path.setter
    def path(self, *parts: str):
        self._path = Path(ROOT_DIR, *parts)

    @property
    def exists(self):
        return self._path.exists()

    def downloadFromWebDriver(self, driver: Chrome, retries=16):
        driver.get(self.src)
        try:
            sleep(3)
            if('500' in SeleniumActions(driver).obter_texto('body > table:nth-child(1) > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > font')):
                return False
        except:
            pass

        for _ in range(retries):
            driver.refresh()
            print('Entrou nas tentativas...')
            sleep(2)
            if self.exists:
                return

        return False
        #raise DownloadFailedException(name=self.path, src=self.src)

    def rename(self, newName, retries=16):
        target = Path(self._parents / newName)

        for i in range(retries):
            sleep(3)
            if target.exists():
                print("NEW PATH pre:",  self._path)
                self.safeRemove(self._path)
                self._path = Path(target)
                print("NEW PATH:",  self._path)
                return

            self._path.rename(target)

        raise CouldntRenameFileException(self.path, newName)

    def remove(self, retries=16):
        for _ in range(retries):
            if self.exists:
                self._path.unlink()
            else:
                return

    @staticmethod
    def safeRemove(filePath: Path, VERBOSE=False) -> bool:
        try:
            filePath.unlink()
            return True
        except Exception as e:
            if VERBOSE:
                print(f"FileHandler:[{e}]")
            return False

    def encodeToBase64(self):
        import base64

        file = open(self.path, 'rb')
        file_base_64 = base64.encodebytes(file.read())
        file.close()
        return file_base_64

    def __repr__(self):
        return f"FileHandler(path={self._path})"


class DownloadFailedException(Exception):
    def __init__(self, name, src):
        self.msg = f"Arquivo ({name} não pôde ser baixado na fonte {src})"

    def __repr__(self):
        return self.msg


class CouldntRenameFileException(Exception):
    def __init__(self, name, newName):
        self.msg = f"Arquivo ({name} não pôde ser renomeado para {newName})"

    def __repr__(self):
        return self.msg
