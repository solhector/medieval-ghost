# Medieval Ghost

围绕 Arnaud Gélis 的中世纪生死关系与社会网络研究。

## 扩展01：从第一案开始

已加入第1—7案的选择性关系编码（第3案为重点段落核读，未完成全文精读）：新增83节点、130条关系陈述、64条带原文摘录的证据。合并版201节点、297条关系；不等于201名已确认不同的历史人物。

- [本批发现、方法和覆盖范围](gelis_network_reconstruction/research/expansion_01/README.md)
- [详细证据与页码](gelis_network_reconstruction/research/expansion_01/evidence.csv)
- [每案阅读进度](gelis_network_reconstruction/research/expansion_01/case_review.csv)
- [合并版人物与关系数据](gelis_network_reconstruction/analysis/expanded)
- [同名身份判断](gelis_network_reconstruction/research/expansion_01/identity_decisions.csv)

运行 `Rscript build_expanded.R` 可重建扩展数据。全卷176条姓名检索命中另存为待核查队列，不能视为已确认的关系。

## Gélis 社会网络（R）：核心v1快照

- [项目说明与运行方法](gelis_network_reconstruction/README_zh.md)
- [五页网络图集](gelis_network_reconstruction/Gelis_Network_Atlas.pdf)
- [人物数据](gelis_network_reconstruction/data/nodes.csv) · [关系数据](gelis_network_reconstruction/data/edges.csv)
- [R 绘图脚本](gelis_network_reconstruction/render_networks.R)

包括 118 个编码节点、167 条关系陈述，以及五组网络可视化。覆盖核心六案及已核读的跨案材料，并非全卷穷尽性网络；身份未决、显灵声称和未履行请求均另行标注。详见项目说明。

![传播网络](gelis_network_reconstruction/figures/01_circulation.png)
