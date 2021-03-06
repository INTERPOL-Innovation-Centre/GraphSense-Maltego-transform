"""
    GraphSense API

    GraphSense API  # noqa: E501

    The version of the OpenAPI document: 0.5.1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from graphsense.api_client import ApiClient, Endpoint as _Endpoint
from graphsense.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from graphsense.model.tx import Tx
from graphsense.model.tx_values import TxValues


class TxsApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        def __get_tx(
            self,
            currency,
            tx_hash,
            **kwargs
        ):
            """Returns details of a specific transaction identified by its hash.  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.get_tx(currency, tx_hash, async_req=True)
            >>> result = thread.get()

            Args:
                currency (str): The cryptocurrency code (e.g., btc)
                tx_hash (str): The transaction hash

            Keyword Args:
                include_io (bool): Whether to include inputs/outputs of a transaction (UTXO only). [optional] if omitted the server will use the default value of False
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                Tx
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['currency'] = \
                currency
            kwargs['tx_hash'] = \
                tx_hash
            return self.call_with_http_info(**kwargs)

        self.get_tx = _Endpoint(
            settings={
                'response_type': (Tx,),
                'auth': [
                    'api_key'
                ],
                'endpoint_path': '/{currency}/txs/{tx_hash}',
                'operation_id': 'get_tx',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'currency',
                    'tx_hash',
                    'include_io',
                ],
                'required': [
                    'currency',
                    'tx_hash',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'currency':
                        (str,),
                    'tx_hash':
                        (str,),
                    'include_io':
                        (bool,),
                },
                'attribute_map': {
                    'currency': 'currency',
                    'tx_hash': 'tx_hash',
                    'include_io': 'include_io',
                },
                'location_map': {
                    'currency': 'path',
                    'tx_hash': 'path',
                    'include_io': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__get_tx
        )

        def __get_tx_io(
            self,
            currency,
            tx_hash,
            io,
            **kwargs
        ):
            """Returns input/output values of a specific transaction identified by its hash.  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.get_tx_io(currency, tx_hash, io, async_req=True)
            >>> result = thread.get()

            Args:
                currency (str): The cryptocurrency code (e.g., btc)
                tx_hash (str): The transaction hash
                io (str): Input or outpus values of a transaction

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                TxValues
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['currency'] = \
                currency
            kwargs['tx_hash'] = \
                tx_hash
            kwargs['io'] = \
                io
            return self.call_with_http_info(**kwargs)

        self.get_tx_io = _Endpoint(
            settings={
                'response_type': (TxValues,),
                'auth': [
                    'api_key'
                ],
                'endpoint_path': '/{currency}/txs/{tx_hash}/{io}',
                'operation_id': 'get_tx_io',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'currency',
                    'tx_hash',
                    'io',
                ],
                'required': [
                    'currency',
                    'tx_hash',
                    'io',
                ],
                'nullable': [
                ],
                'enum': [
                    'io',
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                    ('io',): {

                        "INPUTS": "inputs",
                        "OUTPUTS": "outputs"
                    },
                },
                'openapi_types': {
                    'currency':
                        (str,),
                    'tx_hash':
                        (str,),
                    'io':
                        (str,),
                },
                'attribute_map': {
                    'currency': 'currency',
                    'tx_hash': 'tx_hash',
                    'io': 'io',
                },
                'location_map': {
                    'currency': 'path',
                    'tx_hash': 'path',
                    'io': 'path',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__get_tx_io
        )
