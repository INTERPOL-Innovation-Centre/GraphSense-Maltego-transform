from maltego_trx.entities import Phrase

from maltego_trx.maltego import UIM_PARTIAL, UIM_FATAL
from maltego_trx.transform import DiscoverableTransform
import sys
import requests
import re as regex
import json


class GraphSense(DiscoverableTransform):
    """
    Lookup the name associated with a Virtual Asset address.
    """

    @classmethod
    def create_entities(cls, request, response):
        virtual_asset_address = request.Value.strip()
        try:
            graphsense_tag = cls.get_details(virtual_asset_address)
            if graphsense_tag:
                if "error" in graphsense_tag:
                    response.addUIMessage(graphsense_tag["error"]["message"], messageType=UIM_FATAL)
                # Create new entity for each tag we found
                # If we have the same tag multiple times, Maltego will merge them automatically
                for tag in graphsense_tag:
                    if "label" in tag:
                        entity = response.addEntity(Phrase, tag["label"])
                        entity.setLinkLabel("To tags [GraphSense] (" + tag["currency"] + ")")
                        entity.setType("maltego.CryptocurrencyOwner")
                        if "category" in tag:
                            entity.addProperty("OwnerType", "loose", tag["category"])
                        
                        entity_note = ""
                        if "source" in tag:
                            entity_note += "Source : " + tag["source"] + "\n"
                        if "abuse" in tag:
                            entity_note += "Abuse : " + tag["abuse"]
                        if entity_note:
                            entity.setNote(entity_note)
            else:
                response.addUIMessage("The Virtual Asset address was not found")
        except Exception as e:
            print(e)
            response.addUIMessage("An error occurred", messageType=UIM_PARTIAL)

    @staticmethod
    def load_config():
        with open("config.json") as json_data_file:
            config = json.load(json_data_file)
        return config

    @staticmethod
    def get_details(virtual_asset_address):
        config = GraphSense.load_config()
        if "token" not in config or "api" not in config:
            return {"error": {"message":"Can not load data from config.json file"}}
        if config["token"] == "YOUR TOKEN":
            return {"error": {"message":"No GraphSense token have been set in the config.json file"}}

        virtual_asset_tags = []
        currencies = []
        #supported_currencies are "btc", "bch", "ltc", "zec", "eth" (note: a BTC address could also be a bch address)
        virtual_asset_match = regex.search(r"\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})|bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})\b", virtual_asset_address)
        if virtual_asset_match:
            currencies.append("btc")
        virtual_asset_match = regex.search(r"\b((?:bitcoincash|bchtest):)?([0-9a-zA-Z]{34})\b", virtual_asset_address)
        if virtual_asset_match:
            currencies.append("bch")
        virtual_asset_match = regex.search(r"\b[LM3][a-km-zA-HJ-NP-Z1-9]{25,33}\b", virtual_asset_address)
        if virtual_asset_match:
            currencies.append("ltc")
        virtual_asset_match = regex.search(r"\b[tz][13][a-km-zA-HJ-NP-Z1-9]{33}\b", virtual_asset_address)
        if virtual_asset_match:
            currencies.append("zec")
        virtual_asset_match = regex.search(r"\b(0x)?[0-9a-fA-F]{40}\b", virtual_asset_address)
        if virtual_asset_match:
            currencies.append("eth")

        for currency in currencies:
            try:
                req = requests.get(f"{config['api']}/{currency}/addresses/{virtual_asset_address}/tags", headers={'Authorization': config["token"]})
                tags = req.json()
                #print ("Req for ",currency," is = ",req)
                #print ("Tags for ",currency," is = ",tags)
                if not ('address_tags' in tags) : #if there is no tag at the address level, we look for tags at the entity level (level=entity)
                    #virtual_asset_tags += tags['address_tags']
                    req = requests.get(f"{config['api']}/{currency}/addresses/{virtual_asset_address}/entity", headers={'Authorization': config["token"]})
                    virtual_asset_entity = req.json()
                    if 'entity' in virtual_asset_entity:
                        #print("search for tags in entity",config['api'],"/",currency,"/","entities","/",virtual_asset_entity['entity'])
                        req = requests.get(f"{config['api']}/{currency}/entities/{virtual_asset_entity['entity']}/tags", headers={'Authorization': config["token"]}, params={'level':"entity"})
                        tags = req.json()
                        #print ("Entity Tags for ",currency," is = ",tags)
                        if 'entity_tags' in tags:
                            virtual_asset_tags += tags['entity_tags']
                else:
                    virtual_asset_tags += tags['address_tags']
                    
            except Exception as e:
                print(e)
        return virtual_asset_tags


if __name__ == "__main__":
    GraphSense.get_details(sys.argv[1])
