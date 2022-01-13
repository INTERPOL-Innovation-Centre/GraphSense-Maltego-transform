from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import create_entity_with_details, get_currency, get_address_details, get_entity_details

@registry.register_transform(
	display_name='To Details',
	input_entity='maltego.Cryptocurrency',
	description='Returns details of a cryptocurerncy address.',
	output_entities=['maltego.Cryptocurrency']
)

class ToDetails(DiscoverableTransform):
	"""
	Lookup for all details associated with a Virtual Asset (balance, total in and out, date last and first Tx...)
	"""
	
	@classmethod
	def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
		
		query_type = "details"

		entity_details = request.Properties
		if 'cryptocurrency.wallet.name' in entity_details: # this means the source entity is a cluster (Wallet) and not a cryptocurrency address
			address = entity_details['cryptocurrency.wallet.name']
			currency = entity_details['currency']
			results = get_entity_details(currency,int(address))
			#currency = "cluster"
			entity = create_entity_with_details(results,currency,query_type,response)
			if entity != "" :
				#print(entity)
				return entity
		else: # this means the source entity is a cryptocurrency address
			if 'properties.cryptocurrencyaddress' in entity_details: 
				address = entity_details['properties.cryptocurrencyaddress']
			else:
				address = entity_details['address']
			if address[:2] == "bc": #beech32 BTC addresses include "bc" at the begining, we want to remove that.
				address = address[2:]
				currencies = ["btc"] #we know this is BTC, no need to check for BCH or other currencies.
			else :
				currencies = get_currency(address)
			
			for currency in currencies:
				results = get_address_details(currency,address)
				entity = create_entity_with_details(results,currency,query_type,response)
				if entity != "" :
					#print(entity)
					return entity

if __name__ == "__main__":
    create_entities(sys.argv[1])