# CoAP-Pub-Sub
Repository for the CoAP publish-subscribe project for Polimi thesis

## Installation
Please use python version 3.6.9

Install all the requirements in a virtual environment by:

```bash
python3 -m venv /path/to/virtual/env 
source /path/to/virtual/env/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage
To run the broker instantiate it and call the start method or run the script with:
```bash
python3 broker/broker.py
```
To run the client instantiate a PSClient object from Client/PSClient.py and call the methods to perform the requests.
An example script is contained in testClient.py 
