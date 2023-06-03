# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:UmeAI
@File:inputWithGoods.py
@Time:2023/5/9 9:55
@Read: define one channel： user input with meta data channel to connect user with rasa
"""
import asyncio
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse

from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import rasa.utils.endpoints
from rasa.core.channels.channel import InputChannel, CollectingOutputChannel, UserMessage


class InputWithGoodsBox(InputChannel):
    def name(cls) -> Text:
        return "inputWithGoodsBox"

    def blueprint(self, on_new_message: Callable[[UserMessage], Awaitable[None]]) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender")  # method to get sender_id
            text = request.json.get("text")  # method to fetch text
            input_channel = self.name()  # method to fetch input channel
            metadata = self.get_metadata(request)  # method to get metadata

            collector = CollectingOutputChannel()

            # include exception handling

            await on_new_message(
                UserMessage(text, collector, sender_id, input_channel=input_channel, metadata=metadata, )
            )

            return response.json(collector.messages)

        return custom_webhook

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        meta = request.json.get("metadata", None)
        print("InputChannel Meta:", meta)
        return meta
