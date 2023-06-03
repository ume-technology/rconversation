# This files contains your custom actions which can be used to run custom Python code.
# See this guide on how to implement these action: https://rasa.com/docs/rasa/custom-actions
import re
import random
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset, Restarted
from rasa_sdk.events import ConversationPaused, SessionStarted, ActionExecuted, UserUtteranceReverted
from rasa_sdk.types import DomainDict
import logging
import requests
import json
import time
import hashlib
import secrets
import re

# from config import *

logger = logging.getLogger('GIIKINLogger')
logger.setLevel(logging.DEBUG)  # debug表示全部打印日志信息；如果设置为INFO，那么debug将不再打印

urlGPT = 'https://chatgpt.giikin.com/v1/chat/conversation'  # gpt api
url = 'https://gimp.giikin.com/service?service=inner.order&action=getOrderData&shipPhone&orderNumber&saleName&appKey&t&token'

infoBoxFromURL = {'goods': 'iPhone', "price": '99', 'color': 'red'}
ordersList = {1: "待发货", 2: "已发货", 3: "已收货", 4: "已退货", 5: "已完成退款"}

goodsList = {
    "牙套": {"name": "老年人护齿牙套", "price": 300},
    "水枪": {"name": "游乐园玩具水枪", "price": 400},
    "小米手机": {"name": "2023新款小米手机", "price": 100},
    "连衣裙": {"name": "2023夏季新款淑女裙", "price": 200},
}

infoBox = {
    "sale_title": "百搭休閒內增高小白鞋",
    "special_price": 899,
    "options": {
        "chinese": [
            {
                "name": "颜色",
                "values": "白桔，白蓝，白红"
            },
            {
                "name": "尺码",
                "values": "35，36，37，38，39，40"
            }
        ],
        "trans": [
            {
                "trans_name": "顏色",
                "trans_values": "白桔色，白藍色，白紅色"
            },
            {
                "trans_name": "尺碼",
                "trans_values": "35，36，37，38，39，40"
            }
        ]
    },
}


def get_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()


class ActionSessionStart(Action):  # First Action
    def name(self) -> Text:
        return "action_session_start"

    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取字典goods infoBox类型的元数据
        metadata = tracker.get_slot("session_started_metadata")
        logger.info("Action metadata: - {}".format(metadata))
        newmeta = {}
        if metadata:
            newmeta['sale_title'] = metadata.get('sale_title')
            newmeta['special_price'] = metadata.get('special_price')
            newmeta['options'] = metadata.get('options')

        return [SessionStarted(), ActionExecuted("action_listen"),
                SlotSet('infoBoxGoods', newmeta), SlotSet('haveInfoBox', True)]

        # if newmeta is not None:
        #     return [SessionStarted(), ActionExecuted("action_listen"),
        #             SlotSet('infoBoxGoods', newmeta), SlotSet('haveInfoBox', True)]
        # else:
        #     return [SessionStarted(), ActionExecuted("action_listen"), SlotSet("haveInfoBox", False)]


class ActionResponseGreet(Action):
    def name(self) -> Text:
        return "action_say_hello"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "妳好，請問需要什麽幫助，我可以為您查詢訂單、查詢物流、檢索商品。同時您也可以嚮我咨詢商品使用方法。",
            'type': 0
        })
        return []


class ActionResponseBye(Action):
    def name(self) -> Text:
        return "action_say_bye"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "Bye Bye",
            'type': 0
        })
        return []


class ActiontotRepeace(Action):
    def name(self) -> Text:
        return "action_repeace"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "很抱歉，我很理解您的心情，因此我已經為您發送您的訂單訊息給相關人員，即刻會有專人幫您處理，請您再給我一些時間，感謝您的理解！",
            'type': 0
        })
        return []


class ActiondoOrder(Action):
    def name(self) -> Text:
        return "action_doorder"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "你好，您正在关注的商品目前該是最低價，所以您現在購買是非常划算的哦！",
            'type': 0
        })
        return []


class ActionDiscount(Action):
    def name(self) -> Text:
        return "action_discount"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "您好，因為這款產品是折扣價格，您在頁面上看到的價格已是優惠的摺扣價，所以是沒有贈品贈送的喔。",
            'type': 0
        })
        return []


class ActionEnsureCode(Action):
    def name(self) -> Text:
        return "action_ensurecode"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "很抱歉，我很理解您的心情，因此我已經為您發送您的訂單訊息給相關人員，即刻會有專人幫您處理，請您再給我一些時間，感謝您的理解！",
            'type': 0
        })
        return []


class ActionFasterExpress(Action):
    def name(self) -> Text:
        return "action_fasterexpress"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={
            'text': "很抱歉，我很理解您的心情，因此我已經為您發送您的訂單訊息給相關人員，即刻會有專人幫您處理，請您再給我一些時間，感謝您的理解！",
            'type': 0
        })
        return []


# ============================================================ QUE  Goods  and to make orders   and  Code  Express


class ActionGoodsInfoWithMetaData(Action):
    def name(self):
        return "action_goodsInfo_Metadata"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        infoBoxGoods = tracker.get_slot('infoBoxGoods')
        # dispatcher.utter_message(text=f"您正在關註的商品信息如下: {infoBoxGoods} \n"
        #                               f"這是目前該商品的最低價，所以您現在購買是非常划算的哦！")
        dispatcher.utter_message(json_message={
            'text': f"您正在關註的商品信息如下: {infoBoxGoods} \n"
                    f"這是目前該商品的最低價，所以您現在購買是非常划算的哦！",
            'type': 0
        })
        return []


class ActionSlotSetterCode(Action):
    def name(self):
        return "action_slot_codes_setter"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        code = tracker.get_slot('codes')
        if code:
            return [SlotSet('havecode', True)]
        else:
            return [SlotSet('havecode', False)]


class ActionSlotSetterUSEgoods(Action):
    """ 完成从用户输入的信息中获取goods slot信息并完成set """

    def name(self):
        return "action_slot_setter_have_usegoods"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        usegoods = tracker.get_slot('usegoods')
        # logger.info(usegoods)
        if usegoods:
            return [SlotSet('havegoods', True)]
        else:
            return [SlotSet('havegoods', False)]


class ActionSelectByCode(Action):
    def name(self) -> Text:
        return "action_select_by_code"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        code = tracker.get_slot('codes')
        # print('code: ', code)
        # code = 'QA2305302350588D9Q27'  # temp  code break

        shipPhone, orderNumber = '', ''
        rule = re.compile('^[a-zA-z]{1}.*$')
        if rule.match(code) is None or '+' in code:  # 不以字母开头，或有+，认为是电话号
            shipPhone = code
        else:
            orderNumber = code

        all_message = tracker.latest_message
        metadata = all_message['metadata']
        print('metadata: ', metadata)

        tst = int(time.mktime(time.localtime(time.time())))
        indata2sha1 = str(tst) + 'zBx+Up0W1CaoVQX3iRR8fBAbDRo='
        if shipPhone:
            post_data = {
                'service': 'inner.order',
                'action': 'getOrderData',
                'shipPhone': shipPhone,
                'orderNumber': '',
                'saleName': '',
                'appKey': 'intent',
                't': str(tst),
                'token': get_sha1(indata2sha1)
            }
            res = requests.post(url, data=post_data).text
            res = json.loads(res)
            info = {}
            info['saleTitle'] = res['data']['productSpecs'][0].get('saleTitle')
            info['logisticsInfo'] = res['data']['logisticsInfo'][0]
            # print('res: ', res)
            dispatcher.utter_message(json_message={
                'text': f"根据您给定的信息：{code}。我们帮您查询到您的订单信息如下：\n"
                        f"{info}。\n 感谢您的来信。",
                'type': 0})
            # return [Restarted()]
            return []
        elif orderNumber:
            post_data = {
                'service': 'inner.order',
                'action': 'getOrderData',
                'shipPhone': '',
                'orderNumber': orderNumber,
                'saleName': '',
                'appKey': 'intent',
                't': str(tst),
                'token': get_sha1(indata2sha1)
            }
            res = requests.post(url, data=post_data).text
            res = json.loads(res)
            info = {}
            info['saleTitle'] = res['data']['productSpecs'][0].get('saleTitle')
            info['logisticsInfo'] = res['data']['logisticsInfo'][0]
            # print('res: ', res)
            dispatcher.utter_message(json_message={
                'text': f"根据您给定的信息：{code}。我们帮您查询到您的订单信息如下：\n"
                        f"{info}。\n 感谢您的来信。",
                'type': 0})
            # return [Restarted()]
            return []
        else:
            dispatcher.utter_message(json_message={'text': f"我沒能幫您查詢到任何有效信息，請檢查信息後重新輸入.", 'type': 0})
            # return [Restarted()]
            return []


class ActionSlotSetterQUEgoods(Action):
    def name(self):
        return "action_slot_setter_have_quegoods"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        quegoods = tracker.get_slot('quegoods')
        logger.info("valid user give question goods：{}".format(quegoods))
        # '# 这里其实是因为tracker确实已经通过NLU捕捉了entity的信息，且更新完成了自己的状态，但是slot的填充需要通过事件触发。因此这里也就有了滞后的现象'

        if quegoods:
            logger.info("fill slot-havegoods True")
            return [SlotSet('havegoods', True)]
        else:
            logger.info("fill slot-havegoods False")
            return [SlotSet('havegoods', False)]


class ActionUseGoods(Action):
    def name(self) -> Text:
        return "action_how_use_goods"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        usegoods = tracker.get_slot('usegoods')
        infoBoxGoods = tracker.get_slot('infoBoxGoods')

        try:
            def requse(infos):
                mid = "我现在有一个这样的商品：{}，请告诉我它的使用方式和一些使用建议。".format(infos)
                res = requests.post(url=urlGPT, json={"message": mid, "user": "Conversation"})
                res = json.loads(res.text)['data'].replace('\n\n', '')

                if res:
                    dispatcher.utter_message(
                        json_message={
                            'text': f"我们建议您按照如下方式使用：\n"
                                    f"{res}\n"
                                    f"以上信息均為參考建議。在實際使用商品的過程中，請仔細斟酌上述信息，併參考隨贈的商品使用說明書。\n"
                                    f"如您無法理解外文說明書，請嚮您身邊的朋友尋求幫助或借助翻譯工具使用，感謝您的配合！",
                            'type': 0})
                else:
                    dispatcher.utter_message(json_message={
                        'text': f"根據您的信息，我暫時無法為您提供更多的使用說明。您可以檢視隨附的產品使用說明書，感謝您的配合！",
                        'type': 1})

            if infoBoxGoods:
                requse(infoBoxGoods['sale_title'])
                return [Restarted()]
                # return []
            elif usegoods:
                requse(usegoods)
                return [Restarted()]
                # return []
            else:
                dispatcher.utter_message(
                    json_message={'text': f"根據您的信息，我暫時無法為您提供更多的使用說明。您可以檢視隨附的產品使用說明書，感謝您的配合！",
                                  'type': 0})
                return [Restarted()]
                # return []
        except:
            dispatcher.utter_message(
                json_message={'text': f"非常抱歉，我暫時無法為您提供更多的使用說明。您可以檢視隨附的產品使用說明書，感謝您的配合！",
                              'type': 0})
            return [Restarted()]
            # return []


# ============================================================ Human   /   OOS   /   FallBack

class ActionHuman(Action):
    def name(self):
        logger.info("active: action_tohuman")
        return "action_tohuman"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(json_message={'text': "我已经记录了您的相关信息，现在我將為您轉人工服務！", 'type': 1})

        # wait 调用人工接口服务API - 传递Tracker
        # url = ""
        # data = {"history": tracker, "task": "cancelOrders"}
        # res = requests.post(url, params=data).text

        logger.info("robot server to human and end server")
        return [ConversationPaused(), UserUtteranceReverted()]


class ActionResponseOutofscope(Action):
    def name(self):
        return "action_response_intent_outofscope"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            text = tracker.latest_message['text']
            data = {"message": text, "user": "Conversation"}
            res = requests.post(url=urlGPT, json=data)
            res = json.loads(res.text)['data'].replace('\n\n', '')
            if res:
                dispatcher.utter_message(
                    json_message={
                        'text': f"{res}\n"
                                f"更多的：我可以為您查詢訂單、查詢物流、檢索商品。您也可以嚮我咨詢商品使用方法。感謝您的配合！",
                        'type': 0})
            else:
                dispatcher.utter_message(
                    json_message={
                        'text': f"很抱歉我还没有能力解决您提出的问题。\n"
                                f"但是我可以為您查詢訂單、查詢物流、檢索商品。您也可以嚮我咨詢商品使用方法。感謝您的配合！",
                        'type': 0})
        except:
            dispatcher.utter_message(
                json_message={'text': f"很抱歉我还没有能力解决您提出的问题。\n"
                                      f"我可以為您查詢訂單、查詢物流、檢索商品。您也可以嚮我咨詢商品使用方法。感謝您的配合！",
                              'type': 0})
        # return []
        return [Restarted()]


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        logger.info("active: action_default_fallback")
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        dispatcher.utter_message(
            json_message={'text': "很抱歉我沒能明白您發送過來的信息的含義。请尝试以更清晰的表达告诉我您需要什么帮助！", 'type': 0})
        # return []
        return [Restarted()]


# ==============================================================================================


class ActionResetHaveQUESlot(Action):
    def name(self):
        return "action_empty_have_que_slot"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info('Empty All Slots - QUE Goods')
        return [AllSlotsReset()]

# class ActionValidGoodsForm(FormValidationAction):
#     def name(self) -> Text:
#         return "action_valid_goods_form"
#
#     def validate_code(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
#                       domain: DomainDict, ) -> Dict[Text, Any]:
#         goods = tracker.get_slot('goods')
#         return {"goods": goods}
#
#
# class ActionValidCodeForm(FormValidationAction):
#     def name(self) -> Text:
#         return 'action_valid_code_form'
#
#     def validate_code(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
#                       domain: DomainDict, ) -> Dict[Text, Any]:
#         code = tracker.get_slot('codes')
#         return {"code": code}
