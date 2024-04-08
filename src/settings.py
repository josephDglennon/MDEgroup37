
import os
import yaml


_ABSOLUTE_PATH = os.path.dirname(__file__)
_CONFIG_FILE_LOCATION = os.path.join(_ABSOLUTE_PATH, '../config')
_CONFIG_FILE_PATH = os.path.join(_CONFIG_FILE_LOCATION, 'dmg-config.yaml')


_DEFAULT_SETTINGS = {
    'database_file_name': 'dmg.db',
    'save_location': os.path.join(_ABSOLUTE_PATH, '../dmgdevicestorage'),
    'process_mode': 'ANALYTICAL',
    'trigger_port': 'COM4',
    'trigger_pin': 'a:0:i',
    'audio_device_id': '1',
    'audio_channels': '2'
}


def __init__():
    # create config file with default settings if no config file exists
    if not os.path.isfile(_CONFIG_FILE_PATH):
        try:
            os.makedirs(_CONFIG_FILE_LOCATION)
        except:
            # try to make the dir if it does not exist
            pass

        with open(_CONFIG_FILE_PATH, 'w') as file:

            # save settings
            with open(_CONFIG_FILE_PATH, 'w') as file:
                yaml.dump(_DEFAULT_SETTINGS, file)
__init__()


def get_setting(name: str):
    '''Access the config file on disk and return the current value of the
    specified settings.
    '''

    with open(_CONFIG_FILE_PATH, 'r') as file:
        settings_file = yaml.safe_load(file)
        try:
            return settings_file[name]
        except KeyError:
            return ''


def configure_setting(name: str, value: str):
    '''Access the config file on disk and update the specified setting to
    the specified value. 
    
    If the specified setting does not exist in the config file, it is added.
    '''

    settings_file = None

    # load settings from memory
    with open(_CONFIG_FILE_PATH, 'r') as file:
        settings_file = yaml.safe_load(file)
    
    # edit setting
    settings_file[name] = str(value)

    # save settings
    with open(_CONFIG_FILE_PATH, 'w') as file:
        yaml.dump(settings_file, file)


def _get_settings():
    '''Outputs a dictionary representing the current status of the
    config file.
    '''

    with open(_CONFIG_FILE_PATH, 'r') as file:
        return yaml.safe_load(file)
    

if __name__ == '__main__':

    pass

    