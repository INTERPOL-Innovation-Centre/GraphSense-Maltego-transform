from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform

from extensions import registry

from api.utils import create_entity_with_details, get_currency, get_address_details

@registry.register_transform(
	display_name='To Tags',
	input_entity='maltego.Cryptocurrency',
	description='Returns known attribution tags',
	output_entities=['maltego.Cryptocurrency']
)

class ToTags(DiscoverableTransform):
	"""
	Lookup the attribution tags associated with a Virtual Asset and the entity (cluster) it belongs to.
	"""
	
	@classmethod
	def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
		
		query_type = "tags"

		entity_details = request.Properties
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
			if results:
				entity = create_entity_with_details(results,currency,query_type, response)
				if entity != "" :
					#print(entity)
					return entity

if __name__ == "__main__":
    create_entities(sys.argv[1])