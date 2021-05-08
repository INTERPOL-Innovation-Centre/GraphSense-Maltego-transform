# GraphSense Maltego Transform
This tranform provided by our Swiss colleagues aims at querying GraphSense data directly in Maltego.  
We have chosen to restrict this repository to LEAs.  
The tranform enables simple queries on GraphSense data and tag-packs to obtain transaction graphs in Maltego.  
Graphsense and this transform works for BTC, BCH, LTC, ZEC and ETH.

![A screen copy of the transform result in Maltego](Maltego%20BTC%20to%20GraphSense%20Tags.png?raw=true "Maltego BTC GraphSense Tag")  
Illustration image from Maltego  

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

You need to provide your own token from the GraphSense API.  
Simply edit the *config.json* file to add your own API Token:

- `token`: *12345*
- `api`: https://api.graphsense.info

## Installation of the required transforms inside Maltego

In Maltego, install the *Blockchain.info (Bitcoin) by Paterva* from the Maltego Transform Hub to work with Bitcoin Address Entities.

In the *Transforms Tab* or in *Transforms manager*, add a *New Local Transform*.

In the *Input entity type*, choose:
```Bitcoin Address [maltego.BTCAddress]```

In the *Command line* box, provide the path to your python3 executable:  
- ```C:\Users\Unicorn\AppData\Local\Programs\Python\Python37\python.exe``` by default for Windows 10. Check one your own machine for the exact path.  
- ```python3``` by default for Mac OS X. (See "*Troubleshooting for Mac*" below if you experience problems).

In the *Command parameters* box, type:  
```project.py local graphsense```

In the *Working directory* box, insert the full path to the folder where you have cloned this project.

-- Done ! --

You can now use this transform in a Maltego Graph starting from a BTC address.

## Contribute
You may help us develop this tool.
The current local transform is possible thanks to the use of [paterva/maltego-trx](https://github.com/paterva/maltego-trx).  
It support a few entities but is very flexible in adding custom properties. Refer to the details of [supported entities](https://github.com/paterva/maltego-trx/blob/master/maltego_trx/entities.py).  
The results displayed are from queries to [GraphSense OpenAPI](https://github.com/graphsense/graphsense-openapi/blob/master/graphsense.yaml).
Feel free to open an [Issue or improvement request](https://github.com/INTERPOL-Innovation-Centre/GraphSense-Maltego-transform/issues).  
The developement is done in the [Dev branch](https://github.com/INTERPOL-Innovation-Centre/GraphSense-Maltego-transform/tree/Dev).


##
*Troubleshooting for Mac*  
On Mac OS X it is important to check that the above pip is installing the modules in the same python3 as Maltego expects. To check which Python Maltego is effectively using, set the tranform with the `Command line` box as `which` and the `Command parameters` box as `python3`. Run the transform once and look for the result in debug output box. This will give you the path to the python version used. It needs to be the same as the pip used above (check by runing ```pip -V``` in terminal).
