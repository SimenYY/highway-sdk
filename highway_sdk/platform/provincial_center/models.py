from sqlalchemy import Column, Numeric, String, DateTime, CHAR, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ========== 当前信息表 ==========


class CurAero(Base):
    """气象检测器当前信息表（cur_aero）"""

    __tablename__ = "cur_aero"

    n_code = Column(
        Numeric(9, 0), primary_key=True, comment="设备编码，9位，格式 yytzzdddd"
    )
    n_period = Column(
        Numeric(4, 0),
        primary_key=True,
        default=1,
        comment="时间周期，缺省值为1，表示最近几分钟数据",
    )
    d_temp = Column(Numeric(5, 2), comment="温度（℃），范围 -99 ~ 100")
    d_humidity = Column(Numeric(5, 2), comment="湿度（%），范围 0 ~ 100")
    c_icing = Column(CHAR(1), comment="是否结冰：'0'=未结冰，'1'=结冰")
    n_visibility = Column(Numeric(6, 0), comment="能见度（米）")
    c_wind_dir = Column(
        CHAR(1),
        comment="风向：'1'=偏北，'2'=东北，'3'=偏东，'4'=东南，'5'=偏南，'6'=西南，'7'=偏西，'8'=西北",
    )
    d_wind_speed = Column(Numeric(3, 1), comment="风速（米/秒）")
    d_rainfall = Column(Numeric(5, 1), comment="雨量（毫米）")
    c_status = Column(
        CHAR(1),
        comment="工作状态：'0'=正常，'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知",
    )
    vc_status_des = Column(String(60), comment="工作状态描述")
    t_rec_time = Column(DateTime, comment="记录时间")


class CurVd(Base):
    """车辆检测器当前信息表（cur_vd）"""

    __tablename__ = "cur_vd"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码，9位")
    n_period = Column(
        Numeric(4, 0), primary_key=True, default=1, comment="时间周期，缺省值为1"
    )

    # 上行车道 1~5
    d_up_lane1_occupy = Column(Numeric(6, 2), comment="上行1车道占有率（%）")
    d_up_lane1_speed = Column(Numeric(5, 2), comment="上行1车道速度（km/h）")
    n_up_lane1_quantity = Column(Numeric(6, 0), comment="上行1车道车流量（辆/分）")
    d_up_lane2_occupy = Column(Numeric(6, 2), comment="上行2车道占有率（%）")
    d_up_lane2_speed = Column(Numeric(5, 2), comment="上行2车道速度（km/h）")
    n_up_lane2_quantity = Column(Numeric(6, 0), comment="上行2车道车流量（辆/分）")
    d_up_lane3_occupy = Column(Numeric(6, 2), comment="上行3车道占有率（%）")
    d_up_lane3_speed = Column(Numeric(5, 2), comment="上行3车道速度（km/h）")
    n_up_lane3_quantity = Column(Numeric(6, 0), comment="上行3车道车流量（辆/分）")
    d_up_lane4_occupy = Column(Numeric(6, 2), comment="上行4车道占有率（%）")
    d_up_lane4_speed = Column(Numeric(5, 2), comment="上行4车道速度（km/h）")
    n_up_lane4_quantity = Column(Numeric(6, 0), comment="上行4车道车流量（辆/分）")
    d_up_lane5_occupy = Column(Numeric(6, 2), comment="上行5车道占有率（%）")
    d_up_lane5_speed = Column(Numeric(5, 2), comment="上行5车道速度（km/h）")
    n_up_lane5_quantity = Column(Numeric(6, 0), comment="上行5车道车流量（辆/分）")

    # 下行车道 1~5
    d_down_lane1_occupy = Column(Numeric(6, 2), comment="下行1车道占有率（%）")
    d_down_lane1_speed = Column(Numeric(5, 2), comment="下行1车道速度（km/h）")
    n_down_lane1_quantity = Column(Numeric(6, 0), comment="下行1车道车流量（辆/分）")
    d_down_lane2_occupy = Column(Numeric(6, 2), comment="下行2车道占有率（%）")
    d_down_lane2_speed = Column(Numeric(5, 2), comment="下行2车道速度（km/h）")
    n_down_lane2_quantity = Column(Numeric(6, 0), comment="下行2车道车流量（辆/分）")
    d_down_lane3_occupy = Column(Numeric(6, 2), comment="下行3车道占有率（%）")
    d_down_lane3_speed = Column(Numeric(5, 2), comment="下行3车道速度（km/h）")
    n_down_lane3_quantity = Column(Numeric(6, 0), comment="下行3车道车流量（辆/分）")
    d_down_lane4_occupy = Column(Numeric(6, 2), comment="下行4车道占有率（%）")
    d_down_lane4_speed = Column(Numeric(5, 2), comment="下行4车道速度（km/h）")
    n_down_lane4_quantity = Column(Numeric(6, 0), comment="下行4车道车流量（辆/分）")
    d_down_lane5_occupy = Column(Numeric(6, 2), comment="下行5车道占有率（%）")
    d_down_lane5_speed = Column(Numeric(5, 2), comment="下行5车道速度（km/h）")
    n_down_lane5_quantity = Column(Numeric(6, 0), comment="下行5车道车流量（辆/分）")

    c_status = Column(
        CHAR(1),
        comment="工作状态：'0'=正常，'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知",
    )
    vc_status_des = Column(String(60), comment="工作状态描述")
    t_rec_time = Column(DateTime, comment="记录时间")


class CurCsls(Base):
    """可变限速标志当前信息表（cur_csls）"""

    __tablename__ = "cur_csls"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码，9位")
    n_limit = Column(Numeric(4, 0), comment="限速值（千米/小时）")
    c_status = Column(
        CHAR(1),
        comment="工作状态：'0'=正常，'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知",
    )
    vc_status_des = Column(String(60), comment="工作状态描述")
    t_rec_time = Column(DateTime, comment="记录时间")


class CurCms(Base):
    """可变情报板当前信息表（cur_cms）"""

    __tablename__ = "cur_cms"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码，9位")
    n_sequence = Column(
        Numeric(4, 0), primary_key=True, comment="序列号：单条信息为1，多条滚动时递增"
    )
    vc_orig_content = Column(
        Text,
        comment="原始显示内容，可为文本或 base64 编码图片，含颜色、位置、字体等属性",
    )
    n_disp_time = Column(
        Numeric(6, 0), comment="停留时间（秒）：单条信息为0，多条滚动时为对应停留秒数"
    )
    c_status = Column(
        CHAR(1),
        comment="工作状态：'0'=正常，'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知",
    )
    vc_status_des = Column(String(60), comment="工作状态描述")
    t_rec_time = Column(DateTime, comment="记录时间")


class CurVi(Base):
    """能见度检测器当前信息表（cur_vi）"""

    __tablename__ = "cur_vi"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码，9位")
    n_period = Column(
        Numeric(4, 0), primary_key=True, default=1, comment="时间周期，缺省值为1"
    )
    n_visibility = Column(Numeric(6, 0), comment="能见度（米）")
    c_status = Column(
        CHAR(1),
        comment="工作状态：'0'=正常，'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知",
    )
    vc_status_des = Column(String(60), comment="工作状态描述")
    t_rec_time = Column(DateTime, comment="记录时间")


class CurEt(Base):
    """紧急电话当前信息表（cur_et）"""

    __tablename__ = "cur_et"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码，9位")
    t_rec_time = Column(
        DateTime, primary_key=True, comment="记录时间（状态变化时记录）"
    )
    c_et_status = Column(CHAR(1), comment="话机状态：'1'=故障，'2'=挂机，'3'=摘机")
    c_status = Column(
        CHAR(1),
        comment="工作状态：'0'=正常，'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知",
    )
    vc_status_des = Column(String(60), comment="工作状态描述")


# ========== 历史记录表 ==========


class HistAero(Base):
    """气象检测器历史数据表（hist_aero）"""

    __tablename__ = "hist_aero"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    n_time_stamp = Column(
        Numeric(12, 0), primary_key=True, comment="时间戳记，格式 YYYYMMDDhhmm"
    )
    d_temp = Column(Numeric(5, 2), comment="温度（℃）")
    d_humidity = Column(Numeric(5, 2), comment="湿度（%）")
    c_icing = Column(CHAR(1), comment="是否结冰：'0'=未结冰，'1'=结冰")
    n_visibility = Column(Numeric(6, 0), comment="能见度（米）")
    c_wind_dir = Column(CHAR(1), comment="风向编码")
    d_wind_speed = Column(Numeric(3, 1), comment="风速（米/秒）")
    d_rainfall = Column(Numeric(5, 1), comment="雨量（毫米）")
    t_rec_time = Column(DateTime, comment="记录时间")
    c_send_flag = Column(
        CHAR(1), default="0", comment="发送标志：'0'=未发送，'1'=已发送至省中心"
    )
    c_stat_falg = Column(
        CHAR(1),
        default="0",
        comment="统计标志：'0'=未统计，'1'=已统计（注：原文拼写为 falg）",
    )


class HistVd(Base):
    """车辆检测器历史数据表（hist_vd）"""

    __tablename__ = "hist_vd"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    n_time_stamp = Column(
        Numeric(12, 0), primary_key=True, comment="时间戳记，格式 YYYYMMDDhhmm"
    )

    # 上行/下行字段同 CurVd（此处完整列出，实际可复用）
    d_up_lane1_occupy = Column(Numeric(6, 2))
    d_up_lane1_speed = Column(Numeric(5, 2))
    n_up_lane1_quantity = Column(Numeric(6, 0))
    d_up_lane2_occupy = Column(Numeric(6, 2))
    d_up_lane2_speed = Column(Numeric(5, 2))
    n_up_lane2_quantity = Column(Numeric(6, 0))
    d_up_lane3_occupy = Column(Numeric(6, 2))
    d_up_lane3_speed = Column(Numeric(5, 2))
    n_up_lane3_quantity = Column(Numeric(6, 0))
    d_up_lane4_occupy = Column(Numeric(6, 2))
    d_up_lane4_speed = Column(Numeric(5, 2))
    n_up_lane4_quantity = Column(Numeric(6, 0))
    d_up_lane5_occupy = Column(Numeric(6, 2))
    d_up_lane5_speed = Column(Numeric(5, 2))
    n_up_lane5_quantity = Column(Numeric(6, 0))

    d_down_lane1_occupy = Column(Numeric(6, 2))
    d_down_lane1_speed = Column(Numeric(5, 2))
    n_down_lane1_quantity = Column(Numeric(6, 0))
    d_down_lane2_occupy = Column(Numeric(6, 2))
    d_down_lane2_speed = Column(Numeric(5, 2))
    n_down_lane2_quantity = Column(Numeric(6, 0))
    d_down_lane3_occupy = Column(Numeric(6, 2))
    d_down_lane3_speed = Column(Numeric(5, 2))
    n_down_lane3_quantity = Column(Numeric(6, 0))
    d_down_lane4_occupy = Column(Numeric(6, 2))
    d_down_lane4_speed = Column(Numeric(5, 2))
    n_down_lane4_quantity = Column(Numeric(6, 0))
    d_down_lane5_occupy = Column(Numeric(6, 2))
    d_down_lane5_speed = Column(Numeric(5, 2))
    n_down_lane5_quantity = Column(Numeric(6, 0))

    t_rec_time = Column(DateTime, comment="记录时间")
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")
    c_stat_falg = Column(CHAR(1), default="0", comment="统计标志")


class HistCsls(Base):
    """可变限速标志历史数据表（hist_csls）"""

    __tablename__ = "hist_csls"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    t_rec_time = Column(
        DateTime, primary_key=True, comment="记录时间（内容或状态变化时新增）"
    )
    n_limit = Column(Numeric(4, 0), comment="限速值（千米/小时）")
    c_status = Column(CHAR(1), comment="工作状态")
    vc_status_des = Column(String(60), comment="工作状态描述")
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")


class HistCms(Base):
    """可变情报板历史数据表（hist_cms）"""

    __tablename__ = "hist_cms"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    t_rec_time = Column(
        DateTime, primary_key=True, comment="记录时间（内容变化时新增）"
    )
    vc_orig_content = Column(String(2000), comment="原始播放内容（厂家协议格式）")
    vc_content = Column(
        String(2000),
        comment="标准化播放内容，格式：内容1/时间1|内容2/时间2…，时间单位秒",
    )
    c_status = Column(CHAR(1), comment="工作状态")
    vc_status_des = Column(String(60), comment="工作状态描述")
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")


class HistVi(Base):
    """能见度检测器历史数据表（hist_vi）"""

    __tablename__ = "hist_vi"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    n_time_stamp = Column(
        Numeric(12, 0), primary_key=True, comment="时间戳记，格式 YYYYMMDDhhmm"
    )
    n_visibility = Column(Numeric(6, 0), comment="能见度（米）")
    t_rec_time = Column(DateTime, comment="记录时间")
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")
    c_stat_falg = Column(CHAR(1), default="0", comment="统计标志")


class HistEt(Base):
    """紧急电话历史数据表（hist_et）"""

    __tablename__ = "hist_et"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    t_rec_time = Column(
        DateTime, primary_key=True, comment="记录时间（状态变化时新增）"
    )
    c_et_status = Column(CHAR(1), comment="话机状态：'1'=故障，'2'=挂机，'3'=摘机")
    c_status = Column(CHAR(1), comment="工作状态")
    vc_status_des = Column(String(60), comment="工作状态描述")
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")


# ========== 门限参数表 ==========


class CurSectLimit(Base):
    """交通区段门限设置表（cur_sect_limit）"""

    __tablename__ = "cur_sect_limit"

    n_sect_code = Column(
        Numeric(8, 0),
        primary_key=True,
        comment="区段编码，8位，格式 ttxxttxx，含方向性",
    )
    n_speed_limit1 = Column(Numeric(3, 0), comment="速度门限1（千米/小时）")
    n_speed_limit2 = Column(Numeric(3, 0), comment="速度门限2")
    n_speed_limit3 = Column(Numeric(3, 0), comment="速度门限3")
    n_speed_limit4 = Column(Numeric(3, 0), comment="速度门限4")
    n_occupy_limit1 = Column(Numeric(3, 0), comment="占有率门限1（%）")
    n_occupy_limit2 = Column(Numeric(3, 0), comment="占有率门限2")
    n_occupy_limit3 = Column(Numeric(3, 0), comment="占有率门限3")
    n_occupy_limit4 = Column(Numeric(3, 0), comment="占有率门限4")
    n_quantity_limit1 = Column(Numeric(4, 0), comment="车流量门限1（辆/小时）")
    n_quantity_limit2 = Column(Numeric(4, 0), comment="车流量门限2")
    n_quantity_limit3 = Column(Numeric(4, 0), comment="车流量门限3")
    n_quantity_limit4 = Column(Numeric(4, 0), comment="车流量门限4")
    t_rec_time = Column(DateTime, comment="设置时间")


class CurAeroLimit(Base):
    """气象门限设置表（cur_aero_limit）"""

    __tablename__ = "cur_aero_limit"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    n_visibility_limit1 = Column(Numeric(6, 0), comment="能见度门限1（米）")
    n_visibility_limit2 = Column(Numeric(6, 0), comment="能见度门限2")
    n_visibility_limit3 = Column(Numeric(6, 0), comment="能见度门限3")
    n_visibility_limit4 = Column(Numeric(6, 0), comment="能见度门限4")
    d_wind_limit1 = Column(Numeric(3, 1), comment="风速门限1（千米/小时）")
    d_wind_limit2 = Column(Numeric(3, 1), comment="风速门限2")
    d_wind_limit3 = Column(Numeric(3, 1), comment="风速门限3")
    d_wind_limit4 = Column(Numeric(3, 1), comment="风速门限4")
    n_rainfall_limit1 = Column(Numeric(4, 0), comment="雨量门限1（毫米）")
    n_rainfall_limit2 = Column(Numeric(4, 0), comment="雨量门限2")
    n_rainfall_limit3 = Column(Numeric(4, 0), comment="雨量门限3")
    n_rainfall_limit4 = Column(Numeric(4, 0), comment="雨量门限4")
    t_rec_time = Column(DateTime, comment="设置时间")


class CurViLimit(Base):
    """能见度门限设置表（cur_vi_limit）"""

    __tablename__ = "cur_vi_limit"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    n_visibility_limit1 = Column(Numeric(6, 0), comment="能见度门限1（米）")
    n_visibility_limit2 = Column(Numeric(6, 0), comment="能见度门限2")
    n_visibility_limit3 = Column(Numeric(6, 0), comment="能见度门限3")
    n_visibility_limit4 = Column(Numeric(6, 0), comment="能见度门限4")
    t_rec_time = Column(DateTime, comment="设置时间")


# ========== 控制命令与故障 ==========


class CtrlCmd(Base):
    """设备控制命令表（ctrl_cmd）"""

    __tablename__ = "ctrl_cmd"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    t_order_time = Column(DateTime, primary_key=True, comment="命令下达时间")
    vc_content = Column(
        String(2000), comment="命令内容，格式：内容1/时间1|内容2/时间2…（秒）"
    )
    vc_postscript = Column(String(250), comment="命令附言")
    c_grade = Column(
        CHAR(1), comment="命令等级：'0'=一般（需确认），'1'=强制（直接执行）"
    )
    t_expire_time = Column(DateTime, comment="命令到期时间")
    n_order_op = Column(Numeric(8, 0), comment="省中心操作员编码（yytzznnn）")
    c_status = Column(
        CHAR(1),
        default="0",
        comment="处理状态：'0'=未接收，'1'=执行中，'2'=执行完毕，'3'=拒绝执行，'4'=已过期",
    )
    vc_status_des = Column(String(250), comment="处理状态描述（如拒绝原因）")
    n_execute_op = Column(Numeric(8, 0), comment="路段中心操作员编码")
    t_execute_time = Column(DateTime, comment="执行时间")
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")


class HistStatus(Base):
    """故障信息历史数据表（hist_status）"""

    __tablename__ = "hist_status"

    n_code = Column(Numeric(9, 0), primary_key=True, comment="设备编码")
    t_fault_time = Column(DateTime, primary_key=True, comment="故障发生时间")
    c_status = Column(
        CHAR(1), comment="故障状态：'1'=设备故障，'2'=通讯失败，'3'=数据错误，'9'=未知"
    )
    vc_status_des = Column(String(60), comment="故障描述")
    t_repair_time = Column(
        DateTime, nullable=True, comment="修复时间（未修复时为 NULL）"
    )
    c_send_flag = Column(CHAR(1), default="0", comment="发送标志")
    c_stat_falg = Column(CHAR(1), default="0", comment="统计标志")
