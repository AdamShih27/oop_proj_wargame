from abc import ABC, abstractmethod
from typing import Dict

class ABCBot(ABC):
    @abstractmethod
    def action(self, country_status: Dict[str, any], world_state: Dict[str, any]) -> Dict[str, any]:
        """
        Abstract method for defining bot action.

        Parameters:
        - country_status (Dict[str, any]): Dictionary containing information about the bot's country status.
        - world_state (Dict[str, any]): Dictionary containing information about the world state.

        Returns:
        - action (Dict[str, any]): Dictionary containing information about the action to be taken by the bot.
        """
        pass

    @staticmethod
    def has_nukes(country_status: Dict[str, any]) -> bool:
        return country_status["Nukes"] > 0

"""
Implement a class with an action method which takes the same arguments as shown by sample_bot.py. 
You will take two arguments country_status and world_state. Return a dictionary (we call the Action).

country_status: A dictionary containing the following keys
{
    "Alive": [A boolean],
    "Filename": [A string],
    "Health": [A non-negative integer],
    "ID": [A unique integer],
    "Kills": [A list of country IDs]
    "Name": [A string],
    "Resources": [A non-negative integer],
    "Nukes": [A non-negative integer]
}

world_state: A dictionary containing the following keys
{
    "active_weapons": [A list of Active Weapon dictionaries]
    "countries": [A list of country_status dictionaries]
    "events": [Events dictionary]
    "alive_players": [A set of integers corresponding to country IDs]
}

Action (Idle)
{}

Action (Attack)
{
    "Target": [A country ID]
    "Weapon": [An element of the Weapon enum]
    "Type": "Attack"
}

Player Action: An Action dictionary with additional keys.
{
    "Source": [The ID of the country that performed the action]
    "Success": [Did they act successfully]
    ...
}

Events
{
    "Player": [List of Player Action which happened this turn]
    "Death": [List of Player Action which killed a player this turn]
    "Hit": [List of Player Action which hit a player this turn]
}

Active Weapon
{
    "Delay": [An integer representing the delay until the weapon hits its target]
    "Event": [Player Action with Attack]
}
"""