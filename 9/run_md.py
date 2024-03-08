from PySide6 import QtWidgets, QtCore

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import TickData, SubscribeRequest, ContractData, OrderRequest
from vnpy.trader.event import EVENT_TICK
from vnpy.trader.utility import load_json, save_json
from vnpy.trader.constant import Exchange, Direction, Offset, OrderType

from vnpy_tts import TtsGateway as Gateway
#  from vnpy_ctp import CtpGateway as Gateway


gateway_name: str = Gateway.default_name


class LoginWidget(QtWidgets.QWidget):
    """接口登陆控件"""

    def __init__(self, main_engine: MainEngine) -> None:
        """构造函数"""

        super().__init__()

        self.main_engine: MainEngine = main_engine

        self.init_ui()
        self.load_setting()

    def init_ui(self) -> None:
        """初始化界面"""
        self.setWindowTitle("连接登陆")

        self.username_line = QtWidgets.QLineEdit()
        self.password_line = QtWidgets.QLineEdit()
        self.password_line.setEchoMode(self.password_line.EchoMode.Password)

        self.broker_line = QtWidgets.QLineEdit()
        self.td_address_line = QtWidgets.QLineEdit()
        self.md_saddress_line = QtWidgets.QLineEdit()
        self.appid_line = QtWidgets.QLineEdit()
        self.auth_code_line = QtWidgets.QLineEdit()

        self.save_check = QtWidgets.QCheckBox("保存")

        button = QtWidgets.QPushButton("登陆")
        button.clicked.connect(self.login)

        form = QtWidgets.QFormLayout()
        form.addRow("用户名", self.username_line)
        form.addRow("密码", self.password_line)
        form.addRow("经纪商代码", self.broker_line)
        form.addRow("交易服务器", self.td_address_line)
        form.addRow("行情服务器", self.md_saddress_line)
        form.addRow("产品名称", self.appid_line)
        form.addRow("授权编码", self.auth_code_line)
        form.addRow(self.save_check)
        form.addRow(button)  

        self.setLayout(form)

    def login(self) -> None:
        """连接登陆"""
        setting = {
            "用户名": self.username_line.text(),
            "密码": self.password_line.text(),
            "经纪商代码": self.broker_line.text(),
            "交易服务器": self.td_address_line.text(),
            "行情服务器": self.md_saddress_line.text(),
            "产品名称": self.appid_line.text(),
            "授权编码": self.auth_code_line.text(),
        }
        self.main_engine.connect(setting, gateway_name)

        if self.save_check.isChecked():
            save_json("tts_connect_data.json", setting)
        
        self.close()

    def load_setting(self) -> None:
        """加载配置"""
        setting = load_json("tts_connect_data.json")

        if setting:
            self.username_line.setText(setting["用户名"])    
            self.password_line.setText(setting["密码"])      
            self.broker_line.setText(setting["经纪商代码"])
            self.td_address_line.setText(setting["交易服务器"])
            self.md_saddress_line.setText(setting["行情服务器"])
            self.appid_line.setText(setting["产品名称"])  
            self.auth_code_line.setText(setting["授权编码"])  

            self.save_check.setChecked(True)


class TradingWidget(QtWidgets.QWidget):
    """交易控件"""

    def __init__(self, main_engine: MainEngine) -> None:
        """构造函数"""
        super().__init__()

        self.main_engine = main_engine
        self.init_ui()

    def init_ui(self) -> None:
        """初始化界面"""
        # 创建控件
        self.symbol_line = QtWidgets.QLineEdit()
        self.symbol_line.returnPressed.connect(self.update_symbol)
        self.exchange_combo = QtWidgets.QComboBox()
        self.exchange_combo.addItems([
            Exchange.CFFEX.value,
            Exchange.SHFE.value,
            Exchange.DCE.value,
            Exchange.CZCE.value,
        ])
        self.direction_combo = QtWidgets.QComboBox()
        self.direction_combo.addItems([
            Direction.LONG.value,
            Direction.SHORT.value, 
        ])
        self.offset_combo = QtWidgets.QComboBox()
        self.offset_combo.addItems([
            Offset.OPEN.value,
            Offset.CLOSE.value,
            Offset.CLOSETODAY.value,
            Offset.CLOSEYESTERDAY.value, 
        ])
        self.price_spin = QtWidgets.QDoubleSpinBox()
        self.price_spin.setDecimals(3)
        self.price_spin.setMinimum(1)
        self.price_spin.setMaximum(1_000_000)

        self.volume_spin = QtWidgets.QSpinBox()
        self.volume_spin.setSuffix("手")
        self.volume_spin.setRange(1,1000)

        button = QtWidgets.QPushButton("下单")
        button.clicked.connect(self.send_order)

        form = QtWidgets.QFormLayout()
        form.addRow("代码", self.symbol_line)
        form.addRow("交易商", self.exchange_combo) 
        form.addRow("方向", self.direction_combo)
        form.addRow("开平", self.offset_combo)
        form.addRow("价格", self.price_spin)
        form.addRow("数量", self.volume_spin)
        form.addRow(button)

        self.setLayout(form)

    def send_order(self) -> None:
        """发送委托"""
        symbol = self.symbol_line.text()
        exchange = Exchange(self.exchange_combo.currentText())
        direction = Direction(self.direction_combo.currentText())
        offset = Offset(self.offset_combo.currentText())
        price = self.price_spin.value()
        volume = self.volume_spin.value()
        order_type = OrderType.LIMIT

        # 确认合约存在
        vt_symbol = f"{symbol}.{exchange.value}"
        contract_new = self.main_engine.get_contract(vt_symbol)
        if not contract_new:
            return
        
        # 发送委托请求
        req = OrderRequest(
            symbol=symbol,
            exchange=exchange,
            direction=direction,
            type=order_type,
            volume=volume,
            price=price,
            offset=offset, 
        )
        self.main_engine.send_order(req, contract_new.gateway_name)

    def update_symbol(self) -> None:
        """更新交易代码"""
        symbol = self.symbol_line.text()
        exchange_str = self.exchange_combo.currentText()
        vt_symbol = f"{symbol}.{exchange_str}"

        contract = self.main_engine.get_contract(vt_symbol)
        if contract:
            self.price_spin.setSingleStep(contract.pricetick)
            self.volume_spin.setSingleStep(contract.min_volume) 


class MainWidget(QtWidgets.QWidget):
    """市场行情组件"""

    # 在类中直接定义signal成员变量，而非__init__构造函数中
    signal = QtCore.Signal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """构造函数"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.ticks = {}

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """初始化界面"""
        # 创建控件
        self.login_button = QtWidgets.QPushButton("登陆")
        self.login_button.clicked.connect(self.show_login_widget)

        self.edit = QtWidgets.QTextEdit()
        self.line = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("订阅")

        # 标签控件
        label = QtWidgets.QLabel()
        label.setText("市场行情监控")  # 文本
        label.setAlignment(QtCore.Qt.AlignCenter) # 对齐

        # 下拉框控件
        self.combo = QtWidgets.QComboBox()

        exchanges = [
            Exchange.CFFEX.value,
            Exchange.SHFE.value,
            Exchange.DCE.value,
            Exchange.CZCE.value,
        ]
        self.combo.addItems(exchanges)

        # ix: int = self.combo.findText("DCE")
        # self.combo.setCurrentIndex(ix)

        # 绑定触发
        self.button.clicked.connect(self.subscribe)

        # 交易控件
        self.trading_widget = TradingWidget(self.main_engine)

        # 网格布局
        grid = QtWidgets.QGridLayout()
        grid.addWidget(label, 0, 0, 1, 2)
        grid.addWidget(self.login_button, 1, 0)
        grid.addWidget(self.line, 2, 0)
        grid.addWidget(self.combo, 2, 1)
        grid.addWidget(self.button, 2, 2)
        grid.addWidget(self.edit, 3, 0, 1, 3)
        
        # 垂直布局
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.trading_widget)

        self.setLayout(vbox)

    def register_event(self) -> None:
        """注册事件监听"""
        # 绑定信号
        self.signal.connect(self.process_tick_event)

        # 注册监听
        self.event_engine.register(EVENT_TICK, self.signal.emit)

    def process_tick_event(self, event: Event) -> None:
        """处理行情数据"""
        tick: TickData = event.data
        last_tick: TickData = self.ticks.get(tick.vt_symbol, None)
        self.ticks[tick.vt_symbol] = tick

        # 必须至少有一条缓存才能计算
        if not last_tick:
            return
        
        # 计算持仓变化
        oi_change: int = tick.open_interest - last_tick.open_interest

        if oi_change > 0:
            oi_str = "开"
        elif oi_change < 0:
            oi_str = "平"
        else:
            oi_str = "换"

        # 计算方向变化
        if tick.last_price >= last_tick.ask_price_1:
            direction_str = "多"
        elif tick.last_price <= last_tick.bid_price_1:
            direction_str = "空"
        else:
            direction_str = "双"

        text = f"{tick.vt_symbol} {tick.last_price} {direction_str} {oi_str}"
        self.edit.append(text) 

    # 定义行情订阅函数
    def subscribe(self) -> None:
        """订阅合约行情"""
        # 获取本地代码
        symbol: str = self.line.text()
        exchange_str = self.combo.currentText()
        vt_symbol: str = f"{symbol}.{exchange_str}"

        # 查阅合约数据
        contract: ContractData = self.main_engine.get_contract(vt_symbol)
        if not contract:
            self.edit.append(f"找不到合约{vt_symbol}")
            return
        
        req = SubscribeRequest(contract.symbol, contract.exchange)
        self.main_engine.subscribe(req, contract.gateway_name)

 
def run() -> None:
    """主程序入口"""
    #  QT应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 创建主引擎
    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)
    main_engine.add_gateway(Gateway)
   
    # 创建控件
    Widget = MainWidget(main_engine, event_engine)
    Widget.show()

    # 运行应用
    qapp.exec()


if __name__ == "__main__":
    run()
