#!/usr/bin/env Rscript
# Reproducible historical multiplex network. Run: Rscript render_networks.R
# No inferred tie from co-occurrence; edge rows are coded claims, not frequencies.
args <- commandArgs(trailingOnly=FALSE)
f <- sub('^--file=', '', args[grepl('^--file=',args)])
if(length(f)) setwd(dirname(normalizePath(f[1])))
suppressPackageStartupMessages({library(igraph);library(ggplot2);library(ggrepel)})
set.seed(1320)
N <- read.csv('data/nodes.csv',fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE,check.names=FALSE)
E <- read.csv('data/edges.csv',fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE,check.names=FALSE)
E$directed <- tolower(E$directed)=='true'
stopifnot(!anyDuplicated(N$id),!anyDuplicated(E$edge_id),all(E$source %in% N$id),all(E$target %in% N$id),all(E$source!=E$target),all(nzchar(E$printed_pages)))
dir.create('figures',showWarnings=FALSE);dir.create('analysis',showWarnings=FALSE)
family <- Sys.getenv('GELIS_FONT', 'Noto Sans CJK SC')
# Install a CJK font on machines without Noto; then set GELIS_FONT to that family.
status_cols <- c(living='#187D8D',dead='#AA584D',uncertain='#B09A70')
status_names <- c(living='生者',dead='死者',uncertain='生死未明／时点不定')
layer_cols <- c(kinship='#A3AAB2',communication='#1B7A89',social='#5A6C97',ritual='#A88532',apparition='#B55C54',care='#8E678F',afterlife='#BA6954',judicial='#434A52')
layer_names <- c(kinship='亲属',communication='谈话与传递',social='服务／交往／冲突',ritual='仪式委托',apparition='声称的显灵',care='死后关切／要求／敌意',afterlife='据称死者同行',judicial='司法程序')
line_names <- c(attested='记载已发生',unfulfilled='未履行／未证实／仅提议',inferred='研究者推定')
E$line <- ifelse(E$evidence_mode=='inferred','inferred',ifelse(E$outcome=='attested','attested','unfulfilled'))
# Directed graph storage retains a directed attribute for symmetric relations.
# For mixed graph consumers, use that attribute, not GraphML's global directedness.
g_all <- graph_from_data_frame(E[c('source','target',setdiff(names(E),c('source','target')))], directed=TRUE,vertices=data.frame(name=N$id,label=N$name,N[setdiff(names(N),c('id','name'))],check.names=FALSE))
stopifnot(identical(V(g_all)$name,N$id))
saveRDS(list(nodes=N,edges=E,graph=g_all), 'analysis/gelis_multiplex.rds')
write_graph(g_all,'analysis/gelis_multiplex.graphml',format='graphml')
# Conservative distinct-neighbour descriptive analysis of observed living communication.
live <- N$id[N$status=='living']
e_comm <- subset(E,layer=='communication' & outcome=='attested' & source %in% live & target %in% live)
g_comm <- simplify(graph_from_data_frame(e_comm[c('source','target')],directed=TRUE),remove.multiple=TRUE,remove.loops=TRUE)
gu <- as_undirected(g_comm,mode='collapse')
m <- data.frame(id=V(g_comm)$name,distinct_partners=degree(gu),out_partners=degree(g_comm,mode='out'),in_partners=degree(g_comm,mode='in'),betweenness=betweenness(gu,normalized=TRUE))
m$name <- N$name[match(m$id,N$id)];m <- m[order(-m$distinct_partners,m$name),]
write.csv(m,'analysis/observed_communication_metrics.csv',row.names=FALSE,fileEncoding='UTF-8')
# Layouts are display coordinates, not social or geographic distances.
layout_nodes <- function(ids,edges,seed=1320){
 n <- N[match(ids,N$id),]; set.seed(seed)
 g <- graph_from_data_frame(edges[c('source','target')],directed=FALSE,vertices=data.frame(name=ids))
 g <- simplify(g)
 xy <- if(length(ids)==1) matrix(c(0,0),1) else layout_with_fr(g,niter=2500,grid='nogrid')
 normalize <- function(x) if(diff(range(x))<1e-8) rep(0,length(x)) else (x-mean(range(x)))/diff(range(x))*2
 n$x<-normalize(xy[,1]);n$y<-normalize(xy[,2]);n
}
edge_xy <- function(edges,n){
 z<-edges; a<-match(z$source,n$id);b<-match(z$target,n$id)
 z$x<-n$x[a];z$y<-n$y[a];z$xend<-n$x[b];z$yend<-n$y[b]
 # Clip endpoints away from node centres so arrowheads remain visible.
 dx<-z$xend-z$x;dy<-z$yend-z$y;len<-sqrt(dx^2+dy^2);off<-pmin(.035,len*.12)
 z$x<-z$x+dx/len*off;z$y<-z$y+dy/len*off
 z$xend<-z$xend-dx/len*off;z$yend<-z$yend-dy/len*off
 z
}
make_plot <- function(n,e,title,subtitle,caption,full=FALSE,edge_labels=FALSE){
 z<-edge_xy(e,n);n$label<-paste0(n$name,'\n',n$role_zh)
 p<-ggplot()+
  geom_curve(data=z[!z$directed,],aes(x=x,y=y,xend=xend,yend=yend,colour=layer,linetype=line),curvature=.08,linewidth=if(full).32 else .6,alpha=.7)+
  geom_curve(data=z[z$directed,],aes(x=x,y=y,xend=xend,yend=yend,colour=layer,linetype=line),curvature=.12,linewidth=if(full).32 else .6,alpha=.7,arrow=grid::arrow(length=grid::unit(if(full)1.3 else 1.8,'mm'),type='closed'))+
  geom_point(data=n,aes(x=x,y=y,fill=status),shape=21,size=if(full)3 else 5,stroke=.7,colour='white')+
  geom_label_repel(data=n,aes(x=x,y=y,label=label),family=family,size=if(full)2.8 else 3.25,colour='#22313F',fill=scales::alpha('#FCFBF7',.94),label.size=0,box.padding=.55,point.padding=.4,segment.color='#AFB6BD',segment.size=.25,max.overlaps=Inf,max.iter=30000,max.time=12,seed=1320,min.segment.length=0)+
  scale_fill_manual(values=status_cols,labels=status_names,name=NULL,drop=FALSE)+
  scale_colour_manual(values=layer_cols,labels=layer_names,name=NULL)+
  scale_linetype_manual(values=c(attested='solid',unfulfilled='dashed',inferred='dotted'),labels=line_names,name=NULL)+
  guides(colour=guide_legend(order=2,override.aes=list(linewidth=1.1)),fill=guide_legend(order=1,override.aes=list(size=4)),linetype=guide_legend(order=3))+
  coord_equal(xlim=c(-1.5,1.5),ylim=c(-1.35,1.35),clip='off')+
  labs(title=title,subtitle=subtitle,caption=caption)+
  theme_void(base_family=family)+theme(plot.background=element_rect(fill='#FCFBF7',colour=NA),panel.background=element_rect(fill='#FCFBF7',colour=NA),plot.title=element_text(size=24,face='bold',colour='#20313E',margin=margin(b=10)),plot.subtitle=element_text(size=11.5,colour='#5D6973',lineheight=1.45,margin=margin(b=22)),plot.caption=element_text(size=9,colour='#5D6973',hjust=0,lineheight=1.4,margin=margin(t=20)),legend.position='bottom',legend.box='vertical',legend.text=element_text(size=9),plot.margin=margin(28,38,24,38))
 if(edge_labels && nrow(z)) p<-p+geom_label_repel(data=z,aes(x=(x+xend)/2,y=(y+yend)/2,label=relation_zh),size=2.5,family=family,fill='#FCFBF7',label.size=0,max.overlaps=Inf,seed=331)
 p
}
plots<-list()
# 1: circulation. Living and undetermined-status people; dead addressees are not mixed in.
e1<-subset(E,layer=='communication' & source %in% N$id[N$status!='dead'] & target %in% N$id[N$status!='dead'])
n1<-layout_nodes(unique(c(e1$source,e1$target)),e1)
# Deterministic curated coordinates for hubs and peripheral receivers.
pos<-data.frame(id=c('gelis','mengarde','raimonde_f','navarre','guillemette','jacqueline','gausia','sister_r','touzes','mengarde_c','jeanne_f','mother_f','nespla','brune_c','ermengarde','resplandie','mother_res','na_serres','monesple','brunissende','barc_d','son_a','raimond_a','cousin','brune_s','brune_e','thomas'),x=c(.25,-.55,-.4,.85,.8,-1.2,-1.05,-1.2,.05,-.8,-.55,-.95,-.9,-.3,1.23,1.3,1.2,1.2,.5,.75,.4,.12,.15,.7,.98,.02,.3),y=c(.1,.25,-.55,-.2,.75,.7,.2,-.25,-1.1,1.1,.95,-.95,-.05,.8,1.15,.65,.35,-.6,-.55,-.85,1.2,.85,.55,-1.2,-1.0,-.25,-1.15))
n1$x<-pos$x[match(n1$id,pos$id)];n1$y<-pos$y[match(n1$id,pos$id)];stopifnot(!anyNA(n1$x))
plots[['01_circulation']]<-make_plot(n1,e1,'01  消息怎样流动','有向传播网络 · 提问者、介绍人、陪访者与消息接收者\n箭头随每条行动的方向；查询与转述并非同一种信息流。虚线不表示已经接触成功。','史料：第8–13案，印刷页158–190。节点等大；位置仅供阅读。\n边的逐条动作、讲述者、履行状态及页码见 data/edges.csv。实际互动也只由审讯记录得知。')
# 2: kinship and cross-death relations; household panels retain only documented internal ties.
sets<-list('A  Gélis自己的家庭'=c('gelis','wife_g','son_g','mil_g','rousse','father_g','cousin','hugou'),'B  两位求助者的母女关系'=c('mengarde','plaisance','raimonde_f','fabrissa_f','guillaume_f'),'C  Navarre与Bru家庭'=c('navarre','pons_b','friar_b','marty','pierre_s'),'D  Battegay家庭'=c('guillemette','pierre_b','fabrissa_b','jr_arnaud','arnaud_b','jean_b'),'E  Durfort与Calmelles家庭'=c('hugues_d','brunissende','calmelles','barc_m','barc_d','loubens','philippa','camelle'),'F  Arignac家庭：保留身份未决'=c('guill_a','bernarde','raimond_a','son_a','girl_a1','girl_a2','girl_a3','gausia','arignac_h'))
ns<-list();zs<-list()
for(k in names(sets)){
 ids<-sets[[k]];ee<-subset(E,source %in% ids & target %in% ids & layer %in% c('kinship','care','social','ritual','communication'))
 nn<-layout_nodes(ids,ee,seed=1320+length(ns));nn$panel<-k;zz<-edge_xy(ee,nn);zz$panel<-k;ns[[k]]<-nn;zs[[k]]<-zz
}
n2<-do.call(rbind,ns);z2<-do.call(rbind,zs);n2$label<-paste0(n2$name,'\n',n2$role_zh)
p2<-ggplot()+geom_curve(data=z2[!z2$directed,],aes(x=x,y=y,xend=xend,yend=yend,colour=layer,linetype=line),curvature=.06,linewidth=.6)+geom_curve(data=z2[z2$directed,],aes(x=x,y=y,xend=xend,yend=yend,colour=layer,linetype=line),curvature=.14,linewidth=.6,arrow=grid::arrow(length=grid::unit(1.6,'mm'),type='closed'))+geom_point(data=n2,aes(x,y,fill=status),shape=21,size=4.5,colour='white')+geom_label_repel(data=n2,aes(x,y,label=label),family=family,size=2.8,label.size=0,fill='#FCFBF7',box.padding=.9,force=8,max.overlaps=Inf,seed=1320,max.time=12,max.iter=30000,min.segment.length=0,segment.color='#ADB3B7')+facet_wrap(~panel,ncol=2)+scale_fill_manual(values=status_cols,labels=status_names,name=NULL,drop=FALSE)+scale_colour_manual(values=layer_cols,labels=layer_names,name=NULL)+scale_linetype_manual(values=c(attested='solid',unfulfilled='dashed',inferred='dotted'),labels=line_names,name=NULL)+coord_equal(xlim=c(-1.65,1.65),ylim=c(-1.45,1.45),clip='off')+labs(title='02  死亡之后，家庭关系仍然存在',subtitle='六个局部网络 · 婚姻／同胞为无向边，亲子箭头由长辈指向子女\n其他箭头按行动方向。未决身份保留独立节点，不靠布局暗示同一人。',caption='F图：债据事件中的“儿子”与Raimond可能同一人，Gausia的丈夫也未强行识别。三个女孩的序号只供区分节点。\n孤立点表示在该图选取的关系中没有可确认的连边，不代表社会孤立；这些面板不是完整家谱。')+theme_void(base_family=family)+theme(plot.background=element_rect(fill='#FCFBF7',colour=NA),plot.title=element_text(size=24,face='bold',colour='#20313E',margin=margin(b=10)),plot.subtitle=element_text(size=11,colour='#5D6973',lineheight=1.4,margin=margin(b=18)),strip.text=element_text(size=12,face='bold',colour='#20313E',margin=margin(t=12,b=15)),panel.spacing=grid::unit(1.2,'cm'),legend.position='bottom',legend.box='vertical',legend.text=element_text(size=9),plot.caption=element_text(size=9,hjust=0,colour='#5D6973',lineheight=1.4,margin=margin(t=15)),plot.margin=margin(28,30,24,30))
plots[['02_households']]<-p2
# 3: old service relationships alongside apparition and judicial testimony.
ids3<-c('gelis','hugues_d','brunissende','monesple','saisset','vidal','catala','rous','athon','durand','germain','fournier','raimonde_f')
e3<-subset(E,source %in% ids3 & target %in% ids3 & layer %in% c('kinship','social','ritual','apparition','judicial'))
n3<-layout_nodes(ids3,e3,1340)
plots[['03_church']]<-make_plot(n3,e3,'03  服务、显灵与教会权威','同一对人物可以有多种关系 · Gélis与Hugues既有生前服务，又有声称的死后接触\n总铎Germain同时是谈话中的批评对象和司法程序的在场者；这不证明报复。','史料：印刷页158–160、168、178–179、185–187。箭头按动作；服务由服务者指向受服务者。\n红色显灵边是史料中的声称，不是研究者对超自然事件的事实认定。')
# 4: reported associations of deceased, no universal clique from general statements.
e4<-subset(E,layer=='afterlife');n4<-N[match(unique(c(e4$source,e4$target)),N$id),]
n4$x<-0;n4$y<-0
rows<-list(c('plaisance','daughter_m'),c('fabrissa_f','gentille_c','mabille'),c('fabrissa_b','daughter_n'),c('nicolas','baquet'),c('barc_f','ava'))
for(i in seq_along(rows)) {ii<-match(rows[[i]],n4$id);n4$x[ii]<-if(length(ii)==2)c(-.75,.75) else c(0,-.9,.9);n4$y[ii]<-1.1-(i-1)*.53;if(length(ii)==3)n4$y[ii]<-n4$y[ii]+c(.1,-.1,-.1)}
plots[['04_deceased_companions']]<-make_plot(n4,e4,'04  死者与谁结伴？','仅绘制供词明确点名的同行者 · 不把“熟人相互扶助”的一般说法扩展为人人相连\n这五组为证词中的结伴关系；没有连线不表示死者互不相识。','来源：Mengarde p.173；Raimonde pp.178–179；Guillemette p.189。\n同一小组中的两位被共同提及者，若无直接关系陈述，不自动补边。')
# 5: complete exploratory atlas, includes peripheral and disconnected people.
n5<-layout_nodes(N$id,E,1320)
plots[['05_full_atlas']]<-make_plot(n5,E,paste0('05  Gélis人物关系总览：',nrow(N),'人'),paste0(nrow(E),'条关系陈述 · 多重关系并存 · 仅作为索引图，不据此推断整个地方社会的中心性\n等大节点；颜色是叙述时点的生死状态；标签为姓名与身份。司法关系与显灵关系均为独立层。'),'边数是人工编码的关系陈述数，不是会面次数或独立证人数。无边节点为已提及但未在选取关系中连接的人物。\n布局不具有地理或时间含义；全量证据见CSV和README。',full=TRUE)
# Save with cairo for UTF-8 text and searchable PDF; SVG is vector and uses local fonts.
for(nm in names(plots)){
 wh<-if(nm=='02_households')c(17,22) else if(nm=='05_full_atlas')c(32,26) else c(18,15)
 ggsave(paste0('figures/',nm,'.png'),plots[[nm]],width=wh[1],height=wh[2],dpi=150,type='cairo',device='png',bg='#FCFBF7',limitsize=FALSE)
 cairo_pdf(paste0('figures/',nm,'.pdf'),width=wh[1],height=wh[2],family=family);print(plots[[nm]]);dev.off()
 svg(paste0('figures/',nm,'.svg'),width=wh[1],height=wh[2],family=family,bg='#FCFBF7');print(plots[[nm]]);dev.off()
}
# One convenient multipage atlas; individual figures above have larger native sizes.
cairo_pdf('Gelis_Network_Atlas.pdf',width=22,height=26,family=family,onefile=TRUE)
for(p in plots)print(p)
dev.off()
write.csv(n5[c('id','x','y')],'analysis/full_layout.csv',row.names=FALSE)
write.csv(n1[c('id','x','y')],'analysis/circulation_layout.csv',row.names=FALSE)
capture.output(sessionInfo(),file='analysis/sessionInfo.txt')
cat('Rendered',length(plots),'views from',nrow(N),'nodes and',nrow(E),'edge assertions.\n')
