from pathlib import Path

from PATHS import project_path

PREFS = {"download.default_directory": str(Path(project_path() + "/ibConsig/anexos/contratos")),
         "download.prompt_for_download": False,
         "plugins.always_open_pdf_externally": True}
