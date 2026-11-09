> 最新批次：第三案已补齐全文，第14–16案已全文阅读（含复审、注释）。新增65节点、82条关系断言；合并版266节点、379条关系断言。详见 [扩展02阅读报告](research/expansion_02/README.md) 和 [逐页阅读记录](research/expansion_02/reading_log.csv)。以下核心图仍为v1快照。

# Gélis 的人物关系网络：可复核的 R 重构

**扩展01已加入**：[从第一案开始的证据与进度](research/expansion_01/README.md)。新增83节点、130关系，合并版共201节点、297关系，见 `analysis/expanded/`。运行 `Rscript build_expanded.R` 重建。下文及五张图仍说明原核心v1快照。

版本：2026-11-08。范围：围绕 Gélis 的核心案组以及已核读的跨案关系。不是全卷人物普查，也不是 Pamiers 的人口或完整社会网络。

## 先看什么

- `Gelis_Network_Atlas.pdf`：五页图集，按传播、家庭、教会、死者结伴、总览排序。
- `figures/`：各图的高清 PNG、可缩放 PDF、SVG。总览独立 PDF 原生画幅较大，比汇总图集更适合放大查看。
- `data/nodes.csv`：118 个节点，姓名、身份、生死状态、身份未决说明和来源页码。
- `data/edges.csv`：167 条人工编码关系陈述，每条有动作、方向、材料类型、履行状态、供词出处和印刷页码。
- `render_networks.R`：全部网络建构、图形输出及探索性指标的 R 源码。
- `analysis/`：R 对象、GraphML、布局坐标、探索性指标和实际运行环境。

图中使用法文姓名和中文身份。节点等大，颜色仅表示生死状态；图中距离不代表居住距离、亲疏或时间先后。亲属面板的分组是便于阅读的人工选择，不是算法发现的社区。

## 边的标准

一个节点原则上对应一个人；匿名但可以区分的人也保留节点。三个夭折的 Arignac 女儿、两个 Dun 贵族青年分别编码，序号仅供数据库识别，不代表出生顺序。

一条边必须有可定位的明确关系或行动陈述。共同出现于一段文字、同姓、同处审讯仪式、属于同一职业，都不自动成边。查询某位死者也不自动产生“见过该死者”的边。

| layer | 内容 | 方向 |
|---|---|---|
| kinship | 亲子、婚姻、同胞、远亲 | 亲子：长辈到子女；其余无向 |
| communication | 提问、转述、引介、陪访、传话 | 行动者到对象；注意查询与消息传递方向并不具有相同意义 |
| social | 服务、共餐、实际同行、债务、争执、调解 | 按关系标签解释；服务者到受服务者，批评者到被批评者等 |
| ritual | 弥撒费用、委托、提出施舍安排 | 委托者／转交者到接收者；拟议安排不算已执行 |
| apparition | 供词声称的显灵、交谈或被转述的接触 | 死者到通灵者，不等于历史学家确认显灵发生 |
| care | 死后关切、要求、亲吻、敌意 | 行动者到对象；这是分析层名称，不代表每条都属于正面照护 |
| afterlife | 明确点名的死者结伴 | 无向；不由一般性论述扩成全连接网络 |
| judicial | 审讯、程序在场 | 官员到相关当事人；与日常交往分层 |

**这是多层、多重关系网络。**同一对人物可有不同边，不能把每条边都当成一次独立接触。现阶段为“关系陈述表”，不是完整逐句事件数据库；未分别记录同一事件的每一次复述。

`directed=false` 的边只存一行，不人为添加逆向副本。GraphML 底层是有向容器，但每条边另有 `directed` 属性，导入其他软件时须依该属性关闭婚姻等边的箭头。R 图形已正确区分。

## 证据与线型

- `reported`：证词报告的亲属、交往或转述。它仍不是未经媒介的事实记录；“reported”不等于“多名独立证人验证”。
- `vision_claim`：显灵、死者行动、死者之间联系的声称。部分由本人讲述，部分由他人转述；具体看 `deposition` 和 `detail_zh`。
- `procedural`：审讯记录中的程序性事件。
- `inferred`：由相关亲属称谓推定的关系，以点线表示。

`outcome=attested` 表示材料记载该动作发生，并非研究者担保它真实发生。`not_fulfilled` 是未履行／拒绝／未实现，`unknown` 是请求是否达成不明，`proposed` 是仅提出的安排。后三种在图中均为虚线，精确差别保留在表内。

例如：Touzes 请求 Raimonde 安排会面，Raimonde 拒绝。因此有“请求但未成功”的边，不补出 Touzes 与 Gélis 成功会面的边。Gélis 未向 Brune d’Escosse 和 Thomas 传递警告，两条边以虚线显示预定传话对象，而非实际信息流。

## 身份识别中的保留

1. Sœur Raimonde 与 Raimonde Fauré 不强并。
2. Gausia 与 na Nespla 不强并；Gausia 的丈夫独立为“Arignac [époux de Gausia]”。
3. 债据事件中的 Guillaume 之子可能就是 Raimond，但暂时分别编码。对应节点不能用于未经敏感性分析的人口计数。
4. Brune de Calmelles 与 Brunissende 可能同一人，保留两节点。
5. Calmelles 家的母女 Barcelone 与 Pons Fauré 的遗孀 Barcelone 是三个人。
6. Pons Bru 父子、Fabrissa Fauré 与 Fabrissa Battegay 各自分开。
7. Gélis 的妻子由岳母及家庭描述推知，生死未明；不能给她补出对通灵的态度。
8. 不把 p.145 的“Bernard de Loubens之妻Barcelone”强并到“Guillaume de Loubens之妻”。不把p.515的同名市民Arnaud de Calmelles自动合并。
9. Na Serres 与 Pierre de Serres 未推定亲属关系。
10. Fléchier 的亲属编码依据p.180供词：该母亲的母亲Gentille、女儿Raimonde、丈夫Faure。未采用索引中将Raimonde写作Faure姐妹的疑误。

## 时间与状态

`status` 表示核心叙事中人物作为生者、死者或生死未明者的位置，不是所有事件共享的截面。Hugues 与 Gélis 的服务关系发生在生前，显灵声称发生在死后。Authié 与女性的关系亦为较早生前关系。这一版保留时期混合，不拟合动态网络。

已故者可有历史婚姻边；婚姻边不意味着死亡后法律婚姻仍继续。未明确死亡的配偶通常记为 uncertain。身份不确定与关系是否实际履行是两种不同变量。

## 来源与覆盖

依据用户提供的 Jean Duvernoy 法译《Le Registre d’Inquisition de Jacques Fournier》合卷扫描本。核心为第8—13案：

- Gélis：印刷pp.158–171，PDF pp.198–211。
- Mengarde：pp.172–177，PDF pp.212–217。
- Raimonde Fauré：pp.178–181，PDF pp.218–221。
- Navarre：pp.182–184，PDF pp.222–224。
- Arnaud de Monesple：pp.185–187，PDF pp.225–227。
- Guillemette Battegay：pp.188–190，PDF pp.228–230。
- 跨案扩展：Sibille案p.583（PDF p.637），Guillaume Baille案p.828（PDF p.888）。

核心页码是法译本连续印刷页码，不是1965年拉丁版卷页。全卷PDF页码与印刷页码的偏移不恒定，不可把核心的“+40”规则用于全书。原文文件未重复打包；其SHA-256及文件名见 `data/source_manifest.json`。

该图重构自已读材料及前一轮人物表，并对图形编码所需的身份与关系作保守区分。边表中文说明是概述，不是逐字翻译。后续若要发表，宜以拉丁文本、手稿及其他城市档案复核人物识别；这不是已完成的版本对勘。

没有把匿名“穷人群体”、不明确人数的孙辈、全体犹太死者等集体做成人物节点。Mas、Cordes等仅有其处境被报告，未因此强造与Gélis的会面；可出现在总图中成为孤立点。未编码所有可能关系，不宜将缺边视为真实无关系。

## 指标如何读

`analysis/observed_communication_metrics.csv` 仅选双方都被标为生者、`communication`层且 `outcome=attested` 的边，合并同向重复边后计算：

- distinct_partners：无向投影中的不同联系人数；
- out_partners / in_partners：有向不同对象数；
- betweenness：该无向投影中的归一化中介中心性。

这些指标描述此编码下的现存证词网络。查询、介绍、转述等混合在同一探索性投影中，不能直接解释为信息传播速率或实际社会权力。该投影也未纳入全部社会交往，不能把中介中心性直接用于社会因果推断。

案件以Gélis为组织中心、审讯追问有选择、存留不均，均会放大某些人物。未强行做社区发现或将中心性画成节点大小。若需要严肃定量分析，应先做不同边层、姓名合并方案、司法层排除与转述证据排除的敏感性分析。

## 运行

在安装R的电脑上解压整个项目，在项目目录执行：

```r
install.packages(c("igraph", "ggplot2", "ggrepel"))
source("render_networks.R")
```

或在终端执行 `Rscript render_networks.R`。脚本会自动以脚本所在目录为工作目录；在RStudio中source时，请先把工作目录设为项目根目录。

中文需 Noto Sans CJK SC 字体。没有该字体时安装它，或在运行前 `Sys.setenv(GELIS_FONT="你的中文字体名")`。需要支持Cairo的R构建以正确生成中文PDF/PNG；已提供的成品不需要安装R即可查看。

实际运行的R与软件包版本见 `analysis/sessionInfo.txt`；随机种子固定为1320等值。总图与部分分图由Fruchterman–Reingold力导向布局生成，传播图采用明确写在脚本里的阅读布局。PNG、PDF、SVG分别渲染，自动避让的细微位置可能随字体、设备尺寸和软件版本变化；不影响图的拓扑。
