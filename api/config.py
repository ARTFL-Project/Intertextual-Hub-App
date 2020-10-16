import rapidjson

with open("../config/appConfig.json") as app_config:
    APP_CONFIG = rapidjson.load(app_config)
with open("../config/db_config.json") as db_config:
    DB_CONFIG = rapidjson.load(db_config)
    PHILO_PATHS = {db_name: db["path"] for db_name, db in DB_CONFIG["philo_dbs"].items()}
    PHILO_URLS = {dbname: values["url"] for dbname, values in DB_CONFIG["philo_dbs"].items()}
