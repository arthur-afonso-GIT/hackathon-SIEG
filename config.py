import os
import re

TEAM_TOKEN = os.getenv("TEAM_TOKEN", "AVENGERS-UR88")

BASE_URL = "https://talkabit-z3eg.onrender.com"
SUBMIT_URL = f"{BASE_URL}/api/submit"

MAX_SUBMISSION_ATTEMPTS = 10
COOLDOWN_SECONDS = 30 


REGEX_CHAVE = re.compile(r'\b\d{44}\b')

REGEX_VALOR = re.compile(r'(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2}|\d+\.\d{2})')


STATUS_VALIDO = "AUTORIZADA"
STATUS_INVALIDOS = ["CANCELADA", "DENEGADA"]

SELENIUM_TIMEOUT = 15     
DOM_RETRY_ATTEMPTS = 3    
HEADLESS_MODE = False     

BLOCK_TAGS_XPATH = "//div | //tr | //li | //article | //section"

NEXT_PAGE_XPATH = "//a[contains(text(), 'Próxim') or contains(text(), '>')] | //button[contains(text(), 'Próxim')]"
SCROLL_PAUSE_TIME = 1.5   

VERBOSE_LOGS = True       