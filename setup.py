from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt", session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='pogo',
    version='0.0.1',
    packages=[
        'pogo', 'POGOProtos', 'POGOProtos.Map', 'POGOProtos.Map.Fort',
        'POGOProtos.Map.Pokemon', 'POGOProtos.Data', 'POGOProtos.Data.Gym',
        'POGOProtos.Data.Logs', 'POGOProtos.Data.Battle',
        'POGOProtos.Data.Player', 'POGOProtos.Data.Capture',
        'POGOProtos.Enums', 'POGOProtos.Settings',
        'POGOProtos.Settings.Master', 'POGOProtos.Settings.Master.Item',
        'POGOProtos.Settings.Master.Pokemon', 'POGOProtos.Inventory',
        'POGOProtos.Inventory.Item', 'POGOProtos.Networking',
        'POGOProtos.Networking.Requests',
        'POGOProtos.Networking.Requests.Messages',
        'POGOProtos.Networking.Envelopes', 'POGOProtos.Networking.Responses'
    ],
    url='https://github.com/rubenvereecken/pokemongo-api',
    license='',
    author='',
    author_email='',
    description='PokemonGO API for Python',
    install_requires=reqs
)
