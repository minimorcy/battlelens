"""BattleLens: ficha instantánea del Pokémon rival en cualquier emulador."""

from importlib.metadata import PackageNotFoundError, version

APP_NAME = "BattleLens"
REPO_URL = "https://github.com/minimorcy/battlelens"
LICENSE_NAME = "MIT"
DATA_ATTRIBUTION = "Datos de Pokémon: PokéAPI (BSD-3-Clause)"
DISCLAIMER = (
    "BattleLens es un proyecto de fans no oficial. No está afiliado ni respaldado por Nintendo, "
    "The Pokémon Company, Creatures Inc. ni GAME FREAK inc. Pokémon y los nombres de los Pokémon "
    "son marcas registradas de sus respectivos titulares."
)

try:
    __version__ = version("battlelens")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"
