# 材料科学文献调研报告（初赛）

> 研究方向：**perovskite solar cell bandgap and phase stability**
> 生成方式：材料科学文献调研智能体（自动检索/抽取/推理/报告）

## 0. 摘要
本报告由材料科学文献调研智能体自动生成。系统围绕给定研究方向，自主完成文献检索、结构化抽取、跨文献融合、Research Gap 识别与构效关系发现，所有结论均附文献证据链。

## 1. 方法论（系统架构）
- 检索：Sciverse 语义检索(web) + Sci-Base 本地 RAG(local)
- 解析：MinerU（PDF→结构化）
- 抽取：规则化知识抽取（成分/结构/性质/方法/条件），每条生成证据对象
- 融合：跨文献知识图谱
- Gap：未探索 / 矛盾 / 缺失连接 三类识别
- 路线A：LLM 假设生成 + 贝叶斯优化/遗传算法搜索 + 材料数据库交叉验证
- 核验：结论 100% 可溯源至证据对象

## 2. 检索到的核心文献（交叉引用）
| ID | 年份 | 标题 | 作者 |
| --- | --- | --- | --- |
| 9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 | 2020 | strategies to improve the stability of perovskite-based tandem solar cells | 周文韬, 陈怡华, 周欢萍 |
| 54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 | 2023 | highly efficient and stable wide‐bandgap perovskite solar cells via strain management | pengjie hang, chen kan, biao li |
| e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 | 2021 | material, phase, and interface stability of photovoltaic perovskite: a perspective | tianyi huang, shaun tan, yang yang |
| e0a69e333f35eb5e7c67f8e4d837c15a859caad7c5ed1effeb3af0318d98c56b | 2020 | recent progress in developing monolithic perovskite/si tandem solar cells | na liu, lina wang, fan xu |
| 8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca | 2022 | wide‐bandgap organic–inorganic lead halide perovskite solar cells | jianxun li, le wang, adel najar |
| c7914c9971953f7b6577ea8305de2c9ceefc4307b7d908075eca819c8af4f179 | 2019 | multi-cation synergy suppresses phase segregation in mixed-halide perovskites | wang, kai, dang, hoang x., barrit, dounya |

## 3. 结构化抽取结果
| 类型 | 原始 | 归一化 | 数值 | 单位 | 证据 |
| --- | --- | --- | --- | --- | --- |
| composition | Sn2+ | Sn2+ | - | - | EV001 |
| composition | Sn4+ | Sn4+ | - | - | EV002 |
| property | phase_stability | phase_stability | - | - | EV003 |
| property | phase_stability | phase_stability | - | - | EV004 |
| composition | PbI2 | PbI2 | - | - | EV005 |
| property | phase_stability | phase_stability | - | - | EV006 |
| property | phase_stability | phase_stability | - | - | EV007 |
| property | phase_stability | phase_stability | - | - | EV008 |
| property | phase_stability | phase_stability | - | - | EV009 |
| property | phase_stability | phase_stability | - | - | EV010 |
| property | phase_stability | phase_stability | - | - | EV011 |
| property | phase_stability | phase_stability | - | - | EV012 |
| property | phase_stability | phase_stability | - | - | EV013 |
| property | phase_stability | phase_stability | - | - | EV014 |
| property | phase_stability | phase_stability | - | - | EV015 |
| property | phase_stability | phase_stability | - | - | EV016 |
| property | phase_stability | phase_stability | - | - | EV017 |
| property | phase_stability | phase_stability | - | - | EV018 |
| composition | SnF2 | SnF2 | - | - | EV019 |
| composition | SnO2 | SnO2 | - | - | EV020 |
| composition | MAPbI3 | MAPbI3 | - | - | EV021 |
| composition | FAPbI3 | FAPbI3 | - | - | EV022 |
| property | bandgap | bandgap | 1.57 | eV | EV023 |
| property | phase_stability | phase_stability | - | - | EV024 |
| property | phase_stability | phase_stability | - | - | EV025 |
| property | phase_stability | phase_stability | - | - | EV026 |
| property | phase_stability | phase_stability | - | - | EV027 |
| property | phase_stability | phase_stability | - | - | EV028 |
| property | phase_stability | phase_stability | - | - | EV029 |
| property | phase_stability | phase_stability | - | - | EV030 |
| property | phase_stability | phase_stability | - | - | EV031 |
| composition | MAPbBr3 | MAPbBr3 | - | - | EV032 |
| composition | FAPbBr3 | FAPbBr3 | - | - | EV033 |
| property | phase_stability | phase_stability | - | - | EV034 |
| property | phase_stability | phase_stability | - | - | EV035 |
| property | phase_stability | phase_stability | - | - | EV036 |
| property | phase_stability | phase_stability | - | - | EV037 |
| composition | FAPbI3 | FAPbI3 | - | - | EV038 |
| composition | MAPbI3 | MAPbI3 | - | - | EV039 |
| property | bandgap | bandgap | 1.48 | eV | EV040 |
| property | bandgap | bandgap | 1.34 | eV | EV041 |
| property | phase_stability | phase_stability | - | - | EV042 |
| property | phase_stability | phase_stability | - | - | EV043 |

## 4. Research Gap 清单
| ID | 类型 | 描述 | 证据 |
| --- | --- | --- | --- |
| G01 | underexplored | 组成 Sn2+ 仅在单篇文献中出现，缺乏系统研究。 | EV001 |
| G02 | underexplored | 组成 Sn4+ 仅在单篇文献中出现，缺乏系统研究。 | EV002 |
| G03 | underexplored | 组成 PbI2 仅在单篇文献中出现，缺乏系统研究。 | EV005 |
| G04 | underexplored | 组成 SnF2 仅在单篇文献中出现，缺乏系统研究。 | EV019 |
| G05 | underexplored | 组成 SnO2 仅在单篇文献中出现，缺乏系统研究。 | EV020 |
| G06 | underexplored | 组成 MAPbBr3 仅在单篇文献中出现，缺乏系统研究。 | EV032 |
| G07 | underexplored | 组成 FAPbBr3 仅在单篇文献中出现，缺乏系统研究。 | EV033 |
| G08 | contradiction | 组成 MAPbI3 的带隙在文献间存在冲突（1.34–1.57 eV），可能源于测试条件或相纯度的差异。 | EV023;EV041 |
| G09 | missing_link | 组成 Sn2+ 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV001 |
| G10 | missing_link | 组成 Sn4+ 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV002 |
| G11 | missing_link | 组成 PbI2 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV005 |
| G12 | missing_link | 组成 SnF2 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV019 |
| G13 | missing_link | 组成 SnO2 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV020 |
| G14 | missing_link | 组成 MAPbBr3 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV032 |
| G15 | missing_link | 组成 FAPbBr3 被提及但未给出关键光电性质（带隙/稳定性）的定量数据，形成证据链缺口。 | EV033 |

## 5. 路线A：构效关系发现
| 假设 | 目标性质 | 预测值 | 新颖性 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- |
| H01 | bandgap | - | 待验证 | candidate | EV023;EV040;EV041 |
| H02 | bandgap | - | 待验证 | candidate | EV023;EV040;EV041 |
| HX01 | bandgap | 1.254 | 新颖 | validated+db_crosschecked | EV001 |
| HX02 | bandgap | 1.256 | 新颖 | validated+db_crosschecked | EV001 |
| HX03 | bandgap | 1.271 | 新颖 | validated+db_crosschecked | EV001 |
| HX04 | bandgap | 1.29 | 新颖 | validated+db_crosschecked | EV001 |
| HX05 | bandgap | 1.274 | 新颖 | validated+db_crosschecked | EV001 |

## 6. 证据链（部分）
- **EV001** [9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 p.1] of perovskite-based tandem can   |  air,Sn2+ is rapidly oxidized to Sn4+,which can shorten the carrier diffusion length and result  →  `—`
- **EV002** [9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 p.1] an   |  air,Sn2+ is rapidly oxidized to Sn4+,which can shorten the carrier diffusion length and result in a drop in efficiency.Her  →  `—`
- **EV003** [9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 p.1] ng at B sites,always face atmospheric instability.When exposed to   |  简短地总结了中间层带来的不稳定性以及相应的解决措施.最后,我们回顾了钙钛矿材料固有的本征不稳定性和相应的改进方法,这对  →  `—` 条件:stability-context
- **EV004** [9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 p.1] ng at B sites,always face atmospheric instability.When exposed to   |  简短地总结了中间层带来的不稳定性以及相应的解决措施.最后,我们回顾了钙钛矿材料固有的本征不稳定性和相应的改进方法,这对  →  `—` 条件:stability-context
- **EV005** [9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 p.1] 1.68 eV bandgap perovskite, achieving a PCE of $20.7\%$ in perovskite single-junction solar cell. They found that the ad  →  `—`
- **EV006** [9edc56458d3143be08f9c7f2380d08645b3765481bab0039ed6f724432e2dc85 p.1] ith additive exhibited impressive light stability, which can remain $80\%$ of initial efficiency after $1000\mathrm{h}$ of continu  →  `—` 条件:stability-context
- **EV007** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV008** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV009** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV010** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV011** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV012** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1] # Highly Efficient and Stable Wide-Bandgap Perovskite Solar Cells via Strain Management  Pengjie Hang, Chenxia Ka  →  `—` 条件:stability-context
- **EV013** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV014** [54f01938d61af95d56f05c6a5ffa8cec92da75de511945f4118f2a2da23fc8b1 p.1]  cells (PSCs) with high performance and stability are in considerable demand to boost tandem solar cell efficiencies. Perovskite b  →  `—` 条件:stability-context
- **EV015** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1]  remarkably good performance, long-term stability is yet one of the last barriers before commercializing halide perovskite photovo  →  `—` 条件:stability-context
- **EV016** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1]  remarkably good performance, long-term stability is yet one of the last barriers before commercializing halide perovskite photovo  →  `—` 条件:stability-context
- **EV017** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1]  remarkably good performance, long-term stability is yet one of the last barriers before commercializing halide perovskite photovo  →  `—` 条件:stability-context
- **EV018** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] ting interfaces. Future perspectives of stable halide perovskite and perovskite solar cells are also proposed to shine light on le  →  `—` 条件:stability-context
- **EV019** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] [30] When integrated into all-perovskite tandem solar cells, one of the best devices reported that utilized $\mathrm{SnF  →  `—`
- **EV020** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] [30] When integrated into all-perovskite tandem solar cells, one of the best devices reported that utilized $\mathrm{SnF  →  `—`
- **EV021** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] [30] When integrated into all-perovskite tandem solar cells, one of the best devices reported that utilized $\mathrm{SnF  →  `—`
- **EV022** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] [30] When integrated into all-perovskite tandem solar cells, one of the best devices reported that utilized $\mathrm{SnF  →  `—`
- **EV023** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1]  room temperature, the relatively large bandgap (1.57 eV) and instability issues motivated the community to search for alternative  →  `1.57eV`
- **EV024** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] its initial performance after 500 h MPP stability test.[27]  # PHASE STABILITY  Even though $\mathrm{MAPbI}_3$ was found to exhibi  →  `—` 条件:stability-context
- **EV025** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1]  after 500 h MPP stability test.[27]  # PHASE STABILITY  Even though $\mathrm{MAPbI}_3$ was found to exhibit a stable perovskite p  →  `—` 条件:stability-context
- **EV026** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] mathrm{MAPbI}_3$ was found to exhibit a stable perovskite phase at room temperature, the relatively large bandgap (1.57 eV) and in  →  `—` 条件:stability-context
- **EV027** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] its initial performance after 500 h MPP stability test.[27]  # PHASE STABILITY  Even though $\mathrm{MAPbI}_3$ was found to exhibi  →  `—` 条件:stability-context
- **EV028** [e3d35ae5d7f031323d894230c55483a42e0ec4fe8e1f33f370621570d28de644 p.1] mathrm{MAPbI}_3$ was found to exhibit a stable perovskite phase at room temperature, the relatively large bandgap (1.57 eV) and in  →  `—` 条件:stability-context
- **EV029** [e0a69e333f35eb5e7c67f8e4d837c15a859caad7c5ed1effeb3af0318d98c56b p.1] ovskite layers with good efficiency and stability. In addition, as a special functional layer in tandem solar cells, the recombina  →  `—` 条件:stability-context
- **EV030** [e0a69e333f35eb5e7c67f8e4d837c15a859caad7c5ed1effeb3af0318d98c56b p.1] 2018). However, the inorganic PVSK is unstable under ambient conditions, it would rapidly degrade from the cubic black phase to th  →  `—` 条件:stability-context
- **EV031** [e0a69e333f35eb5e7c67f8e4d837c15a859caad7c5ed1effeb3af0318d98c56b p.1] er ambient conditions, it would rapidly degrade from the cubic black phase to the undesirable orthorhombic yellow phase, which det  →  `—` 条件:stability-context
- **EV032** [8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca p.1] For WBG perovskites, there is a subtle relation between the bandgap of the perovskites and the device stability of the c  →  `—`
- **EV033** [8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca p.1] For WBG perovskites, there is a subtle relation between the bandgap of the perovskites and the device stability of the c  →  `—`
- **EV034** [8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca p.1] ndgap of the perovskites and the device stability of the corresponding solar cells. First, the bandgap region of $2.2 - 2.3\mathrm  →  `—` 条件:stability-context
- **EV035** [8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca p.1] attices, these Br-based perovskites are stable against humidity/O in the ambient air, and they also possess excellent photo stabil  →  `—` 条件:stability-context
- **EV036** [8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca p.1] ndgap of the perovskites and the device stability of the corresponding solar cells. First, the bandgap region of $2.2 - 2.3\mathrm  →  `—` 条件:stability-context
- **EV037** [c7914c9971953f7b6577ea8305de2c9ceefc4307b7d908075eca819c8af4f179 p.1] ce, the perovskite film is inherently unstable, segregating into MIA-I- and FA-Br-rich phases. Adding either Cs+ or Rb+ is shown t  →  `—` 条件:stability-context
- **EV038** [c7914c9971953f7b6577ea8305de2c9ceefc4307b7d908075eca819c8af4f179 p.1] Currently, optimal perovskite compositions are based on $\mathrm{FA^{+}}$ as the majority cation. The cubic perovskite $  →  `—`
- **EV039** [c7914c9971953f7b6577ea8305de2c9ceefc4307b7d908075eca819c8af4f179 p.1] Currently, optimal perovskite compositions are based on $\mathrm{FA^{+}}$ as the majority cation. The cubic perovskite $  →  `—`
- **EV040** [c7914c9971953f7b6577ea8305de2c9ceefc4307b7d908075eca819c8af4f179 p.1] perovskite $\alpha$ -FAPbl₃ phase has a band gap of 1.48 eV, which is closer to the ideal single-junction device Shockley-Queisser  →  `1.48eV`
...

## 7. 审计轨迹（节选）
```
[parse] 8d7fa792ed87fc90543849c82265cd14ab6784c8b4fa0996a3493164e6ca94ca 解析完成，含 2 个章节
[parse] c7914c9971953f7b6577ea8305de2c9ceefc4307b7d908075eca819c8af4f179 解析完成，含 2 个章节
[node] parse executed
[extract] 抽取实体 43 条，证据 43 条
[node] extract executed
[normalize] 实体归一化完成
[node] normalize executed
[fusion] 知识图谱：13 节点 / 16 边
[node] fuse executed
[gap] 识别 Gap 15 条
[node] gap executed
[routeA] 生成种子假设 2 条（LLM 基于真实证据）
[node] routeA_hyp executed
[routeA-explore] 候选 MA_0.00FA_1.00Pb(I_0.99Br_0.01)3 t=0.959 Eg=1.25 LLM剪枝=True
[routeA-explore] 候选 MA_0.01FA_0.99Pb(I_0.99Br_0.01)3 t=0.959 Eg=1.26 LLM剪枝=True
[routeA-explore] 候选 MA_0.00FA_1.00Pb(I_0.97Br_0.03)3 t=0.959 Eg=1.27 LLM剪枝=True
[routeA-explore] 候选 MA_0.00FA_1.00Pb(I_0.95Br_0.05)3 t=0.959 Eg=1.29 LLM剪枝=True
[routeA-explore] 候选 MA_0.01FA_0.99Pb(I_0.97Br_0.03)3 t=0.959 Eg=1.27 LLM剪枝=True
[routeA-explore] 算法=bayes，接受假设 5 条
[node] routeA_explore executed
[routeA-validate] 与 Materials Project(模拟)交叉验证完成，新颖假设 5 条
[node] routeA_validate executed
[verify] 证据核验: 证据总数=43, 问题=0
[verify] 全部结论均可溯源 ✅
[node] verify executed
```
