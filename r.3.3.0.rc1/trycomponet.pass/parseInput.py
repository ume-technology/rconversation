# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:parseInput.py
@Time:2023/5/8 23:34
@Read: 
"""
from typing import Dict, Text, Any, List
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData


@DefaultV1Recipe.register([DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER], is_trainable=True)
class CustomNLUComponent(GraphComponent):
    @classmethod
    def create(
            cls,
            config: Dict[Text, Any],
            model_storage: ModelStorage,
            resource: Resource,
            execution_context: ExecutionContext,
    ) -> GraphComponent:
        pass
