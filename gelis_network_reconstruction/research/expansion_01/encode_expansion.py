import csv,json,re,hashlib,unicodedata,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]; out=Path(__file__).resolve().parent
pages=Path(sys.argv[1]).read_text().split('\f'); source=json.loads((root/'data/source_manifest.json').read_text())
def norm(s): return re.sub(r'\s+',' ',s).strip()
def write(name,rows):
 with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
people=[];ev=[];edges=[];excluded=[]
core=list(csv.DictReader((root/'data/nodes.csv').open(encoding='utf-8-sig'))); known={x['id'] for x in core}
def N(id,name,role,p,status='living',note=''):
 assert id not in known,id; known.add(id)
 people.append(dict(id=id,name=name,role_zh=role,status=status,group='前七案扩展',identity_note=note,printed_pages=str(p),source_basis='扩展01；见assertions/evidence，未关联者为身份标题或人物登记'))
def V(case,p,pdf,speaker,anchor,date='',time='',notes='',length=480):
 s=norm(pages[pdf-1]); assert anchor.casefold() in s.casefold(),(pdf,anchor)
 pos=s.casefold().index(anchor.casefold()); start=max(0,pos-50);end=min(len(s),pos+length)
 id=f'v{len(ev)+1:03}'
 ev.append(dict(evidence_id=id,source_id='duvernoy1978_user_scan',case_id=f'C{case:03}',printed_page=str(p),pdf_page=pdf,speaker=speaker,deposition_date=date,event_time_expression=time,anchor=anchor,excerpt_fr_ocr=s[start:end],normalized_char_start=start,normalized_char_end=end,page_text_sha256=hashlib.sha256(pages[pdf-1].encode()).hexdigest(),source_pdf_sha256=source['sha256'],source_layer='translated_register',verification='text_read; PDF text-layer page location checked; not Latin/facsimile collated',notes_zh=notes))
 return id
def A(a,b,layer,rel,v,detail='',directed=True,mode='reported',outcome='attested'):
 assert a in known and b in known,(a,b)
 e=next(x for x in ev if x['evidence_id']==v)
 edges.append(dict(edge_id=f'x01_{len(edges)+1:03}',source=a,target=b,layer=layer,relation_zh=rel,directed=str(directed).lower(),evidence_mode=mode,outcome=outcome,printed_pages=e['printed_page'],deposition=e['speaker'],detail_zh=detail,evidence_id=v,case_id=e['case_id'],event_time_expression=e['event_time_expression']))
def X(a,b,claim,v,reason):
 excluded.append(dict(claim_id=f'neg{len(excluded)+1:03}',source=a,target=b,claim_zh=claim,evidence_id=v,disposition='excluded_from_graph',reason_zh=reason))
# Case 1: ordinary interactions and a deliberately non-exhaustive procedural layer.
for row in [
('aude','Aude de Maucasal','Merviel居民；Guillaume Fauré妻',31,'living','原籍Lafage；不是其他案件同名女性'),
('faure_m','Guillaume Fauré [Merviel]','Aude丈夫',31,'living','不与Saint-Bauzeil的Guillaume Fauré合并'),
('maucasal','Guillaume de Maucasal','Aude亡父；Lafage人',31,'dead',''),
('garaud','Ermengarde Garaud','Merviel年长女性；劝慰者、证人',35,'living','tia不构成亲属证据；p.36明确否认与Aude有亲属关系'),
('infirmerie',"Guillaume de l’Infirmerie",'神父；Merviel／Ventenac代牧',37,'living','职衔在证词和传票中不同，均保留'),
('escribe','Geoffroy Escribe','Ventenac居民；证人',37,'living','第7案再出现'),
('quie','Bernard de Quié','Merviel居民；证人',37,'living',''),
('montventoux','Jean de Montventoux','Merviel居民；证人',37,'living',''),
('jean_garaud','Jean Garaud','Ermengarde之子；证人',37,'living',''),
('alazays_nurse','Alazays [épouse de Pregolh]','Aude家庭的乳母',39,'living','不与Alazays Garnis合并'),
('pregolh','Raimond de Pregolh','Merviel居民；乳母之夫',39,'uncertain',''),
('aude_son','Fils d’Aude [anonyme]','Aude与Guillaume之子；受乳儿',39,'living',''),
('alazays_g','Alazays [veuve d’Arnaud Garnis]','Merviel寡妇；探病者、证人',39,'living',''),
('arnaud_g','Arnaud Garnis','Alazays亡夫',39,'dead',''),
('raimonde_g','Raimonde [veuve de Pierre Garnis]','Merviel寡妇；探病者、证人',40,'living',''),
('pierre_g','Pierre Garnis','Raimonde亡夫',40,'dead','不由同姓推出与Arnaud的亲属关系'),
('guillemette_athon','Guillemette d’Athon','Aude的女仆；Limbrassac人之女',42,'living','fille suivante不译为女儿'),
('arnaud_athon','Arnaud d’Athon','Limbrassac居民；Guillemette父',42,'uncertain',''),
('den_raimond','Guillemette den Raimond','Merviel房屋主人；病者领圣餐地点',40,'living','与女仆Guillemette分开'),
('cure_sc','Curé de Sainte-Croix [anonyme]','Aude告解对象',33,'living','不强并Guillaume de l’Infirmerie或丈夫召来的匿名神父'),
('priest_aude','Prêtre appelé par Guillaume [anonyme]','丈夫召来的告解神父',34,'living','与Sainte-Croix神父可能同一；保留未决'),
('verdier','Pierre du Verdier','Majorque总铎；审讯顾问',31,'living',''),
('bilheres','Hugues de Bilhères','Pamiers上诉法官',31,'living',''),
('saintjulien','Guillaume de Saint-Julien','Pamiers法律人士',31,'living',''),
('gaubert','Bernard Gaubert','Narbonne教区法律人士；另称神父',31,'living',''),
('pardailhan','Guillaume de Pardailhan','宗座公证人',31,'living',''),
('arnaud_melonier','Arnaud Melonier','Pamiers市民；第1案判决见证者',46,'living','与Pierre-Arnaud Melonier的同一性未定')]:N(*row)
v=V(1,31,67,'程序记录／Aude','Aude, fille de feu Guillaume','1318-07-15');A('maucasal','aude','kinship','父女',v);A('faure_m','aude','kinship','婚姻',v,directed=False)
v=V(1,32,68,'Aude','mon mari me dit alors','1318-07-15','近期重病时');A('faure_m','aude','social','以遣离相威胁并要求告解',v);A('aude','faure_m','communication','透露信仰困扰',v)
v=V(1,32,68,'Aude','Ermengarde me reprit fortement','1318-07-15');A('garaud','aude','communication','劝诫并讲述圣餐奇迹故事',v,'故事中的匿名古代人物不进入当时地方社会网')
v=V(1,33,69,'Aude','au curé de Sainte-Croix','1318-07-17','约一月前');A('aude','cure_sc','ritual','告解',v);A('cure_sc','aude','ritual','减轻所提补赎',v)
v=V(1,34,70,'Guillaume Fauré','fis alors venir pour elle un prêtre','1318-07-17');A('faure_m','priest_aude','communication','请神父为妻告解',v);A('aude','priest_aude','ritual','告解',v)
v=V(1,36,72,'Ermengarde Garaud','venir souvent la voir','1318-07-17');A('aude','garaud','communication','请求经常探访安慰',v,outcome='unknown')
v=V(1,36,72,'Ermengarde Garaud',"j'ai révélé ce qu'elle",'1318-07-17');A('garaud','infirmerie','communication','透露Aude的话',v);X('infirmerie','fournier','已向主教报告',v,'证人仅称Je crois；不升级为确认发生')
v=V(1,36,72,'Ermengarde Garaud',"Etes-vousparente d ' A u d e",'1318-07-17');X('garaud','aude','tia表示血亲姑姨',v,'明确答Non；仅亲昵称呼')
v=V(1,37,73,'Guillaume de l’Infirmerie','Ermengarde Garaud venait','1318-07-19','前一周四清晨');A('garaud','infirmerie','ritual','病中告解',v)
v=V(1,37,73,'Guillaume de l’Infirmerie','je fis appel à maître Geoffroy','1318-07-19',length=850)
for id in ['escribe','quie','montventoux','jean_garaud']:
 A('infirmerie',id,'communication','召集听取Ermengarde陈述',v)
 A('garaud',id,'communication','病榻前转述Aude言语',v)
A('garaud','jean_garaud','kinship','母子',v)
v=V(1,39,75,'Aude',"mon mari prit pour nourrice",'1318-07-24');A('faure_m','alazays_nurse','social','雇用乳母',v);A('alazays_nurse','pregolh','kinship','婚姻',v,directed=False);A('aude','aude_son','kinship','母子',v);A('alazays_nurse','aude_son','social','乳养',v)
v=V(1,42,78,'程序记录／Guillemette d’Athon',"Guillemette d'Athon, fille",'1318-07-29');A('arnaud_athon','guillemette_athon','kinship','父女',v);A('guillemette_athon','aude','social','家庭服务／女仆',v)
v=V(1,42,78,'Aude及Alazays、Raimonde当面对质',"Le même jour, sur le soir",'1318-07-29',notes='前两名证人起初否认；对质后承认。地点以更正后Aude家为准。',length=1000)
for id in ['alazays_g','raimonde_g']:A(id,'aude','social','晚间探病并劝慰',v,'见同页随后承认；先前否认不删除，记入争议记录')
v=V(1,41,77,'程序记录','Alazays, veuve', '1318-07-29');A('alazays_g','arnaud_g','kinship','生前婚姻',v,directed=False);A('raimonde_g','pierre_g','kinship','生前婚姻',v,directed=False)
v=V(1,43,79,'Alazays乳母',"Nous allâmes donc toutes les deux",'1318-08-02',length=950);A('alazays_nurse','aude','social','共同前往领圣餐地点并返回',v,directed=False);A('alazays_nurse','aude','ritual','应要求跪地祈祷',v);A('guillemette_athon','aude','ritual','应要求跪地祈祷',v)
v=V(1,40,76,'Aude',"mais chez Guillemette den Raimond",'1318-07-29');X('alazays_nurse','den_raimond','房主亲自接待乳母',v,'只证明领圣餐地点属于其房屋，未证明人际互动')
v=V(1,31,67,'程序记录','Mondit seigneur évêque, ayant appelé','1318-07-15',length=750)
for id in ['verdier','bilheres','saintjulien','gaubert','pardailhan']:A(id,'fournier','judicial','受召协助保密调查',v,mode='procedural')
A('fournier','aude','judicial','主持审讯',v,mode='procedural')
v=V(1,46,82,'程序记录','Arnaud Melonier et Raimond','1318-08-07',notes='仅判决在场，不据此推出他与Aude或其他见证者的私人交往');A('arnaud_melonier','fournier','judicial','判决程序见证',v,mode='procedural')
# Case 2
for row in [('sabatier','Pierre Sabatier','Varilhes织工；被审者',49,'living',''),('masse','Bernard Masse','织工；Sabatier姻亲及师傅',49,'dead','beau-frère具体方向不明'),('helis','Hélis [veuve de Guillaume Mate]','Varilhes寡妇',50,'living',''),('mate','Guillaume Mate','Hélis亡夫',50,'dead',''),('gout','Arnaud Gout','Varilhes居民；谈话听众',50,'dead','发言时活着，审讯时已死'),('wife_sabatier','Épouse de Pierre Sabatier [anonyme]','共同朝圣的妻子',50,'living',''),('father_sabatier','Père de Pierre Sabatier [anonyme]','来自Bagan',51,'uncertain',''),('mother_sabatier','Mère de Pierre Sabatier [anonyme]','来自Saint-Gaudens',51,'uncertain','')]:N(*row)
v=V(2,49,85,'Pierre Sabatier','Bernard Masse, mon défunt beau-frère','1318-10-23');A('masse','sabatier','kinship','姻亲（beau-frère）',v,directed=False);A('masse','sabatier','social','据称诬告后临终求原谅',v,'仅Sabatier陈述；p.50-51后承认确说过带条件的话，不代表诬告已被证实')
v=V(2,50,86,'Pierre Sabatier',"étant entendu d'Hélis",'1318，圣凯瑟琳节前星期二；译本括注日期有疑',length=520);A('sabatier','helis','communication','评论教会仪式',v);A('sabatier','gout','communication','评论教会仪式',v);A('helis','mate','kinship','生前婚姻',v,directed=False)
v=V(2,50,86,'Pierre Sabatier',"avec sa femme",'1318-11-06','上年Montserrat；当年Compostelle');A('sabatier','wife_sabatier','kinship','婚姻',v,directed=False);A('sabatier','wife_sabatier','social','共同朝圣',v,directed=False)
v=V(2,51,87,'Pierre Sabatier',"m'apprit ensuite le métier de tisserand",'1318，圣凯瑟琳节前星期二','约25年前的谈话；教学在后');A('masse','sabatier','social','传授织工手艺',v);A('masse','sabatier','communication','询问临终蜡烛意义',v);A('sabatier','masse','communication','解释蜡烛与认罪悔改',v)
v=V(2,51,87,'Pierre Sabatier','Mon père était de Bagan');A('father_sabatier','sabatier','kinship','父子',v);A('mother_sabatier','sabatier','kinship','母子',v)
v=V(2,50,86,'程序记录','Jacques Camelie, Bernard Gaubert',notes='法译Camelie/Camelle拼写变体；与核心camelle暂作同一，依据姓名+法律身份+Pamiers语境；可撤回',length=600);A('camelle','fournier','judicial','担任审讯顾问并宣誓保密',v,mode='procedural')
# Cases 3-6: household, instruction, intimacy, and urban acquaintances.
for row in [
('saintefoy','Raymond de Sainte-Foy','瓦尔多派执事；alias de la Côte',55,'living','生死状态为所编码交往时；1320年处刑见第7案'),
('agnes','Agnès [veuve de Francou]','Vermelle寡妇；Raimond乳母',123,'living','1320年处刑；身份以p.125更正后自述'),
('francou','Etienne Francou','Agnès亡夫',123,'dead',''),
('jean_v','Jean de Vienne','桶匠；Huguette丈夫',128,'living','alias Fustier、Marinier；第3案初称charpentier，p.141妻称tonnelier'),
('huguette','Huguette [épouse de Jean de Vienne]','瓦尔多派信徒；Jean妻',140,'living','不与Agnès所称已死同名房东合并'),
('petrone','Pétrone [sœur de Jean]','Jean之姊妹；逃离Pamiers者',141,'living','Pétronille的对应需逐段判断；不自动合并Pascal同名女性'),
('jeanne_ray','Jeanne [sœur de Raimond]','Raimond之姊妹；同住者',125,'living','按Agnès、Huguette的称谓'),
('jacqueline_ray','Jacqueline [parente de Raimond]','Raimond亲属；同住者',141,'living','不与Jacqueline Othon或Avignon旅店主人合并'),
('etienne_nephew','Etienne [neveu de Raimond]','Raimond侄／甥；同行者',145,'living','不与仆人Etienne强并'),
('etienne_servant','Etienne [domestique de Raimond]','Raimond仆人；与Pétrone逃离',147,'living','先前称Jean，p.147明确更名'),
('jeanne_m_sis','Jeanne [sœur d’Arnaud Melonier]','Pamiers来访者',125,'living','不与Arnaud之妻Jeanne合并'),
('jeanne_m_wife','Jeanne [épouse d’Arnaud Melonier]','Huguette的教堂同行者',145,'living','不与同姓丈夫之姊妹Jeanne合并'),
('barcelone_bl','Barcelone [épouse de Bernard de Loubens]','Huguette的教堂同行者',145,'living','不与Guillaume de Loubens妻Barcelone合并'),
('bernard_loubens','Bernard de Loubens','Barcelone之夫',145,'uncertain','不与Guillaume de Loubens合并'),
('jeanne_pc','Jeanne [épouse de Pierre de Calmelles]','Huguette教堂同行者',145,'living',''),
('pierre_calmelles','Pierre de Calmelles','Jeanne之夫',145,'uncertain','不与Arnaud de Calmelles合并'),
('guillemette_paredes','Guillemette [épouse de Jean Parédès]','Huguette教堂同行者',145,'living','不与邻居泥瓦匠之妻直接合并'),
('jean_paredes','Jean Parédès','Guillemette之夫',145,'uncertain',''),
('guillemette_mason','Guillemette [épouse du maçon]','瓦尔多同住者的邻居；来访者',125,'living','可能与Parédès妻同人，未决'),
('mason','Maçon voisin [anonyme]','Pamiers泥瓦匠；Guillemette夫',125,'uncertain',''),
('jean_lorrain','Jean le Lorrain','瓦尔多派majoral；教师、告解者',104,'dead','生前教学与死后爱戴分开编码'),
('michel','Michel l’Italien','瓦尔多派神父；教师',104,'dead',''),
('barthelemy_w','Barthélémy [diacre vaudois]','瓦尔多派执事；同伴',104,'dead',''),
('moran','Jean Moran','瓦尔多派神父；同伴',104,'dead','不与Jean Mourier自动合并'),
('mourier','Jean Mourier','Jean de Vienne的引介者',131,'uncertain',''),
('guirard','Guirard [maître d’Huguette]','教授Huguette禁誓的瓦尔多信徒',142,'uncertain','不与Girard le Provençal自动合并'),
('bertrande','Bertrande de Tarascón','Arles住房主人；Huguette居所',142,'uncertain',''),
('roux','Jean Roux','面包师；Huguette亡父',141,'dead',''),
('petrone_mother','Pétrone [mère d’Huguette]','Huguette母亲',141,'uncertain','不与其小姑Pétrone合并'),
('jacqueline_av','Jacqueline [hôtelière d’Avignon]','识字旅店女主人；约40岁',133,'living','不与Raimond亲属或Othon妻合并'),
('ray_father','Père de Raimond [anonyme]','Genevois人；聘乳母者',125,'uncertain',''),
('ray_mother','Mère de Raimond [anonyme]','Raimond亡母',125,'dead',''),
('huguette_host','Huguette [hôtesse de Beaumont]','Agnès所称已死房东',124,'dead','死亡仅Agnès声称，不推为确证'),
('etienne_priest','Etienne [vicaire de Vermelle]','Agnès最初称授禁誓的神父',123,'uncertain','后来改称由Raimond教导，不自动判定此人不存在')]:N(*row)
v=V(3,55,91,'程序记录','est venu habiter Pamiers avec',notes='明确同屋居住；不将所有住客两两连边')
for id in ['agnes','jean_v','huguette']:A('saintefoy',id,'social','同屋居住',v,directed=False)
v=V(3,104,144,'Raimond de Sainte-Foy',"C'est Jean Lorrain",time='被捕前长期经历；相对年数见原文',length=1000);A('jean_lorrain','saintefoy','ritual','授执事职',v);A('jean_lorrain','saintefoy','communication','教授圣经并安排学习',v);A('michel','saintefoy','communication','教授圣经',v)
v=V(3,104,144,'Raimond de Sainte-Foy',"j'aimais beaucoup, et que j'aime encore après sa mort",length=370);A('saintefoy','jean_lorrain','care','明确表达死后仍然爱戴',v,'没有显灵；与主张不为死者行代祷并存');A('saintefoy','jean_lorrain','social','共同旅行包括意大利',v,directed=False)
v=V(3,104,144,'Raimond de Sainte-Foy','Avec le ministre Jean, avec le prêtre Michel')
for id in ['michel','barthelemy_w','moran']:A('saintefoy',id,'social','长期相处／停留',v,directed=False)
v=V(4,123,163,'程序记录／Agnès',"Agnès, veuve",'1319-08-10');A('agnes','francou','kinship','生前婚姻',v,directed=False)
v=V(4,124,164,'Agnès','une femme nommée Huguette','1319-08-10');A('agnes','huguette_host','social','在Beaumont同住约一月',v,directed=False)
v=V(4,125,165,'Agnès',"car j'ai été sa nourrice",'1320-01-18','Raimond婴儿期',notes='推翻初次供称只认识一年半',length=380);A('agnes','saintefoy','social','乳养',v);A('ray_father','agnes','social','母亲死后雇乳母',v);A('ray_father','saintefoy','kinship','父子',v);A('ray_mother','saintefoy','kinship','母子',v)
v=V(4,125,165,'Agnès',"Jeanne, la sœur d'Arnaud Melonier",'1320-01-18',length=680);A('jeanne_m_sis','arnaud_melonier','kinship','姊妹／兄弟',v,directed=False);A('guillemette_mason','mason','kinship','婚姻',v,directed=False)
for id in ['jeanne_m_sis','guillemette_mason']:A(id,'jeanne_ray','social','来访、共食饮酒',v,directed=False)
A('jeanne_ray','saintefoy','kinship','姊妹／兄弟',v,directed=False)
v=V(4,126,166,'Agnès',"C'est Raimond de la Côte",'1320-04-25','约二十年');A('saintefoy','agnes','communication','教授禁誓',v,'与p.123初称只有神父Etienne教导不一致，保留变更')
v=V(5,131,171,'Jean de Vienne',"C'est Jean le Lorrain",'1321-03-13','约十二年前');A('jean_lorrain','jean_v','communication','用俗语读福音教授',v)
v=V(5,131,171,'Jean de Vienne',"J'avais été envoyé à ce Jean par Jean Mourier",'1321-03-13');A('mourier','jean_v','communication','通过熟人引介至Jean le Lorrain',v,'中间熟人匿名，未将两人伪装成当面直接交谈')
v=V(5,132,172,'Jean de Vienne',"changer à Toulouse de la petite monnaie",'1321-03-13');A('jean_v','mourier','social','受托换金币并交还',v)
v=V(5,132,172,'Jean de Vienne',"J e bus avec lui",'1321-03-13','被捕前三年约');A('jean_v','saintefoy','social','Montpellier共饮',v,directed=False)
v=V(5,132,172,'Jean de Vienne',"avant queje ne l'épouse",'1321-03-13');A('jean_v','huguette','kinship','婚姻',v,directed=False);A('huguette','jean_v','communication','婚前透露所属信仰',v)
v=V(5,133,173,'Jean de Vienne','une femme nommée Jacqueline','1321-03-16','两年前');A('jacqueline_av','jean_v','communication','教授信条及圣事分类',v)
v=V(6,141,181,'Huguette',"fille de Jean Roux",'1320-01-21');A('roux','huguette','kinship','父女',v);A('petrone_mother','huguette','kinship','母女',v);A('petrone_mother','huguette','social','父死后带往Arles抚养',v)
v=V(6,141,181,'Huguette',"Tout cela est faux",'1320-01-21');X('saintefoy','huguette','母舅与外甥女',v,'p.140初述，p.141明确撤回；不是可纳入的亲属边')
v=V(6,141,181,'Huguette',"Pétrone, sa sœur",'1320-01-21');A('petrone','jean_v','kinship','姊妹／兄弟',v,directed=False);A('huguette','petrone','social','共同迁往Pamiers',v,directed=False)
v=V(6,147,187,'Huguette',"il ne s'appelait pas Jean, mais Etienne",'1321-03-18');A('etienne_servant','saintefoy','social','仆役服务',v);A('etienne_servant','petrone','social','一同逃离',v,directed=False)
v=V(6,145,185,'Huguette',"Etienne, qui était le neveu de Raimond",'1321-03-16');A('saintefoy','etienne_nephew','kinship','叔伯舅／侄甥（方向细节未明）',v);A('jacqueline_ray','saintefoy','kinship','亲属（具体未明）',v,directed=False)
v=V(6,142,182,'Huguette',"J'habitais chez Bertrande",'1321-03-13','约十二岁；约十八年前');A('huguette','bertrande','social','居住其家',v,directed=False);A('guirard','huguette','communication','教授禁誓',v)
v=V(6,142,182,'Huguette',"je lui donnai une fois à boire et à manger",'1321-03-13');A('huguette','guirard','social','提供饮食',v);A('guirard','huguette','social','给一枚银币',v)
v=V(6,142,182,'Huguette',"poussée par Guirard",'1321-03-13','约十六年前');A('guirard','huguette','communication','引导去Montpellier见Jean',v);A('jean_lorrain','huguette','communication','教导禁誓及否认死后炼狱',v)
v=V(6,143,183,'Huguette',"une demi-livre de dattes",'1321-03-13',length=650);A('huguette','jean_lorrain','social','赠半磅椰枣',v);A('jean_lorrain','huguette','social','赠亚麻头巾和腰带',v);A('huguette','jean_lorrain','ritual','多次告解并相信获赦',v)
v=V(6,145,185,'Huguette',"J'avais quelques connaissances",'1321-03-16','圣安妮日一次；另有平时同行',length=650)
for id in ['jeanne_m_wife','barcelone_bl','jeanne_pc','guillemette_paredes']:A('huguette',id,'social','共同前往教堂',v,directed=False);X('huguette',id,'传授被称为异端的观点',v,'明确说未向她们谈这些观点；共去教堂不等于同属瓦尔多派')
for a,b in [('jeanne_m_wife','arnaud_melonier'),('barcelone_bl','bernard_loubens'),('jeanne_pc','pierre_calmelles'),('guillemette_paredes','jean_paredes')]:A(a,b,'kinship','婚姻',v,directed=False)
v=V(6,146,186,'Huguette',"Avec Jean mon mari",'1321-03-18');A('huguette','jean_v','communication','讨论并积极劝丈夫接受信仰',v)
# Case 7: transmission about an executed dead man, not apparition.
for row in [('escoulan','Bérenger Escoulan','Foix居民；谈论处刑者',151,'living','明确否认见过Raimond'),('gentille_e','Gentille [épouse d’Escoulan]','在Pierre Cayran家售酒；Bérenger妻',151,'living','不与Gentille Camier合并'),('cayran','Pierre Cayran','Foix酒馆房屋主人',151,'living',''),('gaillarde','Gaillarde [épouse de Germain Cayran]','酒馆交谈者',151,'living',''),('germain_c','Germain Cayran','Gaillarde之夫',151,'uncertain','不推定与Pierre亲属'),('mon_vernat','Mon de Vernat','Laroque d’Olmes酒馆经营者',151,'living','Mon由编者释作Raimond'),('faure_montaut','Fauré de Montaut','Pujols辖区公证人',153,'living','不与其他Faure合并'),('bauzeil','Guillaume Bauzeil','Ventenac教区长代理',153,'living',''),('prayols','Bernard de Prayols','Ventenac居民；共饮者',153,'living',''),('lombard','Bernard Lombard','Foix居民；共餐交谈者',155,'living',''),('letinier','Raimond Létinier','Foix居民；酒馆听众',155,'living',''),('bernard_serny','Bernard Serny','Foix居民；劝止议论者',155,'living','不与Jean Serny合并'),('carbonnier','Jacques Carbonnier','Foix酒馆经营者',155,'living',''),('alias','Pierre Arnaud den Alias','纠正禁誓观点者',155,'living','')]:N(*row)
v=V(7,151,191,'Gentille','Gentille, femme Je Bérenger','1320-05-06');A('gentille_e','escoulan','kinship','婚姻',v,directed=False)
v=V(7,151,191,'Gentille',"Gaillarde, la femme de Germain Cayran",'1320-05-06','上周五');A('gaillarde','germain_c','kinship','婚姻',v,directed=False);A('gaillarde','escoulan','communication','反对称处刑者为好人',v,'她对一群听众发言；不据此构造全体共场两两关系')
v=V(7,151,191,'Gentille',"à mon mari de sortir de la taverne",'1320-05-06');A('gentille_e','escoulan','communication','要求停止议论并离开酒馆',v)
v=V(7,153,193,'Guillaume Bauzeil','Fauré lui dit alors',time='1320年5月2日');A('faure_montaut','escoulan','communication','辩论禁誓与处刑',v)
v=V(7,153,193,'Guillaume Bauzeil',"Il y avait avec moi",time='1320年5月2日');
for id in ['faure_montaut','escribe','prayols','gaillarde']:A('bauzeil',id,'social','酒馆共饮',v,directed=False)
v=V(7,153,193,'Geoffroy Escribe',"et j e les entendis",time='1320年5月2日');A('escoulan','escribe','communication','称Raimond因批评教士被烧死',v)
v=V(7,155,195,'Bérenger Escoulan','Bernard Lombard, Raimond','1320-05-06','处刑当天');
for id in ['lombard','letinier','bernard_serny']:A('escoulan',id,'communication','谈论据闻处刑及灵魂获救',v)
v=V(7,155,195,'Bérenger Escoulan','Bernard Serny me répondit de me taire','1320-05-06','处刑日返回Foix途中');A('bernard_serny','escoulan','communication','要求停止质疑审判者',v)
v=V(7,155,195,'Bérenger Escoulan','Jacques Carbonnier, Raimond Létinier','1320-05-06','处刑翌日');
for id in ['carbonnier','letinier']:A(id,'escoulan','communication','询问是否目睹处刑',v)
v=V(7,155,195,'Bérenger Escoulan','Mon me demanda alors','1320-05-06');A('mon_vernat','escoulan','communication','询问是否见过被处刑者',v)
v=V(7,155,195,'Bérenger Escoulan','Pierre Arnaud den Alias','1320-05-06');A('alias','escoulan','communication','劝其相信为真话起誓非罪',v)
v=V(7,155,195,'Bérenger Escoulan','Avez-vous jamais vu ce Raimond','1320-05-06');X('escoulan','saintefoy','生前相识或目睹处刑',v,'明确否认；听闻死者的故事不能作相识或显灵边')
v=V(4,123,163,'Agnès',"curé qui s'appelait",'1319-08-10',notes='最初归因给神父Etienne，p.126又归给Raimond；没有证据直接断言Etienne虚构')
X('etienne_priest','agnes','最初自称神父Etienne教授禁誓',v,'暂不作确认的传授边；与p.126后说法并列待复核')
v=V(7,152,192,'Fauré de Montaut',"l'Eglise ne doit pas prier pour les morts",'1320-05-04',notes='证人说Escoulan对Raimond否认代祷持反对态度；不能概括为他全盘赞同')
A('faure_montaut','escoulan','communication','转述Raimond反对死者代祷的主张',v)
# Case coverage is granular and candid.
coverage=[]
for c,title,pp,pdf,status,detail in [
(1,'Aude de Maucasal','31-48','67-84','text_read_relations_selected','通读正文及注释；编码主要日常关系和选择性司法联系；未穷尽顾问名单'),
(2,'Pierre Sabatier','49-54','85-90','text_read_relations_selected','通读正文及注释；保留说法变化；p.54 Gélis仅编者比较'),
(3,'Raymond de Sainte-Foy','55-122','91-162','targeted_reading_not_complete','核读55-58、66-68、103-106、111、116-117；其余姓名检索，不声称逐页精读'),
(4,'Agnès Francou','123-127','163-167','text_read_relations_selected','通读；乳母身份更正与Pamiers来访者；程序名单不穷尽'),
(5,'Jean de Vienne','128-139','168-179','text_read_relations_selected','正文核读；附录判决为编者引录，仅查主要段落；未逐句编码'),
(6,'Huguette','140-150','180-190','text_read_relations_selected','通读；撤回亲属说法、改仆人名、教堂同行；未穷尽全部异地往来'),
(7,'Bérenger Escoulan','151-157','191-197','text_read_relations_selected','核读正文与注释；酒馆传播链；含p.152证词；不将同场者全连接')]:
 coverage.append(dict(case_id=f'C{c:03}',case_title=title,printed_pages=pp,pdf_pages=pdf,review_status=status,relationship_extraction='selected_not_exhaustive',notes_zh=detail))
write('new_nodes.csv',people);write('assertions.csv',edges);write('evidence.csv',ev);write('excluded_claims.csv',excluded);write('case_review.csv',coverage)
print('nodes',len(people),'assertions',len(edges),'evidence',len(ev),'excluded',len(excluded))
