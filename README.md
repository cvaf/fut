# FUT 21

Scraping player attributes and prices:

```bash
(fut) $ python run.py --help
  --update        Download new player data and refresh prices
  --game INTEGER  Game to fetch data for. One of (19, 20, 21)
  --log TEXT      Logging verbosity level.
  --help          Show this message and exit.
```

Currently in the process of refactoring the previous scraper + model. 

###  TO-DO:

- [x] Add hooks.
- [x] Refactor scraping.
- [ ] Refactor training.
- [ ] Tune.