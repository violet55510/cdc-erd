# -*- coding: utf-8 -*-
"""
CDC (Clearbrook Diabetes Centre) 集中数据库
生成 UML 类图 + ERD（Fivetran QuickBooks 风格）

用法: python make_diagrams.py
输出: ../diagrams/class-diagram.svg, ../diagrams/erd.svg
"""
import os, math, html

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "diagrams")

FONT = "'Segoe UI','Microsoft YaHei','PingFang SC',sans-serif"
MONO = "'Cascadia Mono','Consolas','Microsoft YaHei',monospace"

# ---------------------------------------------------------------- 尺寸常量
W = 360          # 卡片宽
ROW = 21         # 行高
HEAD = 50        # 表头高
PADB = 12        # 底部留白
OPS = 30         # 类图操作分区高

def ch(n, extra=0):
    return HEAD + n * ROW + PADB + extra

# ---------------------------------------------------------------- 配色
PALETTE = {
    "cyan":   {"fill": "#E4F2F7", "stroke": "#C4E2EC", "ink": "#2B6C7E", "dot": "#7FB3C4"},
    "pink":   {"fill": "#FBE7EA", "stroke": "#F1CBD3", "ink": "#9A4757", "dot": "#D79BA7"},
    "green":  {"fill": "#E7F4E1", "stroke": "#CEE7C4", "ink": "#4A7A43", "dot": "#8FBE83"},
    "amber":  {"fill": "#FDF3DB", "stroke": "#F6E1B7", "ink": "#8A6820", "dot": "#DDBB6A"},
    "blue":   {"fill": "#E5EEFA", "stroke": "#C7DAF3", "ink": "#385E92", "dot": "#8FB0DA"},
    "purple": {"fill": "#EDE7F8", "stroke": "#D8CCF0", "ink": "#5C488A", "dot": "#A995D2"},
}
INK, SUB, MUTED = "#1F2937", "#5B6675", "#93A0B0"
LINE = "#A9B4C2"

# ---------------------------------------------------------------- 数据模型
# 列: (字段名, 类型, 键标记, 外键目标, 中文注释, 操作)
# 键标记: "PK" / "FK" / "UK" / "PK,FK" / "PK,UK" / ""
T = {}

T["Center"] = dict(cn="中心表", mod="A", cols=[
    ("CenterID",     "CHAR(4)",      "PK", None,          "中心编号"),
    ("CenterName",   "VARCHAR(50)",  "",   None,          "中心名称"),
    ("Address",      "VARCHAR(100)", "",   None,          "邮寄地址"),
    ("Phone",        "VARCHAR(20)",  "",   None,          "联系电话"),
    ("Email",        "VARCHAR(50)",  "",   None,          "电子邮箱"),
    ("DirectorName", "VARCHAR(50)",  "",   None,          "中心主任姓名"),
])

T["Room"] = dict(cn="诊室表", mod="A", cols=[
    ("CenterID",  "CHAR(4)", "PK,FK", "Center", "所属中心（组合主键）"),
    ("RoomNo",    "CHAR(4)", "PK",    None,     "房间编号（组合主键）"),
    ("SeatCount", "INT",     "",      None,     "座位数量"),
])

T["Resource"] = dict(cn="资源表", mod="A", cols=[
    ("ResourceID",   "CHAR(10)",     "PK", None,     "资源标签编号"),
    ("ResourceName", "VARCHAR(50)",  "",   None,     "资源名称"),
    ("PurchaseDate", "DATE",         "",   None,     "购置日期（可空）"),
    ("Remark",       "VARCHAR(100)", "",   None,     "特殊备注（可空）"),
    ("CenterID",     "CHAR(4)",      "FK", "Center", "所属中心"),
    ("RoomNo",       "CHAR(4)",      "FK", "Room",   "所属诊室"),
])

T["Patient"] = dict(cn="患者表", mod="C", cols=[
    ("PatientID",      "CHAR(8)",      "PK", None, "患者编号"),
    ("FullName",       "VARCHAR(50)",  "",   None, "患者全名"),
    ("MailingAddress", "VARCHAR(100)", "",   None, "邮寄地址"),
    ("Phone",          "VARCHAR(20)",  "",   None, "电话号码"),
    ("Email",          "VARCHAR(50)",  "",   None, "电子邮箱（可空）"),
    ("BirthDate",      "DATE",         "",   None, "出生日期"),
    ("DiagnosisDate",  "DATE",         "",   None, "确诊日期"),
    ("DiabetesType",   "VARCHAR(10)",  "",   None, "糖尿病类型"),
])

T["CDE"] = dict(cn="CDE 表", mod="B", cols=[
    ("CDEID",       "CHAR(8)",     "PK", None, "CDE 编号"),
    ("Name",        "VARCHAR(50)", "",   None, "姓名"),
    ("StaffNo",     "CHAR(9)",     "UK", None, "9 位员工编号"),
    ("HireDate",    "DATE",        "",   None, "入职日期"),
    ("WorkPhone",   "VARCHAR(20)", "",   None, "工作电话"),
    ("HomePhone",   "VARCHAR(20)", "",   None, "家庭电话"),
    ("WorkEmail",   "VARCHAR(50)", "",   None, "工作邮箱"),
    ("MobilePhone", "VARCHAR(20)", "",   None, "手机（可空）"),
])

T["Qualification"] = dict(cn="资质表", mod="B", cols=[
    ("QualID",   "CHAR(4)",     "PK", None, "资质编号"),
    ("QualName", "VARCHAR(30)", "",   None, "资质名称"),
])

T["CDE_Qualification"] = dict(cn="CDE-资质关联表", mod="B", cols=[
    ("CDEID",  "CHAR(8)", "PK,FK", "CDE",           "CDE 编号"),
    ("QualID", "CHAR(4)", "PK,FK", "Qualification", "资质编号"),
])

T["Appointment"] = dict(cn="预约表", mod="D", cols=[
    ("ApptID",       "CHAR(10)",     "PK", None,     "预约编号"),
    ("PatientID",    "CHAR(8)",      "FK", "Patient", "就诊患者"),
    ("CDEID",        "CHAR(8)",      "FK", "CDE",     "接诊 CDE"),
    ("CenterID",     "CHAR(4)",      "FK", "Center",  "所属中心"),
    ("RoomNo",       "CHAR(4)",      "FK", "Room",    "使用诊室"),
    ("ApptDate",     "DATE",         "",   None,     "预约日期"),
    ("ApptTime",     "TIME",         "",   None,     "预约时间"),
    ("Status",       "VARCHAR(6)",   "",   None,     "到诊/改期/取消"),
    ("ClinicalNote", "VARCHAR(200)", "",   None,     "CDE 临床记录"),
])

T["Complication"] = dict(cn="并发症表", mod="C", cols=[
    ("CompID",   "CHAR(4)",     "PK", None, "并发症编号"),
    ("CompName", "VARCHAR(50)", "",   None, "并发症名称"),
])

T["Patient_Complication"] = dict(cn="患者-并发症关联表", mod="C", cols=[
    ("PatientID", "CHAR(8)",      "PK,FK", "Patient",      "患者编号"),
    ("CompID",    "CHAR(4)",      "PK,FK", "Complication", "并发症编号"),
    ("OnsetDate", "DATE",         "",      None,           "发病日期（可空）"),
    ("Remark",    "VARCHAR(100)", "",      None,           "备注（可空）"),
])

T["BloodGlucose"] = dict(cn="血糖读数表", mod="E", cols=[
    ("ReadingID",     "CHAR(12)",     "PK", None,     "读数编号"),
    ("PatientID",     "CHAR(8)",      "FK", "Patient", "患者编号"),
    ("TestDateTime",  "DATETIME",     "UK", None,     "检测日期时间"),
    ("GlucoseValue",  "DECIMAL(4,1)", "",   None,     "血糖值 mmol/L"),
    ("Remark",        "VARCHAR(100)", "",   None,     "异常值原因"),
])

T["Injection"] = dict(cn="胰岛素注射表", mod="E", cols=[
    ("InjectionID", "CHAR(12)", "PK", None,          "注射编号"),
    ("ReadingID",   "CHAR(12)", "FK,UK", "BloodGlucose", "对应血糖读数"),
    ("InjType",     "VARCHAR(6)", "", None,          "餐时/基础"),
    ("Units",       "INT",        "", None,          "注射单位数"),
    ("InjTime",     "DATETIME",   "", None,          "注射时间"),
])

T["Nutrition"] = dict(cn="营养记录表", mod="F", cols=[
    ("NutriID",      "CHAR(12)",     "PK", None,     "记录编号"),
    ("PatientID",    "CHAR(8)",      "FK", "Patient", "患者编号"),
    ("NutriDate",    "DATE",         "",   None,     "记录日期"),
    ("MealCount",    "INT",          "",   None,     "进餐次数"),
    ("TotalCalorie", "INT",          "",   None,     "总热量 kcal"),
    ("FatRatio",     "DECIMAL(3,1)", "",   None,     "脂肪比例 %"),
    ("ProteinRatio", "DECIMAL(3,1)", "",   None,     "蛋白质比例 %"),
    ("CarbRatio",    "DECIMAL(3,1)", "",   None,     "碳水比例 %"),
])

# 布局: 表 -> (x, y)
POS = {
    "Center": (80, 150), "Room": (80, 392), "Resource": (470, 392),
    "CDE": (940, 150), "Qualification": (940, 440), "CDE_Qualification": (940, 594),
    "Patient": (1800, 150), "Complication": (1800, 440), "Patient_Complication": (1800, 594),
    "Appointment": (80, 830),
    "BloodGlucose": (940, 830), "Injection": (1330, 830),
    "Nutrition": (1800, 830),
}

MODULES = [
    ("A", "01", "中心与诊室", "CENTER · ROOM · RESOURCE", "cyan"),
    ("B", "02", "临床人员",   "CDE · QUALIFICATION",      "pink"),
    ("C", "03", "患者与并发症", "PATIENT · COMPLICATION",  "green"),
    ("D", "04", "预约",       "APPOINTMENT",             "amber"),
    ("E", "05", "血糖与胰岛素", "BLOOD GLUCOSE · INJECTION", "blue"),
    ("F", "06", "营养记录",   "NUTRITION",               "purple"),
]
MOD_OF = {k: v["mod"] for k, v in T.items()}

# 关系: (主表, 端类型, 偏移, 从表, 端类型, 偏移, 走线, 基数标签)
# 走线: "V" 直线竖直 / "H" 直线水平 / list of 中间拐点
EDGES = [
    ("Center", "B", 180, "Room", "T", 180, "V", ("1", "N")),
    ("Center", "R", 150, "Resource", "L", 96, [455], ("1", "N")),
    ("Room", "R", 60, "Resource", "L", 60, "H", ("1", "N")),
    ("CDE", "L", 180, "CDE_Qualification", "L", 50, [920], ("1", "N")),
    ("Qualification", "B", 180, "CDE_Qualification", "T", 180, "V", ("1", "N")),
    ("Patient", "R", 150, "Patient_Complication", "R", 64, [2172], ("1", "N")),
    ("Complication", "B", 180, "Patient_Complication", "T", 180, "V", ("1", "N")),
    ("Patient", "L", 30, "Appointment", "T", 540, "BUSY", ("1", "N")),
    ("Center", "L", 130, "Appointment", "L", 70, [34], ("1", "N")),
    ("Room", "B", 80, "Appointment", "T", 80, "V", ("1", "N")),
    ("CDE", "L", 100, "Appointment", "T", 280, "BUSY2", ("1", "N")),
    ("Patient", "L", 90, "BloodGlucose", "T", 180, "BUSY3", ("1", "N")),
    ("Patient", "R", 100, "Nutrition", "T", 260, [2200], ("1", "N")),
    ("BloodGlucose", "R", 81, "Injection", "L", 81, "H", ("1", "1")),
]

# 类图操作
OPS_MAP = {
    "Center": "+ 统计诊室()  + 查询资源()",
    "Room": "+ 查询可用时段()  + 检查冲突()",
    "Resource": "+ 登记资源()  + 变更所属()",
    "Patient": "+ 登记患者()  + 查询历史读数()",
    "CDE": "+ 维护资质()  + 接诊预约()",
    "Qualification": "+ 授予()  + 撤销()",
    "CDE_Qualification": "+ 校验资质有效性()",
    "Appointment": "+ 创建预约()  + 变更状态()",
    "Complication": "+ 分类()  + 统计发病率()",
    "Patient_Complication": "+ 记录发病()  + 更新备注()",
    "BloodGlucose": "+ 校验唯一性()  + 判定异常()",
    "Injection": "+ 关联读数()  + 计算总量()",
    "Nutrition": "+ 计算比例合计()  + 校验完整性()",
}
# 类图中文名
CN_CLASS = {
    "Center": "中心", "Room": "诊室", "Resource": "资源",
    "Patient": "患者", "CDE": "糖尿病教育师", "Qualification": "专业资质",
    "CDE_Qualification": "CDE-资质关联", "Appointment": "预约",
    "Complication": "并发症", "Patient_Complication": "患者-并发症关联",
    "BloodGlucose": "血糖读数", "Injection": "胰岛素注射", "Nutrition": "营养记录",
}

# ---------------------------------------------------------------- 工具
def esc(s):
    return html.escape(str(s), quote=True)

try:
    from PIL import ImageFont
    _FONTS = {}

    def _font(size, bold):
        k = (size, bold)
        if k not in _FONTS:
            p = r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"
            _FONTS[k] = ImageFont.truetype(p, max(8, int(round(size * 4))))
        return _FONTS[k]

    def _w_ascii(s, size, bold):
        return _font(size, bold).getlength(s) / 4.0
except Exception:                                            # 无 Pillow 时退化为估算
    def _w_ascii(s, size, bold):
        return sum(size * (0.60 if bold else 0.545) for _ in s)

def tw(s, size, bold=False):
    """混排宽度：CJK 按字身宽，西文用真实字形宽度"""
    total, buf = 0.0, ""
    for c in str(s):
        if ord(c) > 0x2E80:
            if buf:
                total += _w_ascii(buf, size, bold); buf = ""
            total += size * 1.0
        else:
            buf += c
    if buf:
        total += _w_ascii(buf, size, bold)
    return total * 1.07

def box_of(name, extra=0):
    x, y = POS[name]
    return (x, y, W, ch(len(T[name]["cols"]), extra))

def anchor(name, side, off, extra=0):
    x, y, w, h = box_of(name, extra)
    if side == "T": return (x + off, y)
    if side == "B": return (x + off, y + h)
    if side == "L": return (x, y + off)
    return (x + w, y + off)

def poly(points, stroke=LINE, width=1.3, dash=None):
    d = " ".join(("M" if i == 0 else "L") + f"{p[0]:.1f},{p[1]:.1f}" for i, p in enumerate(points))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{da}/>'

def crow_foot(pt, toward, size=11, color=LINE):
    """在三叉末端画 crow's foot, toward 为指向卡片的方向向量"""
    tx, ty = toward
    n = math.hypot(tx, ty) or 1
    tx, ty = tx / n, ty / n
    px, py = -ty, tx
    x, y = pt
    out = []
    for s in (-1, 0, 1):
        ex = x - tx * size + px * s * size * 1.15
        ey = y - ty * size + py * s * size * 0.92
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="1.15" stroke-linecap="round"/>')
    return "".join(out)

def one_mark(pt, toward, color=LINE, gap=3.5):
    """「恰一」端：垂直短线（垂直于连线方向）"""
    tx, ty = toward
    n = math.hypot(tx, ty) or 1
    tx, ty = tx / n, ty / n
    px, py = -ty, tx
    cx, cy = pt[0] - tx * gap, pt[1] - ty * gap
    return (f'<line x1="{cx-px*5.5:.1f}" y1="{cy-py*5.5:.1f}" x2="{cx+px*5.5:.1f}" y2="{cy+py*5.5:.1f}" '
            f'stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>')

def two_marks(pt, toward, color=LINE, gap=3.0):
    """「恰一」强制端：双短线"""
    return one_mark(pt, toward, color, gap) + one_mark(pt, toward, color, gap + 6.5)

def key_icon(x, y, color="#B08A2E"):
    return (f'<g transform="translate({x:.1f},{y:.1f})" stroke="{color}" stroke-width="1.15" fill="none" stroke-linecap="round">'
            f'<circle cx="3" cy="3" r="2.4"/><path d="M4.7,4.7 L4.7,9.6"/><path d="M4.7,7.1 L7.4,7.1"/><path d="M4.7,9.0 L6.6,9.0"/></g>')

def fk_arrow(x, y, color="#6E7F96"):
    return (f'<g transform="translate({x:.1f},{y:.1f})" fill="{color}">'
            f'<path d="M0,0.4 L6.4,3.4 L0,6.4 Z"/></g>')

def uk_mark(x, y, color="#8D9AAB"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="7.6" font-weight="600" '
            f'fill="{color}" letter-spacing="0.4">UQ</text>')

def txt(x, y, s, size=11, color=INK, weight="400", anchor="start", family=None, ls=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family or FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{a}{l}>{esc(s)}</text>')

# ---------------------------------------------------------------- 卡片
def card_header_path(x, y, w, h, r=8):
    return (f'M{x},{y+h} L{x},{y+r} Q{x},{y} {x+r},{y} L{x+w-r},{y} '
            f'Q{x+w},{y} {x+w},{y+r} L{x+w},{y+h} Z')

UML_TYPE = {"CHAR": "String", "VARCHAR": "String", "DATE": "Date",
            "TIME": "Time", "DATETIME": "DateTime", "INT": "int",
            "DECIMAL": "Decimal"}

def uml_type(t):
    return UML_TYPE.get(t.split("(")[0].strip().upper(), t)


def draw_card(name, mode, extra=0):
    """mode: 'erd' | 'class'"""
    x, y, w, h = box_of(name, extra)
    t = T[name]
    pal = PALETTE[[m[4] for m in MODULES if m[0] == t["mod"]][0]]
    out = []
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" '
               f'stroke="#D7DFE9" stroke-width="1" filter="url(#cardShadow)"/>')
    out.append(f'<path d="{card_header_path(x, y, w, HEAD)}" fill="#F8FAFC"/>')
    out.append(f'<path d="M{x},{y+HEAD} L{x+w},{y+HEAD}" stroke="{pal["stroke"]}" stroke-width="2"/>')
    out.append(f'<path d="M{x},{y+HEAD} L{x+w},{y+HEAD}" stroke="#E6ECF3" stroke-width="0.6"/>')

    if mode == "erd":
        out.append(txt(x + 14, y + 24, name, 13.2, "#16202E", "700", ls="0.3"))
        out.append(txt(x + 14, y + 40, t["cn"], 10.2, SUB))
        out.append(txt(x + w - 14, y + 24, f'{len(t["cols"])} 字段', 9.2, MUTED, "400", "end"))
        out.append(txt(x + w - 14, y + 40, "TABLE", 8.4, "#C3CCD8", "600", "end", ls="1.2"))
    else:
        out.append(txt(x + w / 2, y + 16, "«entity»", 9.6, pal["ink"], "600", "middle", ls="1.0"))
        nw = tw(name, 13.6, True) + tw(CN_CLASS[name], 9.6) + 12
        sx = x + (w - nw) / 2
        out.append(txt(sx, y + 36, name, 13.6, "#16202E", "700"))
        out.append(txt(sx + tw(name, 13.6, True) + 9, y + 36, CN_CLASS[name], 9.6, SUB))

    # 字段行
    for i, (cname, ctype, key, ref, cn) in enumerate(t["cols"]):
        ry = y + HEAD + i * ROW
        base = ry + ROW - 7
        if i: out.append(f'<path d="M{x+10},{ry} L{x+w-10},{ry}" stroke="#F1F4F8" stroke-width="1"/>')
        if mode == "erd":
            out.append(txt(x + 14, base, cname, 11.2, "#1F2A37", "500"))
            cx = x + 14 + tw(cname, 11.2, False) + 10
            if "PK" in key:
                out.append(key_icon(cx, ry + 5)); cx += 17
            if "FK" in key:
                out.append(fk_arrow(cx, ry + 6.4)); cx += 10
                out.append(txt(cx, base, ref.upper(), 9.0, "#62748C", "600", ls="0.3")); cx += tw(ref.upper(), 9.0, True) + 0.3 * len(ref) + 12
            if "UK" in key:
                out.append(uk_mark(cx, base))
            out.append(txt(x + w - 14, base, ctype, 9.6, "#8C99AA", "400", "end"))
        else:
            out.append(txt(x + 14, base, f'− {cname}', 11.0, "#1F2A37", "500"))
            tag = ""
            if "PK" in key: tag = "{PK}"
            elif "FK" in key: tag = "{FK}"
            elif "UK" in key: tag = "{UQ}"
            if tag:
                out.append(txt(x + 14 + tw(f'− {cname}', 11.0, False) + 9, base, tag, 8.6, "#9AA7B8", "600"))
            out.append(txt(x + w - 14, base, uml_type(ctype), 9.6, "#8C99AA", "400", "end"))

    # 类图操作分区
    if mode == "class":
        oy = y + HEAD + len(t["cols"]) * ROW
        out.append(f'<path d="M{x},{oy} L{x+w},{oy}" stroke="#E3E9F1" stroke-width="1"/>')
        out.append(txt(x + 14, oy + 19, OPS_MAP[name], 9.8, "#4B6B8A"))

    return "".join(out)

# ---------------------------------------------------------------- 模块分区
def draw_module(mod_id, num, cn, en, colorkey, extra=0):
    pal = PALETTE[colorkey]
    names = [k for k, v in T.items() if v["mod"] == mod_id]
    xs, ys = [], []
    for n in names:
        x, y, w, h = box_of(n, extra)
        xs += [x, x + w]; ys += [y, y + h]
    pad_x, pad_top, pad_bot = 32, 46, 30
    gx, gy = min(xs) - pad_x, min(ys) - pad_top
    gw, gh = max(xs) - min(xs) + pad_x * 2, max(ys) - min(ys) + pad_top + pad_bot
    out = [f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="18" fill="{pal["fill"]}" stroke="{pal["stroke"]}" stroke-width="1.2"/>']
    out.append(f'<circle cx="{gx+22}" cy="{gy+24}" r="3.4" fill="{pal["dot"]}"/>')
    out.append(txt(gx + 34, gy + 28, f'{num}  {cn}', 11.6, pal["ink"], "700", ls="0.4"))
    out.append(txt(gx + 34 + tw(f'{num}  {cn}', 11.6, True) + 10, gy + 28, en, 8.8, pal["ink"], "500", ls="1.1"))
    return "".join(out)

# ---------------------------------------------------------------- 连线
def route(edge, extra=0, mode="erd"):
    a, s1, o1, b, s2, o2, way, card = edge
    p1 = anchor(a, s1, o1, extra)
    p2 = anchor(b, s2, o2, extra)
    pts = [p1]
    if way == "V":
        pts.append(p2)
    elif way == "H":
        pts.append(p2)
    elif way == "BUSY":      # 左出 → 下 → 横穿走廊 → 下入顶
        xb, yb = 1740, 770
        pts += [(xb, p1[1]), (xb, yb), (p2[0], yb), p2]
    elif way == "BUSY2":
        xb, yb = 884, 728
        pts += [(xb, p1[1]), (xb, yb), (p2[0], yb), p2]
    elif way == "BUSY3":
        xb, yb = 1700, 748
        pts += [(xb, p1[1]), (xb, yb), (p2[0], yb), p2]
    else:
        mx = way[0]
        pts += [(mx, p1[1]), (mx, p2[1]), p2]
    return pts, card

def draw_edges(extra=0, mode="erd"):
    out = []
    for edge in EDGES:
        pts, (ca, cb) = route(edge, extra, mode)
        a, s1, o1, b, s2, o2, way, _ = edge
        color = "#B9C4D1" if mode == "class" else "#9FAAB8"
        out.append(poly(pts, stroke=color))
        # 端点朝向
        d1 = (pts[0][0] - pts[1][0], pts[0][1] - pts[1][1])
        d2 = (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
        if mode == "erd":
            if cb == "1":
                out.append(two_marks(pts[-1], d2, color))
            else:
                out.append(crow_foot(pts[-1], d2, 9.5, color))
            out.append(one_mark(pts[0], d1, color))
            if cb == "1":   # 1:1 标注
                lx, ly = pts[-1][0], pts[-1][1]
                if abs(d2[0]) < abs(d2[1]):
                    out.append(txt(lx + 8, ly - 8, "1:1", 8.6, "#8C99AA", "600"))
                else:
                    out.append(txt(lx - 8, ly - 9, "1:1", 8.6, "#8C99AA", "600", "end"))
        else:
            if (a, b) in (("Center", "Room"), ("Room", "Resource")):
                cx0, cy0 = pts[0]
                ang = math.atan2(-d1[1], -d1[0])
                out.append(diamond(cx0, cy0, ang, color, fill="#9FB0C2"))
                s1c = "1"; s2c = "1..*"
            else:
                s1c, s2c = ("1", "0..1") if (a, b) == ("BloodGlucose", "Injection") else ("1", "1..*")
            out.append(mult(pts[0], pts[1], s1c, color, -1))
            out.append(mult(pts[-1], pts[-2], s2c, color, 1))
    return "".join(out)

def mult(pt, prev, s, color="#8A97A8", side=1, along=13.0):
    """多重性标注：沿连线内缩 along，垂直方向偏移 9px（side=1 右/下，-1 左/上）"""
    dx, dy = pt[0] - prev[0], pt[1] - prev[1]
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    bx, by = pt[0] - ux * along, pt[1] - uy * along
    if abs(ux) < abs(uy):                      # 竖直段
        if side > 0:
            return txt(bx + 9, by + 3.4, s, 9.2, color, "600", "start")
        return txt(bx - 9, by + 3.4, s, 9.2, color, "600", "end")
    if side > 0:                               # 水平段
        return txt(bx, by + 15, s, 9.2, color, "600", "middle")
    return txt(bx, by - 8, s, 9.2, color, "600", "middle")


def diamond(x, y, ang, color, fill="#FFFFFF"):
    """组合菱形，长轴沿 ang 方向"""
    L, Wd = 15, 6.5
    ca, sa = math.cos(ang), math.sin(ang)
    def pt(t, u):
        return (x + ca * t - sa * u, y + sa * t + ca * u)
    a1 = pt(0, 0); a2 = pt(L * 0.5, Wd); a3 = pt(L, 0); a4 = pt(L * 0.5, -Wd)
    d = f'M{a1[0]:.1f},{a1[1]:.1f} L{a2[0]:.1f},{a2[1]:.1f} L{a3[0]:.1f},{a3[1]:.1f} L{a4[0]:.1f},{a4[1]:.1f} Z'
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="1.2"/>'

# ---------------------------------------------------------------- 图例
def legend(x, y, mode):
    """底部横向图例条"""
    w, h = 1068, 52
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#FFFFFF" stroke="#E1E7EF" stroke-width="1" stroke-dasharray="5 4"/>']
    o.append(txt(x + 20, y + 31, "图例", 10.2, "#7C8899", "700", ls="1.2"))
    o.append(txt(x + 58, y + 31, "LEGEND", 8.6, "#B3BDCA", "600", ls="1.4"))
    yy = y + 28
    if mode == "erd":
        items = [("key", x + 128, "主键"), ("fk", x + 268, "外键 → 被引用表"),
                 ("crow", x + 476, "一对多 1:N"), ("one", x + 620, "一对一 1:1"),
                 ("uQ", x + 748, "唯一约束")]
    else:
        items = [("diam", x + 128, "组合 Composition"), ("many", x + 316, "多重性"),
                 ("ent", x + 500, "「entity」实体类"), ("dash", x + 676, "关联类 / 关联表")]
    for kind, ix, label in items:
        if kind == "key":
            o.append(key_icon(ix, yy - 9))
        elif kind == "fk":
            o.append(fk_arrow(ix, yy - 5))
        elif kind == "crow":
            o.append(crow_foot((ix + 4, yy - 3), (1, 0), 8))
        elif kind == "one":
            o.append(one_mark((ix + 4, yy - 3), (-1, 0)))
        elif kind == "uQ":
            o.append(uk_mark(ix, yy))
        elif kind == "diam":
            o.append(f'<path d="M{ix},{yy-4} L{ix+8},{yy-9} L{ix+16},{yy-4} L{ix+8},{yy+1} Z" fill="#9FB0C2" stroke="#8FA0B4"/>')
        elif kind == "many":
            o.append(txt(ix, yy, "1", 9.2, "#8A97A8", "600"))
            o.append(f'<path d="M{ix+12},{yy} L{ix+34},{yy}" stroke="#B9C4D1" stroke-width="1.2"/>')
            o.append(txt(ix + 38, yy, "1..*", 9.2, "#8A97A8", "600"))
        elif kind == "dash":
            o.append(f'<path d="M{ix},{yy-3} L{ix+26},{yy-3}" stroke="#B9C4D1" stroke-width="1.3" stroke-dasharray="4 3"/>')
        off = {"key": 22, "fk": 22, "crow": 22, "one": 22, "uQ": 22, "diam": 22, "dash": 34}.get(kind, 0)
        if kind == "many":
            o.append(txt(ix + 74, yy, label, 10.2, SUB))
        else:
            o.append(txt(ix + off, yy, label, 10.2, SUB))
    o.append(f'<path d="M{x+108.5},{y+14} L{x+108.5},{y+38}" stroke="#E8EDF3" stroke-width="1"/>')
    o.append(f'<path d="M{x+246},{y+14} L{x+246},{y+38}" stroke="#E8EDF3" stroke-width="1"/>')
    return "".join(o)


# ---------------------------------------------------------------- 画布
def canvas(title, subtitle, mode):
    extra = OPS if mode == "class" else 0
    cw, chh = 2250, 1210 if mode == "erd" else 1234
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{chh}" viewBox="0 0 {cw} {chh}">']
    out.append('''<defs>
<filter id="cardShadow" x="-20%" y="-20%" width="150%" height="150%">
  <feDropShadow dx="0" dy="1.6" stdDeviation="2.4" flood-color="#7A8797" flood-opacity="0.14"/>
</filter></defs>''')
    out.append(f'<rect width="{cw}" height="{chh}" fill="#FBFCFD"/>')
    # 标题
    out.append(f'<rect x="0" y="0" width="{cw}" height="82" fill="#FFFFFF"/>')
    out.append(f'<path d="M0,82 L{cw},82" stroke="#E8EDF3" stroke-width="1"/>')
    out.append(f'<rect x="0" y="0" width="5" height="82" fill="#2E6E8E"/>')
    out.append(txt(48, 38, title, 21, "#16202E", "700", ls="0.3"))
    out.append(txt(48, 62, subtitle, 11.2, "#7C8899"))
    out.append(txt(cw - 48, 32, "Clearbrook 糖尿病中心 · 集中数据库系统", 10.6, "#5B6675", "600", "end", ls="0.6"))
    out.append(txt(cw - 48, 52, "信管2401班 · 1602240110 · 刘洋", 10.2, "#93A0B0", "400", "end"))
    out.append(txt(cw - 48, 70, "版本 1.0 / 2026-10", 9.2, "#B3BDCA", "400", "end"))

    for m in MODULES:
        out.append(draw_module(*m, extra=extra))
    out.append(draw_edges(extra=extra, mode=mode))
    for name in T:
        out.append(draw_card(name, mode, extra=extra))
    out.append(legend(1120, 1136, mode))
    out.append('</svg>')
    return "".join(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    # ---- 类图（先画，用类图说明分析模型）
    svg = canvas("CDC 核心域实体类图  ·  Analysis Class Diagram",
                 "分析建模：13 个实体类（含 2 个关联类）· 6 个业务模块分区 · 属性—关联—多重性",
                 "class")
    open(os.path.join(OUT, "class-diagram.svg"), "w", encoding="utf-8").write(svg)

    # ---- ERD
    svg = canvas("CDC 集中数据库  ·  Entity Relationship Diagram",
                 "设计建模：13 张表 · 68 个字段 · 14 条外键关系 · 由核心域类图按「类→表、属性→列、关联→外键」映射",
                 "erd")
    open(os.path.join(OUT, "erd.svg"), "w", encoding="utf-8").write(svg)
    print("done")
