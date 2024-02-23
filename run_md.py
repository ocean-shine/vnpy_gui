from time import sleep
from PySide6 import QtWidgets

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import TickData, SubscribeRequest
from vnpy.trader.constant import Exchange
from vnpy.trader.event import EVENT_TICK

from vnpy_tts import TtsGateway as Gateway
# from vnpy_ctp import CtpGateway as Gateway


gateway_name: str = Gateway.default_name

setting: dict = {
    # "用户名": "222772",
    # "密码": "Cc@18800159600",
    "用户名": "8505",
    "密码": "123456",
    "经纪商代码": "",
    # "交易服务器": "180.168.146.187:10201",
    # "行情服务器": "180.168.146.187:10211",
    # "交易服务器": "180.168.146.187:10130",
    # "行情服务器": "180.168.146.187:10131",
    # "交易服务器": "121.37.90.193:20002",
    # "行情服务器": "218.202.237.33:10213",
    "交易服务器": "121.37.80.177:20002",
    "行情服务器": "121.37.80.177:20004",
    "产品名称": "",
    "授权编码": "",
}

    
def run() -> None:
    """主程序入口"""
    #
    qapp = QtWidgets.QApplication([])

    #
    edit = QtWidgets.QTextEdit()
    edit.show()
    
    #
    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)
    main_engine.add_gateway(Gateway)
    edit.append("创建主引擎成功")
    
    #
    def print_tick(event: Event) -> None:
        """打印行情数据"""
        tick: TickData = event.data
        edit.append(str(tick))

    #
    event_engine.register(EVENT_TICK, print_tick)
    edit.append("注册行情事件监听")

    #
    main_engine.connect(setting, gateway_name)
    edit.append("连接交易接口")

    sleep(5)

    req = SubscribeRequest("sn2402", Exchange.SHFE)
    main_engine.subscribe(req, gateway_name)
    edit.append(f"订阅行情推送{req.vt_symbol}")

    qapp.exec()


if __name__ == "__main__":
    run()
