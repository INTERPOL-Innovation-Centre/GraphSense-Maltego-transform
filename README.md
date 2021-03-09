# GraphSense Maltego Transform
This tranform provided by our Swiss colleagues aims at querying GraphSense data directly in Maltego.<br>
We have chosen to restrict this repository to LEAs.<br>
The tranform enables simple queries on GraphSense data and tag-packs to obtain transaction graphs in Maltego.<br>
Graphsense works for BCT, BCH, LTC and DASH.<br>
## Disclaimer
Please do not share outside LEA circles, this is [TLP:AMBER]<br>
##
### INSTALL
To setup and configure this transform you will need to have a working API Key which you can optain via the Austrian Institute of Technology at [graphsense.info](https://graphsense.info).
We can help you liaise with the team.<br>
--This is work in progress-- We will update this page as we include the transforms python scripts and setup procedure.<br>
```
pip install canari
git clone https://github.com/INTERPOL-Innovation-Centre/GraphSense-Maltego-transform.git
cd GraphSense-Maltego-transform
```
Update the .py to include your own API key.
Line xxx
```
canari create-profile
```
Import ethereum.mtz into maltego

Blockchain.info entities should be installed.