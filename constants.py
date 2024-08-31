
import keyring

BUILDING_TECH = [
    {"school": "AUX", "email": "asyed@min201.org"},
    {"school": "JES", "email": "bthornton@min201.org"},
    {"school": "MES", "email": "ahuffman@min201.org"},
    {"school": "MIS", "email": "jprusinski@min201.org"},
    {"school": "MJHS", "email": "jlyon@min201.org"},
    {"school": "MPC", "email": "dplaskett@min201.org"},
    {"school": "WT", "email": "smayper@min201.org"},
]

SHEET_ID = "19ykUZq9igAaBALvKHUX5Nrr-RMCcGVa7b_9mh2VqCT4"

PS_ADMIN_URL = "https://min201.powerschool.com/admin/home.html"
PS_PARENT_URL = "https://min201.powerschool.com/public"

PS_ADMIN_USERNAME = "201apps"
PS_ADMIN_PASSWORD = keyring.get_password("psadmin", PS_ADMIN_USERNAME)

DEFAULT_PASSWORD = "minooka201"
