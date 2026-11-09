# 扩展01：从第一案起检索人物与关系

本批范围为第1—7案，法译印刷pp.31–157；第3案篇幅很长，采用相关段落核读加姓名检索，**未完成逐页精读**。其余案件核读正文并选择性编码；也没有宣称穷尽每个见证者或全部关系。详细进度见 `case_review.csv`。下一批应先补第3案剩余段落，再推进第14案以后，同时复核全卷检索队列。

本批新增83个人物节点、130条关系陈述、64条定位到具体页和原文片段的证据，另保留10条未纳入图的否定／撤回／证据不足陈述。与原118节点、167边合并后为201节点、297条关系陈述；这些不是人口统计、独立事件数或已证实的历史事实数。

## 主要发现与Gélis的关系

1. **Jacques Camelle/Camelie**：第2案p.50（PDF86）明确列在保密审讯的法律顾问名单中。与原Gélis材料中Philippa之夫、法律人士Camelle暂作同一（既有ID `camelle`）。这是司法角色的扩展，不能由此推出他与Pierre Sabatier的私人交往。暂合并依据及可撤销性见身份判断表。
2. **Melonier、Loubens、Calmelles**：第4案p.125及第6案p.145给出Pamiers的来访、共食和教堂同行关系。这些值得追踪，但目前不足以证明都接入Gélis的私人交往网。Arnaud与Pierre-Arnaud Melonier暂不合并；Bernard与Guillaume de Loubens及其两位同名妻子也分别登记。不能根据同姓把他们全连起来。
3. **死后仍然爱戴**：Raimond在第3案p.104（PDF144）说他深爱Jean le Lorrain，死后仍爱。这是明确指向已故具体人物的关系，编码为`care`层的“死后仍然爱戴”，不是显灵。其对死后代祷的否定须另外研究，不能据此抹去这种感情关系。
4. **死者故事的传播**：第7案中Bérenger Escoulan的酒馆、路途交谈形成可追踪的转述链。他明确说没有见过Raimond；这不是亲见行刑，更不是显灵。这批材料适合与Gélis传说的传播机制对照，但尚无证据将两条传播链直接连起来。
5. **跨案具体人物**：Geoffroy Escribe出现在第1案的病榻陈述与第7案的酒馆证言中，姓名、Ventenac居所相合，使用同一新ID。普通家庭、护理与邻里谈话也保留，便于以后寻找此前未预见的连接。

## 文件与字段

- `new_nodes.csv`：新增人物；身份、生死说明、来源页与消歧。
- `assertions.csv`：新增关系陈述；`evidence_id`连接证据，`case_id`连接案件，关系方向和层与原数据兼容。同一关系的不同动作仍可多行；不是接触频次。
- `evidence.csv`：法译本页码、PDF物理页码（从1开始）、证词人、审讯日期、事件相对时间、OCR摘录、检索锚点、标准化页内字符区间及页文本SHA-256、原PDF SHA-256。区间是Unicode字符位置，0起点、结束位置不含；标准化仅压缩空白。摘录有时从句中开始或结束，须回看整页，不是完整逐句校译。
- `excluded_claims.csv`：不进入图的撤回、否定或不足证据。它们是研究资料，不应当作为实际社会关系。
- `identity_decisions.csv`：跨案合并、暂不合并和纠名的可审查记录。`candidate`关系不是图中的人物边。
- `case_review.csv`：每案覆盖程度与遗漏；“检索过”不等于“逐页读过”，更不等于“全部编码”。
- `search_queries.csv`、`search_hits.csv`：对整份PDF文本的15组姓名／别名检索，176处命中。包括正文、页眉、注释、目录与索引，尚未全部人工分类；只作下一轮工作队列。未命中也不证明人物未出现。
- `encode_expansion.py`：保存本批逐条人工编码决定；`scan_register.py`：重建候选检索队列。Python只用于史料摘录和数据登记；合并与网络导出使用项目根目录的`build_expanded.R`。

原`data/nodes.csv`与`data/edges.csv`以及五张图保留为**核心案组v1快照**。本批扩展版在`analysis/expanded/nodes.csv`、`edges.csv`、`expanded_network.rds`与`expanded_network.graphml`，不要把旧图误认为201节点的扩展总图。

## 史料及批判规则

使用用户提供的1978年Jean Duvernoy法译合卷扫描本，文件名与哈希见原`data/source_manifest.json`。`source_id=duvernoy1978_user_scan`。摘录来自PDF现有文本层，保留OCR的断词和错字，没有将它伪装成拉丁原文或经手稿校验的转录。页码已用PDF文本层抽查定位；未逐条进行影像／拉丁版对勘。原书未上传本仓库。

- 本批PDF页与印刷页**不是固定偏移**：pp.31–62偏移36；pp.63–94偏移38；pp.95起这批范围偏移40。中间插图造成差异。证据各行给具体物理页码。
- `reported`仍是证词的声称，不保证事件实际发生；`procedural`是程序记录。发言人、转述层次与更正记录必须一起读。不同证人叙述同一事件不是独立发生多次。
- 第1案Aude等人的供词多次更改。探病地点与时间采用最后对质后版本，但保留前后来源；“tia”不是亲属证明；“fille suivante”是女仆，不是女儿。
- 第4案Agnès起初说只认识Raimond一年半，后来承认曾为其乳母。第6案Huguette撤回母舅说，仆人由Jean更名为Etienne。撤回后的身份关系不能与前说并列当作两个事实。
- 人物`status`不是统一日期的截面：新Raimond节点按生前交往场景标living，1320年处刑及死后传播另见说明。死亡前后、审讯时间、事件时间不能混用。
- 第2案译本括注日期存在疑点：本批保留“圣凯瑟琳节前星期二”的原表达，不强算公历日期。第7案多人证词的登记日也分开存，不统一替换。
- 司法顾问、证人同场不自动形成两两关系；地点属于某人不自动证明他在场或接待；讨论死者不自动证明生前认识。
- 新增亲属／邻里关系中，尚未连接Gélis的部分仍保留。不要为了使图连通而合并姓名；共同被Fournier审讯也不能当作普通社交纽带。
- 原核心167条边仍主要只有页码级出处；本次没有虚称已经为全部旧边补齐原文。扩展合并表用`provenance_level`明确区分。

## 重建与后续

在项目目录用`Rscript build_expanded.R`合并数据并校验。只需`igraph`，不需要重新绘制旧图。

如持有同一PDF，用`pdftotext -layout 原书.pdf register.txt`提取，然后：

```bash
python3 research/expansion_01/encode_expansion.py /path/to/register.txt
python3 research/expansion_01/scan_register.py /path/to/register.txt
Rscript build_expanded.R
```

下一步：补读第3案余段；逐条复核176条搜索命中的正文/编者层；从第14案继续依次登记。旧核心案组8—13也需要升级为这套证据粒度。若遇同名，先更新身份判断表，再决定是否改合并视图，不覆盖原始陈述。
