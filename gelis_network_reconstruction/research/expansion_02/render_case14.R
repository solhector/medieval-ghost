#!/usr/bin/env Rscript
args <- commandArgs(FALSE); f <- sub('^--file=', '', args[grepl('^--file=', args)])
if(length(f)) setwd(dirname(normalizePath(f[1])))
library(ggplot2)
font <- Sys.getenv('GELIS_FONT','Noto Sans CJK SC')
e <- read.csv('assertions.csv',fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE)
n <- read.csv('new_nodes.csv',fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE)
pos <- data.frame(id=c('carot','caussou_miller','gaillarde_child','rouch','lagleize','carot_h','canals'),x=c(-2,-2,0,2,2,-3.5,0),y=c(0,2,1,2,0,-1.4,-1.4))
pos$label <- c('Jacqueline den Carot\nAx居民／寡妇','Guillaume Caussou\nAx磨工','Gaillarde\n约12岁／乞食、寄住','Pierre Rouch\nMérens教区长','Barthélémy de Lagleize\nSorgeat神父／Ax代牧','Raimond Carot\nJacqueline亡夫','Pierre de Canals\nGaillarde父亲')
pos$status <- n$status[match(pos$id,n$id)]
# Selected views preserve source edge IDs; choose one account of repeated speech.
s <- subset(e,case_id=='C014' & source %in% pos$id & target %in% pos$id)
s <- s[!duplicated(paste(s$source,s$target,s$layer)),]
# The corrective replies and co-hearing are in data; omit from this single-purpose view.
s <- s[s$layer != 'care' & !s$relation_zh %in% c('回答教会持相反教义','在磨坊亲耳听见谈话'),]
# Witness links drawn separately to display the girl's firsthand hearing.
s <- rbind(s,subset(e,case_id=='C014' & relation_zh=='在磨坊亲耳听见谈话'))
s$label <- ifelse(s$relation_zh=='在磨坊亲耳听见谈话','亲耳听见',ifelse(grepl('转述',s$relation_zh),'转述／求证',ifelse(grepl('磨坊讨论',s$relation_zh),'讨论死后相认',ifelse(grepl('炉边',s$relation_zh),'炉边讨论',s$relation_zh))))
a <- match(s$source,pos$id);b <- match(s$target,pos$id)
s$x<-pos$x[a];s$y<-pos$y[a];s$xend<-pos$x[b];s$yend<-pos$y[b]
dx<-s$xend-s$x;dy<-s$yend-s$y;d<-sqrt(dx^2+dy^2)
s$x<-s$x+dx/d*.22;s$y<-s$y+dy/d*.22;s$xend<-s$xend-dx/d*.22;s$yend<-s$yend-dy/d*.22
p <- ggplot()+geom_segment(data=s,aes(x=x,y=y,xend=xend,yend=yend,colour=layer),linewidth=.8,alpha=.75)+
 geom_label(data=s,aes(x=(x+xend)/2,y=(y+yend)/2,label=label),family=font,size=3.5,label.size=0,fill='#FCFBF7')+
 geom_point(data=pos,aes(x=x,y=y,fill=status),shape=21,size=6,colour='white')+
 geom_label(data=pos,aes(x=x,y=y+.27,label=label),family=font,size=4,lineheight=1.25,label.size=0,fill='#FCFBF7',colour='#22313F')+
 scale_colour_manual(values=c(kinship='#B5A48A',communication='#167E88',care='#946F9A',social='#6B7FA2'),guide='none')+
 scale_fill_manual(values=c(living='#167E88',dead='#B76150',uncertain='#B5A48A'),guide='none')+
 coord_equal(xlim=c(-4.8,3.4),ylim=c(-2.25,3),clip='off')+
 labs(title='磨坊、炉边与告发',subtitle='第十四案 · Jacqueline den Carot · 1320年证词中的选定关系',caption='蓝绿＝生者；赭红＝死者；米灰＝生死未明。连线表示选定关系，传播方向见CSV。\n墓地声响与Valentin Barra遇害构成谈话背景，不能据此画出已证实的鬼魂行动边。\n来源：Duvernoy法译本，第191–196页；PDF第231–236页。全文及异词见证据表。')+
 theme_void(base_family=font)+theme(plot.background=element_rect(fill='#FCFBF7',colour=NA),plot.title=element_text(size=25,face='bold',colour='#22313F'),plot.subtitle=element_text(size=13,colour='#60717B',margin=margin(t=10)),plot.caption=element_text(size=10,hjust=0,lineheight=1.5,colour='#60717B'),plot.margin=margin(25,25,25,25))
ggsave('case14_circulation.png',p,width=14,height=9,dpi=160,bg='#FCFBF7')
ggsave('case14_circulation.pdf',p,width=14,height=9,device=cairo_pdf,bg='#FCFBF7')
write.csv(s,'case14_plotted_edges.csv',row.names=FALSE,fileEncoding='UTF-8')
