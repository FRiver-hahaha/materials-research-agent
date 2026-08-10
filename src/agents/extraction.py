"""知识抽取 Agent：从解析文本中规则化抽取结构化实体与证据对象。
抽取维度：成分(composition) / 性质(property) / 方法(method) / 条件(condition)。
设计原则：泛化规则优先（不绑定特定配方白名单），兼容真实文献的 LaTeX 公式写法
（如 Cs_a FA_b MA_(1-a-b) Pb(Br_y I_(1-y))_3 这类带下标/合金比例的写法）。
关键消歧：性质/方法按「同段中最接近的化学式」归属到具体材料，避免比较句误归因。"""
import re
from src.agents.state import AgentState, Entity, Evidence

# 化学式片段：大写元素符号开头，后续为元素/数字/下标/括号/LaTeX 字符组成的片段
_SUBS = "₀₁₂₃₄₅₆₇₈₉"          # Unicode 下标数字
_LATIN_SUB = "ₐₑₒₓₔ"           # Unicode 下标字母
_SUBTRANS = str.maketrans(_SUBS, "0123456789")
_FORMULA_FRAG = re.compile(
    r"[A-Z][a-z]?[\w" + _SUBS + _LATIN_SUB + r".(){}\[\]\\^+\-]*"
)
_BANDGAP = re.compile(
    r"(?:band[\s\-]?gap|E_g|Eg|bandgap)[^0-9a-zA-Z]{0,15}?(?:of\s|equal\s?to\s|≈|≈\s)?([0-9]+(?:\.[0-9]+)?)\s*(?:[\u00B1\u00B1]?\s*[0-9]+(?:\.[0-9]+)?\s*)?(eV|electron[\s\-]?volt)",
    re.I)
_STABILITY = re.compile(r"(phase[\s\-]?stab|thermal[\s\-]?stab|stab(?:le|ility)|degrad|decomposition)", re.I)
_METHOD = re.compile(r"\b(DFT|density functional|molecular dynamics|MD|GGA|HSE06|HSE|PBE|first[\s-]?principles|Machine Learning Potential|MLP|ab[\s-]?initio|spin[\s-]?orbit|SCAN|VASP)\b", re.I)

# 元素符号白名单（用于过滤噪声片段）
_ELEMENTS = {
    "H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar",
    "K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br",
    "Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te",
    "I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm",
    "Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn",
    "Fr","Ra","Ac","Th","Pa","U","MA","FA","FA","GA",
}
_NOISE = {"Si","In","As","Of","Or","And","The","For","With","This","That","Figure","Table","Eq"}


def _clean_formula(raw):
    s = raw.replace("\\mathrm", "").replace("{", "").replace("}", "")
    s = re.sub(r"\\[a-zA-Z]+", "", s)           # 去掉剩余 LaTeX 命令（如 \mathrm 残留）
    s = s.replace("$", "").replace("\\", "").replace("_", "").strip()
    s = re.sub(r"[" + _LATIN_SUB + r"]", "", s)  # 丢弃下标字母噪声
    s = s.translate(_SUBTRANS)                   # Unicode 下标数字 -> ASCII
    # 剥除尾随标点/括号噪声（WBG) -> WBG, PSCs. -> PSCs）
    s = s.rstrip(").],.;:")
    # 碘(I) 被误识别为小写 l 的校正：仅当 l 后接数字且前导非 C/F/A/T（保护 Cl/Al/Tl/Fl）
    s = re.sub(r"(?<!C|F|A|T)l(\d)", r"I\1", s)
    return s


# 典型光电/钙钛矿材料金属（排除 Y/La 等通用稀土，避免 STABILITY 类单词误判）
_METALS = {"Li","Na","K","Rb","Cs","Mg","Ca","Sr","Ba","Al","Ga","In",
           "Sn","Pb","Bi","Cu","Ag","Au","Zn","Cd","Ti","Zr","Hf","V","Nb",
           "Ta","Cr","Mo","W","Mn","Fe","Co","Ni","Ru","Rh","Pd","Ir","Pt",
           "MA","FA","GA"}
# 阴离子/配位（材料体系必有其一）
_ANIONS = {"O","S","Se","Te","F","Cl","Br","I","N","P","C","H","B"}
# 明确噪声黑名单（缩写单词/章节标记）
_BLACKLIST = {"WBG","MPP","PCE","PSCs","PVSK","STABILITY","Sin","UV","Cells","School",
              "Tech","Center","Science","Technology","Interface","Recommendations",
              "ABSTRACT","ACCESS","Article","JPCC","Currently","However","Although",
              "They","Figure","Table","Eq","Phase","READ","More","Sn2","Sn4","FA"}

def _is_plausible_formula(name):
    """过滤噪声：真正的材料配方需同时含金属(阳离子)与阴离子(卤素/氧硫等)迹象，
    或明确的合金/比例写法；纯缩写单词(PCE/WBG/MPP)与噪声被剔除。"""
    if len(name) < 3:
        return False
    # 剔除含上标符号或不完整括号的残缺片段（如 FA^+(HC(NH2)2^+、PEA(I0.25SCN0.75）
    if "^" in name or name.startswith("(") or name.count("(") != name.count(")"):
        return False
    if name in _BLACKLIST or name.lower() in {x.lower() for x in _NOISE}:
        return False
    clean = name.rstrip(").].,")
    tokens = re.findall(r"[A-Z][a-z]?", clean)
    has_metal = any(t in _METALS for t in tokens)
    has_anion = any(t in _ANIONS for t in tokens)
    if has_metal and has_anion:
        return True
    # 含数字/下标且长度够，视为合金比例写法（如 FA0.83Cs0.17PbI3）
    if re.search(r"[0-9₀₁₂₃₄₅₆₇₈₉]", clean) and len(clean) >= 4:
        return True
    return False


def _find_snippet(text, token):
    i = text.lower().find(token.lower())
    if i < 0:
        return text[:120]
    return text[max(0, i - 40): i + 90].replace("\n", " ")


def _nearest(spans, pos):
    best, best_d = None, 1 << 30
    for name, start in spans:
        d = abs(pos - start)
        if d < best_d:
            best, best_d = name, d
    return best


def _formula_candidates(text):
    """返回 (归一化名, 起始位置) 列表（去重，按出现顺序）。"""
    out = []
    seen = set()
    for m in _FORMULA_FRAG.finditer(text):
        name = _clean_formula(m.group(0))
        if not _is_plausible_formula(name):
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append((name, m.start()))
    return out


def regex_extract_section(state, ev_store, entity_db, pid, p, sec_name, sec_text, page, ev_counter):
    """单段落正则抽取（LLM 抽取失败时降级复用）。"""
    formula_spans = _formula_candidates(sec_text)

    # 成分实体
    for name, start in formula_spans:
        ev_counter[0] += 1
        eid = f"EV{ev_counter[0]:03d}"
        ev = Evidence(eid, pid, p.title, page, _find_snippet(sec_text, name),
                      None, None, None, section=sec_name)
        ev_store.put(ev)
        state.evidence[eid] = ev
        entity_db.add(Entity("composition", name, name, evidence_id=eid,
                             paper_id=pid, section=sec_name))

    # 带隙性质（归属最近化学式）
    for m in _BANDGAP.finditer(sec_text):
        val, unit = float(m.group(1)), "eV"
        comp = _nearest(formula_spans, m.start())
        ev_counter[0] += 1
        eid = f"EV{ev_counter[0]:03d}"
        ev = Evidence(eid, pid, p.title, page, _find_snippet(sec_text, m.group(0)),
                      val, unit, None, section=sec_name)
        ev_store.put(ev)
        state.evidence[eid] = ev
        entity_db.add(Entity("property", "bandgap", "bandgap", val, unit, eid,
                             paper_id=pid, section=sec_name, composition=comp))

    # 稳定性性质标记
    for m in _STABILITY.finditer(sec_text):
        comp = _nearest(formula_spans, m.start())
        ev_counter[0] += 1
        eid = f"EV{ev_counter[0]:03d}"
        ev = Evidence(eid, pid, p.title, page, _find_snippet(sec_text, m.group(0)),
                      None, None, "stability-context", section=sec_name)
        ev_store.put(ev)
        state.evidence[eid] = ev
        entity_db.add(Entity("property", "phase_stability", "phase_stability",
                             evidence_id=eid, paper_id=pid, section=sec_name, composition=comp))

    # 方法（归属最近化学式）
    for m in _METHOD.finditer(sec_text):
        comp = _nearest(formula_spans, m.start())
        ev_counter[0] += 1
        eid = f"EV{ev_counter[0]:03d}"
        ev = Evidence(eid, pid, p.title, page, _find_snippet(sec_text, m.group(0)),
                      None, None, None, section=sec_name)
        ev_store.put(ev)
        state.evidence[eid] = ev
        entity_db.add(Entity("method", m.group(0), m.group(0).upper(), evidence_id=eid,
                             paper_id=pid, section=sec_name, composition=comp))


def extract(state: AgentState, ev_store, entity_db) -> AgentState:
    """规则式抽取入口（无真实 LLM 时使用）。"""
    ev_counter = [0]
    for pid in state.filtered_ids:
        p = state.papers.get(pid)
        if not p:
            continue
        page_guess = 1
        for sec_name, sec_text in p.parsed.get("sections", {}).items():
            if not isinstance(sec_text, str) or not sec_text.strip():
                continue
            regex_extract_section(state, ev_store, entity_db, pid, p, sec_name, sec_text, page_guess, ev_counter)
    state.entities = entity_db.all()
    state.log(f"[extract] 抽取实体 {len(state.entities)} 条，证据 {len(state.evidence)} 条")
    return state
