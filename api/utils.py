from maltego_trx.maltego import MaltegoEntity, MaltegoTransform, Phrase
from graphsense.configuration import Configuration

import json

import re as regex

from graphsense.api import addresses_api, entities_api
from graphsense.api_client import ApiClient, ApiException

from datetime import datetime

def open_config():
	try:
		with open("config.json") as json_data_file:
			config = json.load(json_data_file)
		if "token" not in config or "api" not in config:
			print("Error message: Cannot load data from config.json file")
		else:
			configuration = Configuration(
			host = config["api"],
			api_key = {'api_key': config["token"]}
			)
			return configuration
	except Exception as e:
		print("Could not read config.json. Error: " + e)

def get_currency(virtual_asset_address):
	#supported_currencies are "btc"(not!), "bch", "ltc", "zec", "eth" (note: a BTC address could also be a bch address)
	currency = [""]
	virtual_asset_match = regex.search(r"\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})|bc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})\b", virtual_asset_address)
	if virtual_asset_match:
		currency = ["btc"]
	virtual_asset_match = regex.search(r"\b((?:bitcoincash|bchtest):)?([0-9a-zA-Z]{34})\b", virtual_asset_address)
	if virtual_asset_match:
		currency += ["bch"]
	virtual_asset_match = regex.search(r"\b[LM3][a-km-zA-HJ-NP-Z1-9]{25,33}\b", virtual_asset_address)
	if virtual_asset_match:
		currency = ["ltc"]
	virtual_asset_match = regex.search(r"\b[tz][13][a-km-zA-HJ-NP-Z1-9]{33}\b", virtual_asset_address)
	if virtual_asset_match:
		currency = ["zec"]
	virtual_asset_match = regex.search(r"\b(0x)?[0-9a-fA-F]{40}\b", virtual_asset_address)
	if virtual_asset_match:
		currency = ["eth"]
	return currency

def get_address_details(currency, address):
	details = []
	configuration = open_config()

	with ApiClient(configuration) as api_client:
		api_instance = addresses_api.AddressesApi(api_client)
		try:
			# Retrieve the address object
			#print(f"-------------- Address: " + currency + ":" + address+ " --------------")
			address_obj = api_instance.get_address(currency, address, include_tags = True)
			#print(address_obj)
			return address_obj
		except ApiException as e:
			print("Exception when calling AddressesApi: %s\n" % e)

def get_entity_details(currency, entity):
	details = []
	configuration = open_config()

	with ApiClient(configuration) as api_client:
		api_instance = entities_api.EntitiesApi(api_client)
		try:
			entity_obj = api_instance.get_entity(currency, entity, include_tags = True)
			#print(entity_obj)
			return entity_obj
		except ApiException as e:
			print("Exception when calling EntitiesApi: %s\n" % e)

def create_entity_with_details(json_result,currency,query_type,response): # Query_type is one of : "known_entities", "tags", "details", "cluster"

	
	if currency == "btc":
		set_type = "maltego.BTCAddress"
	if currency == "bch":
		set_type = "maltego.BCHAddress"
	if currency == "ltc":
		set_type = "maltego.LTCAddress"
	if currency == "zec":
		set_type = "maltego.CryptocurrencyAddress"
		#set_type = "maltego.ZECAddress"
	if currency == "eth":
		set_type = "maltego.ETHAddress"


	if query_type == "details":
		#if currency == "cluster":
		if not ('address' in json_result): # This means this is a cluster not a cryptocurrency address
			#currency = json_result['tags']['address_tags'][0]['currency']
			set_type = "maltego.CryptocurrencyWallet"
			cluster_ID = json_result['entity'] #the Cluster ID is known as "entity" in GraphSense API json result
			entity = response.addEntity(set_type, cluster_ID)
			json_result = get_entity_details(currency,json_result['entity'])
			entity.addProperty("num_addresses", "Number of addresses", value=json_result['no_addresses'])
		else:
			if 'properties.cryptocurrencyaddress' in json_result:
				address = json_result['properties.cryptocurrencyaddress']
			else:
				address = json_result['address']
			entity = response.addEntity("Cryptocurrency", address)
			entity.addProperty("properties.cryptocurrencyaddress", value=json_result['address'])
		entity.setType(set_type)
		balance_value = json_result['balance']['value']#/100000000 # Satoshis to BTCs 10e-9
		total_received_value = json_result['total_received']['value']#/100000000 # Satoshis to BTCs 10e-9
		total_sent_value = json_result['total_spent']['value']#/100000000 # Satoshis to BTCs 10e-9
		balance_fiat_value = json_result['balance']['fiat_values'][0]['value']
		balance_fiat_currency = json_result['balance']['fiat_values'][0]['code']
		num_transactions = json_result['no_incoming_txs']+json_result['no_outgoing_txs']
		cluster_ID = json_result['entity']
		total_throughput = total_received_value + total_sent_value
		last_tx_datetime = datetime.fromtimestamp(json_result['last_tx']['timestamp'])
		first_tx_datetime = datetime.fromtimestamp(json_result['first_tx']['timestamp'])
		
		entity.addProperty("currency", "Currency", "loose", value=currency)
		entity.addProperty("final_balance", "Final balance (" + currency + ")", "loose", value=balance_value)
		entity.addProperty("final_balance_fiat", "Final balance (" + balance_fiat_currency + ")", "loose", value=balance_fiat_value)
		entity.addProperty("total_throughput", "Total throughput", "loose", value=total_throughput)
		entity.addProperty("total_received", "Total received", "loose", value=total_received_value)
		entity.addProperty("total_sent", "Total sent", value=total_sent_value)
		entity.addProperty("num_transactions","Number of transactions", "loose", value=num_transactions)
		entity.addProperty("num_in_transactions","Number of incoming transactions", "loose", value=json_result['no_incoming_txs'])
		entity.addProperty("num_out_transactions","Number of outgoing transactions", "loose", value=json_result['no_outgoing_txs'])
		entity.addProperty("cluster_ID", "Cluster ID", "loose", value=cluster_ID)
		entity.addProperty("Last_tx", "Last transaction (UTC)", value=last_tx_datetime)
		entity.addProperty("First_tx", "First transaction (UTC)", value=first_tx_datetime)

	if query_type == "cluster":
		set_type = "maltego.CryptocurrencyWallet"
		cluster_ID = json_result['entity'] #the Cluster ID is known as "entity" in GraphSense API json result
		entity = response.addEntity(set_type, cluster_ID)
		json_result = get_entity_details(currency, cluster_ID)
		#print(json_result)
		entity.addProperty("cryptocurrency.wallet.name", "loose", value=cluster_ID)
		entity.addProperty("cluster_ID", "Cluster ID", "loose", value=cluster_ID)
		entity.addProperty("currency","Currency", "loose", value=currency)
		
	if query_type == "known_entities":
		known_neighbors = [el for el in json_result.neighbors if len(el.labels) > 0]
		for neighbor in known_neighbors:
			#print(neighbor)
			#entity = MaltegoEntity()
			neighbor_value = neighbor.labels[0]
			entity = response.addEntity.MaltegoEntity(Phrase, value=neighbor_value)
			entity.setLinkLabel("Tx out to tagged entity: " + neighbor.id +" )[GraphSense]")
			entity.setType(entity_type)
			entity_note = ""


	if query_type == "tags":
		tags = []
		set_type = "maltego.CryptocurrencyOwner"
		#entity.note = ""
		json_result = get_entity_details(currency, json_result['entity']) # We query the entity to get the "Address" and the "Entity" (cluster) tags if any.

		if ('tags' in json_result):
			tags = json_result['tags']
			if ('address_tags' in tags):
				tags = tags['address_tags'] ## MODIFY TO QUERY the entity
				#print ("Address Tags for ",currency," is = ",tags)
			else:
				if ('entity_tags' in tags):
					tags = tags['entity_tags']
					#print ("Entity tags for ",currency," is = ",tags)
				else:
					tags = []

			if tags:
				if "error" in tags:
					response.addUIMessage(graphsense_tag["error"]["message"], messageType=UIM_FATAL)
				# Create new entity for each tag we found
				# If we have the same tag multiple times, Maltego will merge them automatically
				for tag in tags:
					if "label" in tag:
						entity=response.addEntity("Cryptocurrency", tag["label"])
						entity.setLinkLabel("To tags [GraphSense] (" + tag["currency"] + ")")
						entity.setType("maltego.CryptocurrencyOwner")
					if "category" in tag:
						entity.addProperty("OwnerType", "loose", tag["category"])
					entity_note = ""
					if "source" in tag:
						entity.addProperty("Source_URI", "Source", "loose", value=tag["source"])
						uri_link = str('<a href="' + str(tag["source"]) + '">' + str(tag["source"]) + '</a>')
						entity.addDisplayInformation(uri_link,"Source URI")
					if "abuse" in tag:
						entity.addProperty("Abuse_type", "Abuse type", "loose", value=tag["abuse"])
			else:
				response.addUIMessage("No attribution tags found for this address and its cluster")
