# GraphSense Maltego Transform
This tranform set for GraphSense is from an original idea of our Swiss colleagues and aims at querying GraphSense data directly in Maltego.  
We have chosen to restrict this repository to LEAs only.  
The tranforms enable simple queries on GraphSense data and tag-packs to obtain transaction graphs and attribution tags in Maltego.  
Graphsense and this transform set work for BTC, BCH, LTC, ZEC and ETH.  

![A screen copy of the transform result in Maltego](Maltego%20BTC%20to%20GraphSense%20Tags.png?raw=true "Maltego BTC GraphSense Tag")  
Illustration image from Maltego  

## Authors
Vincent Graber  
[github/grarbervi](https://github.com/grabervi)  
Vincent Danjean  
[github/VinceICPO](https://github.com/vinceicpo)  

## Disclaimer
Please do not share outside LEA circles, this is [TLP:AMBER]  
This set of tools is provided as-is with no guaranty of accuracy.  

## Prerequisite

Works with Python3  

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the below required python librairies.  

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

1/ In the *Transforms Tab* or in *Transforms manager*, add a *New Local Transform*.  

2/ Fill-in the required fields:  
In the *Display Name* box, enter:
```To tags [Graphsense]```  
In the *Transform ID* box, enter:  
```graphsense.ToTags```, no space, no special characters here.  
In the *Author* box, enter:  
```Interpol Innovation Centre```
In the *Input entity type* box, choose:  
```Unknown [maltego.Unknown]```  
Click on *Next>*  

3/ In the *Command line* box, provide the path to your python3 executable:  
- ```C:\Users\Unicorn\AppData\Local\Programs\Python\Python37\python.exe``` by default for Windows 10. Check on your own machine for the exact path.  
- ```python3``` by default for Mac OS X. (See "*Troubleshooting for Mac*" below if you experience problems).  

4/ In the *Command parameters* box, type:  
```project.py local totags```
"totags" is one of the transforms available. Please see 6/ below.  

5/ In the *Working directory* box, insert the full path to the folder where you have cloned this project.  

6/ You need to repeat 1/ to 5/ above for each of the transforms contained in this set:
- To Details (project.py local todetails)
- To Cluster (project.py local tocluster)

7/ Import the GraphSense Entities:  
For this, go to *Entities* tab, click on *Import Entities*  
Browse to and select the "Graphsense Entities.mtz" file. Click *Next>*  
Tick both the *Entities* and the *Icons* boxes to import everything. Click *Next>*  
Click *Finish*

-- Done ! --

You can now use these transforms in a Maltego Graph starting from any supported cryptocurrency address or cluster (BTC, BCH, LTC or ZEC).  
## Hints
Please note that when running on an unknown cryptocurrency address (one that is not BTC), our transforms will use find what cryptocurrency this address can be and will create the corresponding entity.  
I.e.: if an address is both a BTC and BCH address, our transform will create both entities.  

When querying the details, the transfrom will add many properties to the entity, including the first and last transaction dates and a *businessman icon* in the top left corner to indicate that there are known GraphSense tags on this entity.  

There is at least *one limitation* to the current way to display the attribution Tags and the addresses linked:  
Only one tag is shown in Maltego but this tag can actually belong to several different addresses in one cluster or even in several currencies. The list of addresses is not shown yet only the last address queried is shown.  
Make sure you understand this limitation prior to drawing conclusions.  

## Contribute
You may help us develop this tool.  
The current local transform is possible thanks to the use of [paterva/maltego-trx](https://github.com/paterva/maltego-trx).  
It support a few entities but is very flexible in adding custom properties. Refer to the details of [supported entities](https://github.com/paterva/maltego-trx/blob/master/maltego_trx/entities.py).  
The results displayed are from queries to [GraphSense OpenAPI](https://github.com/graphsense/graphsense-openapi/blob/master/graphsense.yaml).  
Feel free to open an [Issue or improvement request](https://github.com/INTERPOL-Innovation-Centre/GraphSense-Maltego-transform/issues).  
The developement is done in the [Dev branch](https://github.com/INTERPOL-Innovation-Centre/GraphSense-Maltego-transform/tree/Dev).  


##
*Troubleshooting for Mac*  
On Mac OS X it is important to check that the above pip is installing the modules in the same python3 as Maltego expects.  

To check which Python Maltego is effectively using, set the tranform with the `Command line` box as `which` and the `Command parameters` box as `python3`.  
Run the transform once and look for the result in debug output box.  
This will give you the path to the python version used by the Maltego app.  
It needs to be the same path as the pip used above (check by runing ```pip -V``` in terminal).  
If it isn't, try with pip3 instead of pip. You may need to reinstall the Prerequisite above once this pip vs python path is fixed.
