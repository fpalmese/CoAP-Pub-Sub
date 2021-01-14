# CoAP-Pub-Sub
Repository for the CoAP publish-subscribe project for Polimi thesis

## Installation
Please use Python version 3.6.9

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

## Used files
The following files and directories are important for the execution, others not cited down here have been used for testing:
-  /lib directory
- /broker directory
- /Client directory

multi_publisher.py and subscriber.py are the two scripts used to execute publishers and subscribers in the simulations
/Client/PSClientTesting.py and /broker/brokerTesting.py contain modified version of the broker and client used for testing.

