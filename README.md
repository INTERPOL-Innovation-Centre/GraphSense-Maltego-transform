# GraphSense Maltego Transform
This tranform provided by our Swiss colleagues aims at querying GraphSense data directly in Maltego.<br>
We have chosen to restrict this repository to LEAs.<br>
The tranform enables simple queries on GraphSense data and tag-packs to obtain transaction graphs in Maltego.<br>
Graphsense works for BTC, BCH, LTC and DASH. This transform is only for BTC for now.<br>

![Alt text](Maltego%20BTC%20to%20GraphSense%20Tags.png?raw=true "Maltego BTC GraphSense Tag") <br>
Illustration image from Maltego<br>

## Author
Vincent Graber
[github/grarbervi](https://github.com/grabervi)
## Disclaimer
Please do not share outside LEA circles, this is [TLP:AMBER]

## Prerequisit

Works with Python3

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required python librairies.

Microsoft Visual C++ 14.0 is required to install [maltego-trx](https://github.com/paterva/maltego-trx)

```bash
pip install maltego-trx
pip install requests
```

## Configuration

You need to provide your own token from the GraphSense API.<br>
Simply edit the *config.json* file to add your own API Token:

- `token`: *12345*
- `api`: https://api.graphsense.info
- `currency`: btc

## Installation of the required transforms inside Maltego

In Maltego, install the *Blockchain.info (Bitcoin) by Paterva* from the Maltego Transform Hub to work with Bitcoin Address Entities.

In the *Transforms Tab* or in *Transforms manager*, add a *New Local Transform*.

In the *Input entity type*, choose:
```Bitcoin Address [maltego.BTCAddress]```

In the *Command line* box, provide the path to your python3 executable:<br>
- ```C:\Users\Unicorn\AppData\Local\Programs\Python\Python37\python.exe``` by default for Windows 10. Check one your own machine for the exact path.<br>
- ```python3``` by default for Mac OS X. (See "troubleshooting on Mac" below if you experience problems).

In the *Command parameters* box, type:<br>
```project.py local graphsense```

In the *Working directory* box, insert the full path to the folder where you have cloned this project.

-- Done ! --

You can now use this transform in a Maltego Graph starting from a BTC address.

Troubleshooting for Mac<br>
On Mac OS X it is important to check that the above pip is installing the modules in the same python3 as Maltego expects. To check which Python Maltego is effectively using, set the tranform with the `Command line` box as `which` and the `Command parameters` box as `python3`. Run the transform once and look for the result in debug output box. This will give you the path to the python version used. It needs to be the same as the pip used above (check by runing ```pip -V``` in terminal).
