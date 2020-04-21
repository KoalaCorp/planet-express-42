# planet-Express-42

planet-express-42 is the NLP module of Planet express project, It's works
with python, nltk, rabbitmq and mongodb.

## Installation

We install the python libraries from requiriments.txt with pip, we use python3
```bash
pip install -r requirements.txt
```

For development purposes you can use [koalacorp/planet-express-charts](https://github.com/KoalaCorp/planet-express-charts)


## Usage

To read messages from a rabbitmq queue we need to run a worker.
```python
cd src && python worker.py bocce
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
