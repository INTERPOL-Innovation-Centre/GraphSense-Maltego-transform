# GraphSense Maltego Transform
This tranform provided by our Swiss colleagues aims at querying GraphSense data directly in Maltego.<br>
We have chosen to restrict this repository to LEAs.<br>
The tranform enables simple queries on GraphSense data and tag-packs to obtain transaction graphs in Maltego.<br>
Graphsense works for BCT, BCH, LTC and DASH.<br>
## Author
Vincent Graber
[github/grarbervi](https://github.com/grabervi)
## Disclaimer
Please do not share outside LEA circles, this is [TLP:AMBER]

## Installation

Works with Python3

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required python librairies.

Microsoft Visual C++ 14.0 is required to install [maltego-trx](https://github.com/paterva/maltego-trx)

```bash
pip install maltego-trx
pip install requests
```

## Config

You need to provide your token from the GraphSense API in the config.json file:

- `token`: *12345*
- `api`: https://api.graphsense.info
- `currency`: btc

## Local Run

To run a local transform, you will need to pass the following arguments:

``` bash
project.py local graphsense BTCAddress
```

## Maltego Local Transform Installation

You need to install the `Blockchain.info (Bitcoin) by Paterva` from the Maltego Transform Hub to work with Bitcoin Address Entity

Go to the Transforms Tab and add a New Local Transform.

Choose `Bitcoin Address [maltego.BTCAddress]` in the `Input entity type`.

In the command path, you need to provide the path to your python3 executable.
Should be *C:\Users\Unicorn\AppData\Local\Programs\Python\Python37\python.exe* by default on Windows 10

In Parameters box put `project.py local graphsense` as it is our entry script.

Put the path of this project as the `Working directory`

Finish

You can now use it in a Maltego Graph.