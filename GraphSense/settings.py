# settings.py
from maltego_trx.decorator_registry import TransformSetting

api_key_setting = TransformSetting(name='api_key',
                                   display_name='API Key',
                                   setting_type='string',
                                   global_setting=True)
api_url_setting = TransformSetting(name='api_url',
                                   display_name='API Url',
                                   setting_type='url',
                                   global_setting=True)