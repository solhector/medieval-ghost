"""Manual, source-led encoding; requires the user's pdftotext -layout register.txt.
Reading notes are human/model-authored after sequential reading, not keyword output.
"""
import csv,json,re,hashlib,sys
from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parents[1]
pages=Path(sys.argv[1]).read_text().split('\f')
source=json.loads((root/'data/source_manifest.json').read_text())
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
known={r['id'] for p in [root/'data/nodes.csv',root/'research/expansion_01/new_nodes.csv'] for r in read(p)}
people=[];ev=[];edges=[];claims=[];themes=[];updates=[];identities=[]
def write(name,rows):
 with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def N(i,name,role,p,status='living',note=''):
 assert i not in known,i
 known.add(i);people.append(dict(id=i,name=name,role_zh=role,status=status,group='第三案补读与第14至16案',identity_note=note,printed_pages=str(p),source_basis='expansion_02；身份据所列页码，关系另见evidence/assertions'))
def V(c,p,speaker,anchor,date='',time='',length=1000,layer='translated_register'):
 pdf=p+(36 if p<63 else 38 if p<95 else 40)
 s=re.sub(r'\s+',' ',pages[pdf-1]).strip();assert anchor in s,(p,anchor)
 st=max(0,s.index(anchor)-40);en=min(len(s),s.index(anchor)+length)
 i=f'v02_{len(ev)+1:03}'
 ev.append(dict(evidence_id=i,source_id='duvernoy1978_user_scan',case_id=f'C{c:03}',printed_page=p,pdf_page=pdf,speaker=speaker,deposition_date=date,event_time_expression=time,anchor=anchor,excerpt_fr_ocr=s[st:en],normalized_char_start=st,normalized_char_end=en,page_text_sha256=hashlib.sha256(pages[pdf-1].encode()).hexdigest(),source_pdf_sha256=source['sha256'],source_layer=layer,verification='sequential full-case text reading; exact normalized excerpt checked; OCR not Latin/facsimile collated',notes_zh='日期按本页或所属审讯段；空白表示未在本条确定，不能解释为事件日期'))
 return i
def A(a,b,layer,rel,v,detail='',directed=True,mode='reported',outcome='attested'):
 assert a in known and b in known,(a,b)
 e=next(x for x in ev if x['evidence_id']==v)
 edges.append(dict(edge_id=f'x02_{len(edges)+1:03}',source=a,target=b,layer=layer,relation_zh=rel,directed=str(directed).lower(),evidence_mode=mode,outcome=outcome,printed_pages=e['printed_page'],deposition=e['speaker'],detail_zh=detail,evidence_id=v,case_id=e['case_id'],event_time_expression=e['event_time_expression']))
def T(subject,kind,text,v,related=''):
 themes.append(dict(statement_id=f't02_{len(themes)+1:03}',subject_id=subject,related_person_id=related,statement_type=kind,summary_zh=text,evidence_id=v,in_positive_graph='false'))
def X(a,b,claim,v,reason,resolution=''):
 claims.append(dict(claim_id=f'neg02_{len(claims)+1:03}',source=a,target=b,claim_zh=claim,evidence_id=v,resolution_evidence_id=resolution,disposition='excluded_from_graph_as_fact',reason_zh=reason))
def I(a,b,decision,reason,v=''):
 identities.append(dict(person_a=a,person_b=b,decision=decision,reason_zh=reason,evidence_id=v))
# C003: supplement existing edges, never duplicate the 11 previously encoded relations.
for x in [
 ('c3_andre','André Guiraud','Vienne地区来Pamiers谋生的同伴',58),
 ('c3_guilhem','Jean Guilhem','Vienne地区来Pamiers谋生的同伴',58),
 ('c3_guillelme','Guillelme Pascal','Vienne地区来Pamiers谋生的女性同伴',58),
 ('c3_petrone','Pétrone Pascal','Vienne地区来Pamiers谋生的女性同伴',58),
 ('c3_mentor','Premier compagnon de Raymond [anonyme]','招引Raymond的早期瓦尔多派同伴；死于Lyon教区',103,'dead','不强并最初供词中的Pierre'),
 ('c3_christin','Christin [majoral]','继Jean之后的瓦尔多派领袖；称不识字',104,'dead','任职相继不等于有直接个人接触'),
 ('c3_jacques','Jacques [majoral]','继Christin之后的瓦尔多派领袖',104,'dead','姓名插句出于编者校订；不与Hautpas募捐人合并'),
 ('c3_majoral','Ministre actuel [anonyme]','Raymond拒绝透露姓名的现任瓦尔多派领袖',104),
 ('c3_questor','Jacques [quêteur de Hautpas]','募捐人；书籍来源',107,'uncertain'),
 ('c3_bookseller','André de Viennois','向Raymond出售书籍者',107,'uncertain'),
 ('c3_motier','Robert Motier','Raymond称曾在Gascogne活动的瓦尔多派神父',115,'dead'),
 ('c3_maurin','Etienne Maurin','Raymond称曾在Gascogne活动的瓦尔多派神父',115,'dead')]:N(*x)
v=V(3,58,'Raymond','Deux hommes',date='1319-08-11',time='约一月前离开Pamiers，去Carcassonne和Narbonne')
for i in ['c3_andre','c3_guilhem','c3_guillelme','c3_petrone']:A('saintefoy',i,'social','在Pamiers结伴',v,directed=False)
I('c3_petrone','petrone','keep_separate','仅名字近似不足以与Jean姊妹合并；该段明确说是另一些同伴',v)
I('c3_bookseller','c3_andre','keep_separate','同名同地区不足以确定同一人')
v=V(3,75,'Raymond','aux âmes de mon père',date='1320-01-05',length=750)
T('saintefoy','explicit_nonaction','明确说不为已故父母祈祷或施舍；若相信有用，他就会这样做。不能编码成正向代祷边。',v,'ray_father;ray_mother')
updates.append(dict(id='ray_father',field='status',new_value='dead',evidence_id=v,reason_zh='明确称父母之亡魂；旧版uncertain现补证'))
v=V(3,75,'Raymond','je ne ferais pas célébrer',date='1320-01-05',length=1100)
T('saintefoy','counterfactual_and_doctrine','不会为死者请弥撒；遗赠的益处在生前决定所获功德，而非缩短死后炼狱。',v)
v=V(3,76,'Raymond','les âmes des saints',date='1320-01-05',length=700)
T('saintefoy','doctrine','承认圣人知道生者给他们的荣誉、听见祈祷并为生者祈祷；泛论不制造具体地方人物边。',v)
v=V(3,103,'Raymond','un compagnon qui',date='1320-01-15',length=1000)
A('c3_mentor','saintefoy','communication','结识并引导加入其生活道路',v,'Raymond否认父母或朋友介绍；入道约27年前，导师约18年前已死')
v=V(3,104,'Raymond','Pendant les deux années',date='1320-01-15',length=950)
A('c3_mentor','saintefoy','social','在学校探访并引见领袖及同伴',v)
A('saintefoy','ray_father','social','初识导师后两年仍住父家',v,directed=False)
v=V(3,104,'Raymond','Après sa mort, je vis Christin',date='1320-01-15',length=650)
A('saintefoy','c3_christin','social','曾会见',v)
A('saintefoy','c3_majoral','social','在其任领袖后会见',v)
T('c3_christin','office_sequence','Jean→Christin→Jacques→匿名现任领袖；记录职务次序，不投影为彼此相识边。Jacques插句参注47。',v,'jean_lorrain;c3_jacques;c3_majoral')
v=V(3,107,'程序记录／Raymond','trois livres',date='1320-01-16',length=650)
A('jean_lorrain','saintefoy','material','提供以Spiritus sanctus开头的书',v,'原文只说得自，不确定赠送或出售')
A('c3_questor','saintefoy','material','提供以Libre d’Esdras开头的书',v)
A('c3_bookseller','saintefoy','material','出售以Discretis开头的书',v)
v=V(3,115,'Raymond','Robert Motier',date='1320-01-23',length=600)
T('saintefoy','named_missionaries','说Robert Motier、Etienne Maurin在Gascogne招收信徒，且相信二人约六年前去世；没有据此建立自己与他们相识的边。',v,'c3_motier;c3_maurin')
A('saintefoy','c3_majoral','authority','自称反抗并不服从现任领袖',v,'不可只据前面的服从原则推定实际服从')
v=V(3,56,'Raymond','Je me suis confessé',length=1000)
X('saintefoy','Pierre [Eclose; unresolved]','在Eclose向Pierre告解，受教禁誓',v,'初期自辩与后期叙述不同；编者注22判为掩饰，暂不确立此人及关系')
v=V(3,57,'程序记录／Raymond','à Huguette et à Pétronille',date='1319-08-11',length=1300)
X('saintefoy','huguette;petrone','教两名女性一概不发誓',v,'明确撤回，且Pétronille身份待核；不添加正向教学边')
T('saintefoy','recantation','8月11日曾承认炼狱与亡者代祷效力，后面又否认；不可把全案处理成不变的信念。',v)
v=V(3,114,'程序记录／Raymond','Il estjuste de dire',date='1320-01-23',length=1800)
T('saintefoy','partial_recantation','撤回洗礼绝对必要、无圣油亦可坚振、已婚者授职无效等观点；仍拒绝撤回禁誓等核心立场。',v)
# C014: named persons; shared rumors are speech events, never ghost agency by inference.
for x in [
 ('carot','Jacqueline den Carot','Ax居民；Raimond Carot遗孀；磨坊谈话被告',191),
 ('carot_h','Raimond Carot','Jacqueline亡夫',196,'dead'),
 ('gaillarde_child','Gaillarde [fille de Pierre de Canals]','约12岁乞食女孩；寄住Pierre Rouch家；证人',191),
 ('canals','Pierre de Canals','Saurai人；Gaillarde之父',192,'uncertain'),
 ('rouch','Pierre Rouch','Mérens教区长；在Ax有房，收留Gaillarde',193),
 ('lagleize','Barthélémy de Lagleize / de Sorgeat','Sorgeat神父；Ax代牧；证人',191),
 ('caussou_miller','Guillaume Caussou','Ax磨坊主／磨工；谈话者及证人',191),
 ('valentin','Valentin Barra','在Ax墓地被杀者；声响传闻的背景人物',191,'dead','不等于已证实发声鬼魂；不与Pons Malet合并'),
 ('mondon','Arnaud Mondon','Ax居民；Jacqueline女婿；失去两匹毛呢者',195),
 ('gasc_notary','Bérenger Gasc','Tarascón公证人；审讯问句指认为施术者',195,'living','Jacqueline答语称匿名clerc；同一指认出自提问框架'),
 ('pellicier','Arnaud Pellicier','Ax居民；被请来参加术法的女孩之父',195,'uncertain'),
 ('pellicier_d','Fille d’Arnaud Pellicier [anonyme]','拟在术法中看见失物去向的女孩',195),
 ('meriana','Pons Mériana','与Jacqueline同列传票的嫌疑人',193,'uncertain','同列传票不等于相识；编者猜逃亡，不作事实')]:N(*x)
v=V(14,192,'Gaillarde','Gaillarde, fille',date='1320-03-03',length=1300)
A('canals','gaillarde_child','kinship','父女',v)
A('gaillarde_child','carot','social','在磨坊亲耳听见谈话',v,'不是由证词同现自动投影',mode='self_report')
A('gaillarde_child','caussou_miller','social','在磨坊亲耳听见谈话',v,mode='self_report')
v=V(14,192,'Gaillarde','Le mardi suivant',date='1320-03-03',length=1050)
A('rouch','gaillarde_child','care','提供住处',v)
for i in ['rouch','lagleize']:
 A('gaillarde_child',i,'communication','转述磨坊言论并求证',v)
 A(i,'gaillarde_child','communication','回答教会持相反教义',v)
A('rouch','lagleize','communication','炉边讨论佩十字者的补赎',v,directed=False)
T('gaillarde_child','social_consequence','自述告发公开后在Ax变得招人憎恶；无具体加害者姓名，不能生成全城人与她的敌对边。',v)
v=V(14,193,'Pierre Rouch','Gaillarde, une petite',date='1320-03-03',length=1250)
A('gaillarde_child','rouch','communication','转述磨坊言论',v,'独立证言支持同一传播事件，不当作另一次传播；Rouch说周一，女孩说周二')
v=V(14,191,'Guillaume Caussou','Nous parlions entre nous',date='1320-03-03',length=1250)
A('carot','caussou_miller','communication','在磨坊讨论墓地声响、复活与死后相认',v,directed=False)
T('valentin','rumor_context','据传Valentin遇害后墓地有夜间声响、神父害怕留宿；证词未说Jacqueline亲闻或认定是Valentin鬼魂。',v)
v=V(14,194,'Jacqueline','Valentin Barra avait été assassiné',date='1320-05-03',length=850)
T('carot','rumor_repetition','承认听到城中流传墓地声响及神父畏惧的说法；与磨坊交流相接。',v,'valentin')
v=V(14,196,'程序记录','de feu Raimond Carot',date='1320-06-21',length=450)
A('carot','carot_h','kinship','婚姻／丧偶',v,directed=False)
v=V(14,195,'审讯问句／Jacqueline','Bérenger Gasc',date='1320-06-21',time='约两年前九月圣米迦勒节',length=1800)
A('mondon','carot','kinship','女婿与岳母',v)
A('mondon','carot','communication','请求找来Pellicier之女',v)
A('carot','pellicier_d','social','接来并带上自家楼层',v)
A('pellicier','pellicier_d','kinship','父女',v)
A('mondon','gasc_notary','social','带来施术教士',v,'Bérenger姓名来自问句；答词仅称clerc',mode='interrogator_identification')
A('mondon','carot','communication','事后告诉她已经施术',v,'她说自己离开楼层，未亲眼观看')
X('gasc_notary','pellicier_d','成功通过术法找回毛呢',v,'仅报告施术已做；没有找回失物的结果，亦无死者显现')
v=V(14,196,'Jacqueline','doutai, et me demandai',date='1320-06-21',length=1400)
T('carot','qualified_admission','终于承认谈话短时间内心存疑惑，始终否认断言不复活；须与Gaillarde的强断言归责并列。',v)
I('carot','jacqueline','keep_separate','Ax的Carot遗孀与Pamiers铁匠女儿Jacqueline Othon不是同一人')
I('valentin','malet','keep_separate','均属Ax遇害者不足以合并；本案没有把墓地声响与Gélis的Pons Malet叙事联系起来')
# C015: ordinary town and prison networks, including changing testimony.
for x in [
 ('savinhan','Arnaud de Savinhan','Tarascón／Quié石匠；45岁左右；被审者、囚犯',204),
 ('cordier','Bertrand Cordier','Pamiers人，居Tarascón；新闻传述者、证人',199),
 ('beubre','Jean Yfort / Beubre','Tarascón居民；桥头谈话者、证人',200),
 ('mayshelac','Pierre de Mayshelac','Tarascón／Quié居民；证人',200),
 ('mercier','Pierre Mercier','Tarascón整呢工；桥头谈话者',199),
 ('fre zat'.replace(' ',''),'Raimond Frézat','Quié教区长；教导Savinhan',202),
 ('gaillac','Pierre de Gaillac','Tarascón人；Savinhan表亲／堂亲；法律人士身份见注10',202),
 ('tolus','Arnaud Tolus','Tarascón学校教师；被称教授世界终末观点',203,'uncertain'),
 ('niaux_a','Arnaud de Niaux','在Tarascón提供主教住处的屋主',201),
 ('vesian','Vésian Teisseyre','桥头邻居；曾买Savinhan的房屋；证人',206),
 ('thibaud','Guillaume Thibaud','Guillaume Bernard Massonier之子；证人',206),
 ('massonier','Guillaume Bernard Massonier','Guillaume Thibaud之父',206,'uncertain'),
 ('auge','Bernard Augé','Tarascón屋主；Savinhan曾在其房屋工作',207),
 ('montanie','Jean Montanié / Montanier','桥头居民；磨坊主人；证人',207),
 ('turiere','Bernard Turière','磨坊谈话参与者；Honors之夫',207),
 ('honors','Honors [épouse de Bernard Turière]','被Savinhan指责与邻人串通者',207),
 ('caussou_a','Arnaud de Caussou','Savinhan指责的邻居',207),
 ('cogul','Arnaud Cogul','与Savinhan等同批入狱者',209),
 ('magre','Pierre Magre','Rabat居民；护送过被称André者；后与Savinhan同批入狱',219),
 ('autast','Guillaume Autast','与Savinhan等同批入狱者；第18案被告',209),
 ('vaissiere','Raimond Vaissière','与Savinhan同囚；议论审判、什一税争端',209),
 ('franque','Bernard Franque','与Savinhan等同批入狱者',209),
 ('amilhac','Barthélémy Amilhac','神父；与Savinhan、Bernard Clergue同囚',209),
 ('spinalbel','Pierre de Spinalbel','Savinhan姻亲（beau-frère）',209),
 ('helie','Bertrand Hélie','Tarascón人；Savinhan一代表／堂亲',209),
 ('cavatier','Guillaume Cavatier','Foix伯爵在Tarascón的sergent',210),
 ('bernard_clergue','Bernard Clergue','Montaillou人；Pierre之兄弟；囚犯',210),
 ('pierre_clergue','Pierre Clergue','Bernard之兄弟；遭Béatrice作证指控者',210,'uncertain','本批只登记本案明确身份；不把熟知的其他传记自动加入'),
 ('beatrice_prison','Béatrice [détenue au Mur]','女囚；对Pierre Clergue作证者',210,'living','与Béatrice de Planissoles的同一性待读其案核定'),
 ('bernarde_s','Bernarde [épouse de Savinhan]','Savinhan之妻',211),
 ('peyre_quie','Raimond Peyre','Quié人；道路谈话听众',211),
 ('niaux_g','Guillaume de Niaux','Tarascón人；曾在Carcassonne服刑；佩十字者',212),
 ('tron','Guillaume Tron','Tarascón人；向Savinhan谈论Gaillac',212),
 ('hugol','Pierre den Hugol','Quié人；妻子受佩十字惩罚',214,'uncertain'),
 ('hugol_w','Épouse de Pierre den Hugol [anonyme]','Quié女性；受佩十字惩罚',214),
 ('delaire','Guillaume Delaire','Quié人；护送被称André者；妻子受佩十字惩罚',215),
 ('delaire_w','Épouse de Guillaume Delaire [anonyme]','Quié女性；受佩十字惩罚',215)]:N(*x)
v=V(15,199,'Bertrand Cordier','il y avait là Jean de Beubre',date='1320-04-20',time='约两年前／1319年大斋期，证词日期不一致',length=1700)
for i in ['beubre','mayshelac','mercier','savinhan']:A('cordier',i,'communication','从Pamiers带来末世消息并讨论',v,'不得将同席者两两推定为朋友')
A('savinhan','cordier','communication','反驳世界将终结',v)
v=V(15,201,'Jean Yfort / Beubre','car il venait',date='1320-04-22',length=350)
A('beubre','cordier','communication','将Savinhan言论归咎于其家族异端背景',v,'这是评价性言语，不是已核定亲属的异端身份')
v=V(15,201,'程序记录',"dans la maison d'Arnaud de Niaux",date='1320-05-09',length=350)
A('niaux_a','fournier','social','提供主教住处',v)
v=V(15,202,'Savinhan','Raimond Frézat',date='1320-05-11',length=700)
for i in ['frezat','gaillac']:A(i,'savinhan','communication','教导复活后身体永存',v)
v=V(15,203,'Savinhan','Maître Arnaud Tolus',date='1320-07-15',length=350)
A('tolus','savinhan','communication','被归因为世界审判后归无观点的教师',v,'后称自悟与公共言论，故此为随时间变化的归责',mode='attributed')
v=V(15,205,'Savinhan','J’allais bien'.replace('’',"'"),date='1320-10-25',length=1100)
T('savinhan','belief_origin_revision','说忙于石匠工作不听讲道，并以俗谚、公共言论及自己思考解释观点来源；与先前Tolus归责存在变化。',v)
v=V(15,206,'Vésian Teisseyre',"j'habite à côté",date='1322-11-25',length=1600)
A('vesian','savinhan','social','邻居',v,directed=False)
A('vesian','savinhan','material','买其房屋并要求偿还40里弗',v,'正文称入狱前购买；编者注19解释为没收后拍卖与赎回。保留矛盾，不采用注释重建为唯一事实')
A('savinhan','vesian','communication','抱怨邻居使自己损失财产',v)
v=V(15,206,'程序记录','Guillaume Thibaud, fils',date='1322-11-25',length=300)
A('massonier','thibaud','kinship','父子',v)
v=V(15,207,'Guillaume Thibaud','travailler dans la maison',date='1322-11-25',length=400)
A('savinhan','auge','economic','在其房屋工作',v,'不足以确定直接雇佣合同')
v=V(15,207,'Jean Montanié',"j'habite assez près",date='1322-11-26',length=1800)
A('montanie','savinhan','social','住得很近',v,directed=False)
for i in ['montanie','turiere']:A('savinhan',i,'communication','在磨坊抱怨邻居串通作证',v)
A('turiere','honors','kinship','婚姻',v,directed=False)
A('savinhan','gaillac','kinship','cousin，亲属具体谱系未明',v,directed=False)
for i in ['beubre','caussou_a','honors','frezat']:X(i,'savinhan','串通作证使其失去财产',v,'Jean转述Savinhan的指控；不据此建立已证实共谋或加害边')
v=V(15,209,'Savinhan','La même semaine',date='1322-11-30',length=1700)
for i in ['cogul','magre','autast','vaissiere','franque','amilhac']:A('savinhan',i,'social','同批判入Mur并在狱中相处',v,directed=False)
A('vaissiere','savinhan','communication','将严厉判决与主教、Sabartès什一税纠纷联系',v,'记录囚犯的解释；不是替其证明主教动机')
v=V(15,209,'Savinhan','Pierre de Spinalbel, mon beau-frère',date='1322-11-30',length=1100)
A('spinalbel','savinhan','kinship','beau-frère，姻亲',v,directed=False)
A('helie','savinhan','kinship','cousin germain，一代表／堂亲',v,directed=False)
A('spinalbel','savinhan','communication','以Gaillac不会使他冒险来劝他接受建议',v,'属于Savinhan此前诱导供述叙事的一部分，后有修订',mode='reported_disputed')
v_acc=v
v=V(15,210,'Savinhan','Guillaume Cavatier',date='1322-11-30',length=550)
A('savinhan','cavatier','communication','押往监狱途中抱怨Gaillac建议不好',v)
v=V(15,210,'Savinhan','Bernard Clergue de Mon',date='1322-11-30',length=1800)
A('bernard_clergue','savinhan','communication','在狱中评论判决、告白与主教',v)
A('bernard_clergue','pierre_clergue','kinship','兄弟',v,directed=False)
A('bernard_clergue','amilhac','social','在Mur同住',v,directed=False)
for i in ['amilhac','vaissiere']:A(i,'savinhan','communication','报告Bernard拟付钱促Béatrice撤回对Pierre的证言',v,'转述链；金额约50里弗、收款对象需进一步对读，不能写成已付款')
X('bernard_clergue','beatrice_prison','贿赂成功并已撤回证词',v,'只报告要求中间人促成撤回及许诺金钱；未报告实现')
v=V(15,211,'Savinhan','ma femme Bernarde',date='1322-11-30',length=1300)
A('savinhan','bernarde_s','kinship','婚姻',v,directed=False)
A('savinhan','bernarde_s','communication','在家抱怨失去财产',v)
A('savinhan','peyre_quie','communication','在路上抱怨惩罚并说明旧信念',v)
v=V(15,212,'Savinhan','Je rencontrai en chemin Guillaume de Niaux',date='1322-11-30',time='1322年9月左右',length=1700)
A('niaux_g','savinhan','communication','在门前共同抱怨Gaillac并谈追回财产',v)
A('tron','savinhan','communication','说Gaillac曾向审讯者中伤他',v,'记录转述，不编码Gaillac实际诬告')
T('savinhan','recantation_motive','承认自己希望主教救济或归还财产，因此声称受Gaillac诱导虚假认罪；又承认原先确实持那些观点。',v)
v=V(15,213,'Savinhan','Cousin, avouez la vérité',date='1322-11-30',length=1100)
A('gaillac','savinhan','communication','修订说法：只在真正相信时才承认相信',v,'与前述诱导虚假认罪版本分开')
X('gaillac','savinhan','诱导其承认从未相信的异端观点',v_acc,'本次讯问后段撤回；保留证言变化，不作已证实诱供关系',v)
v=V(15,214,'Savinhan','la femme de Pierre den Hugol',date='1323-05-12',length=350)
A('hugol','hugol_w','kinship','婚姻',v,directed=False)
v=V(15,215,'Savinhan','la femme de Guillaume Delaire',date='1323-05-12',length=750)
A('delaire','delaire_w','kinship','婚姻',v,directed=False)
T('savinhan','negative_observation','称未见Delaire妻佩戴十字；称两位同教区女性未前来受鞭；未见不等于从来没有履行。',v,'delaire_w;hugol_w')
# C016: hearsay about consolamentum distinguished from eyewitness accompaniment.
N('amiel','Pierre Amiel','Rabat居民；临终时据说接受入教仪式',219,'dead')
N('andre_prades','André [accompagné par Magre]','被Delaire称为bon chrétien；编者认为即Prades Tavernier',219,'uncertain')
N('tavernier','Prades Tavernier','Magre说长期相信是好人的宗教人物；编者称织工出身',220,'uncertain','本批不把姓名校订当成证人亲自的同一认定')
v=V(16,219,'Pierre Magre','trouvai là Guillaume Delaire',date='1320-04-21',time='约18年前，Pierre Amiel临终疾病期间',length=1500)
A('delaire','magre','communication','请求同行并介绍André',v)
A('magre','delaire','social','从Plan de Serres同行到La Campagne',v,directed=False)
A('magre','andre_prades','social','亲自伴行',v,directed=False)
A('delaire','andre_prades','social','同行',v,directed=False)
A('delaire','magre','communication','告知André已为Amiel施入教仪式',v)
A('andre_prades','amiel','ritual','据Delaire转述在临终时接纳为bon chrétien',v,'Magre未目睹仪式，且未听André本人说明',mode='hearsay')
v=V(16,220,'程序记录／Pierre Magre','Prades Tavernier',date='1321-03-07',length=400)
A('magre','tavernier','belief','长期认为是bon homme',v,'信任／评价不等于亲眼相见')
v=V(16,221,'Jean Duvernoy，注3','Prades Tavernier, tisserand',length=850,layer='editorial_note')
I('andre_prades','tavernier','candidate_same_editorial','编者明确认同；正文从André转称ce Prades也有线索，但保留两个节点，待跨案核定再合并',v)
I('magre','Pierre Magre [C015 p209]','same','相邻案同名人物，第16案注4与第15案同批判刑、释放时间吻合；复用magre')
# Actual reading ledger: one entry per printed page, including notes; plates separated below.
notes3='''55|拘捕同住者；拒誓并称癫痫；案首年号与后文1319并列，不擅自抹平
56|自称Eclose神父教禁誓、教两女；卷轴来源；否认死者代祷效力
57|Pierre lo Clergue教学说；8月11日撤回姓名、教学与炼狱表述
58|四位Vienne同伴；迁居经济理由与读书；12月信经审讯开始
59|创造、道成肉身、复活、审判与圣事定义
60|婚姻同意、终傅与授职的一般教义
61|自称由Maurienne主教Jean授职；后文另叙Jean Lorrain，须辨版本
62|三位一体措辞及12月21日禁誓解释
63|禁誓与殉道；对司法处死的区别回答
64|12月29日、31日关于教会强迫发誓的争辩与修订
65|良心、服从、绝罚；1月2日续讯
66|有条件服从及授职领袖也反对发誓
67|majoral名称、拒绝透露所在地；选举的一般假设
68|领袖告解、授职程序，不是逐项实见事件
69|自己授执事；按手与集体选举说明
70|年轻人训练、誓愿、纪律与重新接纳
71|无领袖时的选举、躲避逮捕；未见majoral授职
72|圣餐做法含推测；告解、补赎的一般说明
73|Roman与本派圣事效力、赦罪范围
74|罪责、刑罚、临终悔改及否认炼狱
75|不为亡父母代祷施舍；条件性愿意；未见同伴死亡葬礼；遗赠功德
76|圣人听祈祷并代祷；埋葬利益不明；神父权能与洗足
77|圣餐纪念食物及书中形式；1月7日告解修订
78|劝悔与神赦罪、领袖与同伴的职分
79|本人授职细节；执事服务职责；否认公开读福音
80|贫穷劳动与迫害、司提反类比
81|共有财产、教宗及讲道权力
82|女性及已婚者限制、服从誓愿与疑难
83|拒绝导致处死的告发；假设囚禁异端不杀
84|鳏夫及再婚、贞洁、身体习惯
85|婚姻与授职；传道授权、告发疑虑
86|服从上级与教宗冲突；赦罪钥匙
87|弥撒礼式及绝罚有效性的承认
88|鼓励参加天主教弥撒、告解领圣体；拉丁语及教堂祈祷
89|基督论；降临limbo与否认purgatory的区别
90|教会、信仰行为与异端圣事有效性
91|审讯者指出矛盾；承认两派圣事与罗马教宗首位
92|教会保持信仰与不愿违背上帝的自辩
93|迫害、圣洁及封圣条件的一般主张
94|什一税、受谴责团体、同一身体复活
95|复活后的性别年龄身材、圣体性质、审判不可逆
96|圣人现时见神不如复活后；1月12日洗礼与未受洗婴儿
97|父母信仰中受洗、形式；1月14日迫害论
98|临终补赎的疑难、无炼狱；上级赦罪权限
99|偿还他人财物、圣餐形式；亡者祷文问题
100|要求将弥撒亡者祷文改为生者；婚姻与教宗禁令
101|夫妻同意出家、坚振与按手圣事修订
102|坚振是否需圣油；本派交由罗马教会施行坚振
103|入道礼、誓愿、贫穷规范；27年前入道及匿名已故导师
104|父家、学校、Jean授职、Michel教学、领袖继任；死后爱戴Jean；旅行
105|以《马加比》及教父权威争论亡者代祷
106|教会法及迫害；详细日课祷文
107|日课、餐桌祝福、斋戒；三书分别得自Jean、Jacques、André
108|审讯方归纳所谓错误；不得误认全部是新的自发供述
109|审讯归纳教会权威与绝罚观点及矛盾
110|归纳授职程序；提到本人Jean授职
111|归纳炼狱、亡者代祷、誓愿等；与问答区分
112|归纳讲道、杀人、洗礼、坚振；请求八天考虑
113|1月19日教父权威逐项阅读；1月23日再劝回归
114|拒绝核心撤回；部分撤回洗礼、坚振、已婚授职及完美状态观点
115|补充撤回；Motier与Maurin；承认反抗上级；授权信与4月24日讯问
116|4月末拒绝揭露同伴；请求判决；传唤程序及见证人
117|校订署名；注1至12开始；案号标题与历史说明
118|注12至25；Curia押返、信经、程序日期、编者解释其早期自辩
119|注26至36；程序日期、圣餐跨史料比较、女性与经文
120|注37至49；领袖继任插句解释及跨史料身份候选，未直接入人物网
121|注49至67；礼仪与引文出处、编辑解释，不等于新证词
122|注68至76；Maurin候选识别、判决文本未存及5月1日处刑交叉参照'''
notes14='''191|两名证人开场；女孩转述、磨坊谈话及Valentin遇害后墓地声响
192|Caussou说她似在怀疑；Gaillarde断言版本、父名、乞食、炉边转述、遭嫌恶
193|Rouch转述女孩；炉边日期与女孩有差异；传票并列Pons Mériana
194|3月否认及逮捕；4月坚持；5月承认墓地传闻与磨坊话题
195|否认断言及宣誓；6月术法寻布、女婿、Pellicier之女、未目睹施术
196|承认短暂疑惑；Raimond Carot遗孀身份；弃绝、赦免条件
197|1321年确认口供、听判日期；注1至10开始，不能把判刑推测当事实
198|注10至13；其他术法比较材料、未知判决、拉丁版对照页码'''
notes15='''199|Cordier自Pamiers带末世消息；桥头四听众；Savinhan反驳
200|Mayshelac与Beubre各自回忆同一聚谈，时间约数不同
201|Beubre称异端家族；5月9日讯问；主教住Niaux家；Savinhan以俗谚回应
202|复活后身体归无主张；5月11日说Frézat与Gaillac教导后改变
203|7月承认说过、否认相信，称Tolus为师；9月拘押
204|10月供认30年观点与5月起改变；无受刑声明是记录的自述
205|石匠职业、无暇听讲道、俗谚与公共言论；1321判决及1322复审开头
206|Vésian邻居、佩十字观察、房屋40里弗及损失抱怨；Thibaud父名
207|Thibaud见工作；Montanié邻居磨坊、被指共谋者、Gaillac为cousin
208|Savinhan详述藏起十字及只在主教所在处公开佩戴
209|同批囚犯与Vaissière解释；Gaillac诱导说；Spinalbel和Hélie亲属
210|坚持被诱导说；向Cavatier抱怨；Clergue兄弟、Amilhac及Béatrice撤供许诺转述
211|妻Bernarde、Vésian、Montanié、Turière、Peyre听抱怨；重读旧供词
212|确认旧信念；Niaux与Tron传话、期望返还财产；承认诱导说失实
213|Gaillac建议改述为只认真实相信的事；撤回诱供指控、弃绝
214|弃绝结束；1323年再讯佩十字；Niaux、Hugol妻的观察
215|Delaire妻同教区；注1至5及其他档案的Niaux背景，分层处理
216|注6至21；读写能力推论、Gaillac背景、房屋回赎解释与正文时序张力
217|注22至31；什一税争端背景、保释、监狱与磨坊工艺解释
218|注32至33；1323严格监禁与1329释放出自其他文书，不当本案直接证词'''
notes16='''219|Magre护送André；Delaire转告临终Amiel入教；亲历和听说分开
220|夜暗难辨、听闻村内传言、否认敬拜；1321确认及Prades好人评价；判决引录
221|编者注：André认同Prades Tavernier；判监与释放交叉文书，不冒称正文亲见'''
ledger=[]
for c,block in [(3,notes3),(14,notes14),(15,notes15),(16,notes16)]:
 for line in block.splitlines():
  p,s=line.split('|',1);p=int(p);pdf=p+(36 if p<63 else 38 if p<95 else 40)
  ledger.append(dict(case_id=f'C{c:03}',printed_page=p,pdf_page=pdf,reading_status='full_text_read',source_layer='body_and_notes' if p in [117,197,215] else 'editorial_notes' if (c==3 and p>=118) or (c==14 and p==198) or (c==15 and p>=216) or (c==16 and p==221) else 'body',content_note_zh=s,page_text_sha256=hashlib.sha256(pages[pdf-1].encode()).hexdigest(),method='逐页全文阅读OCR文本；不是关键词命中推定通读；未逐字核对原版图像'))
for pdf in [99,100,133,134]:
 ledger.append(dict(case_id='C003',printed_page='',pdf_page=pdf,reading_status='caption_read_image_not_reviewed',source_layer='plate',content_note_zh='插图页不属于审讯正文；仅读图题，未以图像补证',page_text_sha256=hashlib.sha256(pages[pdf-1].encode()).hexdigest(),method='图题阅读'))
reviews=[]
for c,title,lo,hi in [(3,'Raymond de Sainte-Foy',55,122),(14,'Jacqueline den Carot',191,198),(15,'Arnaud de Savinhan',199,218),(16,'Pierre Magre',219,221)]:
 reviews.append(dict(case_id=f'C{c:03}',title=title,printed_pages=f'{lo}-{hi}',reading_status='full_text_read_including_notes',extraction_status='selected_named_relations_and_thematic_statements',direct_gelis_relation='not_found_in_read_testimony',limitation_zh='全文通读不等于所有程序见证人均已穷尽入库；编者交叉引用不是人物社交边；未作拉丁校勘'))
for name,rows in [('new_nodes.csv',people),('assertions.csv',edges),('evidence.csv',ev),('excluded_claims.csv',claims),('thematic_statements.csv',themes),('node_updates.csv',updates),('identity_decisions.csv',identities),('reading_log.csv',ledger),('case_review.csv',reviews)]:write(name,rows)
manifest=dict(batch='expansion_02',source_pdf_sha256=source['sha256'],full_text_cases=[3,14,15,16],printed_pages_read=len(ledger)-4,plate_captions=4,new_nodes=len(people),new_assertions=len(edges),evidence_records=len(ev),excluded_claims=len(claims),thematic_statements=len(themes),next_case=17,old_batches_preserved=True)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Assertions are relations attested in testimony, not certification that every narrated event occurred.
for e in edges: assert e['source'] in known and e['target'] in known
for e in ev:
 s=re.sub(r'\s+',' ',pages[e['pdf_page']-1]).strip()
 assert s[e['normalized_char_start']:e['normalized_char_end']]==e['excerpt_fr_ocr']
for c,lo,hi in [(3,55,122),(14,191,198),(15,199,218),(16,219,221)]:
 assert {r['printed_page'] for r in ledger if r['case_id']==f'C{c:03}' and r['printed_page']!=''}==set(range(lo,hi+1))
print(json.dumps(manifest,ensure_ascii=False))
