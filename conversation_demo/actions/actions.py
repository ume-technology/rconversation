import re
import random
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset, Restarted
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import ConversationPaused
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SessionStarted, ActionExecuted
import logging
import requests
import json


class ActionListen(Action):
    def name(self):
        return "action_start_listen"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
        Dict[Text, Any]]:
        return [SessionStarted(), ActionExecuted("action_listen")]


class ActionResponseOutofscope(Action):
    def name(self):
        return "action_make_sure_yes_or_no"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="我将为您转人工服务")
        res = tracker.get_intent_of_latest_message(skip_fallback_intent=True)
        print("====", res)
        if res:
            return [SlotSet("makesure", True)]
        else:
            return [SlotSet("makesure", False)]
