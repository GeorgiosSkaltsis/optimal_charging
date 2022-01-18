import configparser 
import os

config = configparser.ConfigParser()
package_dir = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()

if os.getenv('CONFIG_PATH') is None:
    config.read(os.path.join(package_dir, 'config.ini'))
else:
    config.read(os.path.join(package_dir, os.getenv('CONFIG_PATH')))
# import ipdb; ipdb.set_trace()
URI = config.get('db', 'URI')
number_of_prosumers = int(config.get('market', 'number_of_prosumers'))
random_parameter_is = int(config.get('market', 'random_parameter'))
power_to_energy_conversion_ratio = float(config.get('market', 'power_to_energy_conversion_ratio'))
time_resolution = int(config.get('market', 'time_resolution'))
