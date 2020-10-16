from sqlalchemy import create_engine
import logging
from datetime import datetime

con = create_engine('sqlite:///data/fifa.db', echo=False)

def setup_logger(log) -> None:
    logging.basicConfig(
        filename=f"logs/{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.log",
        filemode='w', 
        level=getattr(logging, log.upper()), 
        datefmt='%H:%M:%S', 
        format='%(asctime)s - %(levelname)s: %(message)s')


def parse_html_table(table) -> list:
    data = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append(''.join([ele for ele in cols if ele]))
    return data


def years_since(date: str) -> int:
    """Number of years between argument and current date"""
    delta = datetime.now() - datetime.strptime(date, '%d-%m-%Y')
    return int(delta.days / 365)