#!/usr/bin/env Rscript
args <- commandArgs(FALSE); f <- sub('^--file=', '', args[grepl('^--file=', args)])
if(length(f)) setwd(dirname(normalizePath(f[1])))
suppressPackageStartupMessages(library(igraph))
read <- function(p) read.csv(p,fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE,check.names=FALSE)
bind <- function(xs) {
 cols <- unique(unlist(lapply(xs,names)))
 do.call(rbind,lapply(xs,function(x){for(k in setdiff(cols,names(x))) x[[k]] <- rep('',nrow(x));x[cols]}))
}
n <- read('data/nodes.csv');n$dataset <- 'core_v1'
e <- read('data/edges.csv');e$dataset <- 'core_v1';e$provenance_level <- 'legacy_page_level'
ns <- list(n); es <- list(e); vs <- list(); us <- list()
paths <- sort(list.dirs('research',recursive=FALSE,full.names=TRUE))
paths <- paths[grepl('/expansion_[0-9]+$',paths)]
for(p in paths) {
 nn <- read(file.path(p,'new_nodes.csv'));ee <- read(file.path(p,'assertions.csv'));vv <- read(file.path(p,'evidence.csv'))
 stopifnot(!anyDuplicated(vv$evidence_id),all(ee$evidence_id %in% vv$evidence_id))
 nn$dataset <- basename(p);ee$dataset <- basename(p);ee$provenance_level <- 'excerpt_and_pdf_page'
 ns[[length(ns)+1]] <- nn;es[[length(es)+1]] <- ee;vs[[length(vs)+1]] <- vv
 up <- file.path(p,'node_updates.csv');if(file.exists(up)) us[[length(us)+1]] <- read(up)
}
n <- bind(ns);e <- bind(es);v <- bind(vs)
stopifnot(!anyDuplicated(n$id),!anyDuplicated(e$edge_id),!anyDuplicated(v$evidence_id),all(e$source %in% n$id),all(e$target %in% n$id))
if(length(us)) for(u in us) for(j in seq_len(nrow(u))) {
 stopifnot(u$id[j] %in% n$id,u$field[j] %in% names(n),u$evidence_id[j] %in% v$evidence_id)
 n[n$id==u$id[j],u$field[j]] <- u$new_value[j]
}
e$directed <- tolower(as.character(e$directed)) == 'true'
e$evidence_pdf_page <- v$pdf_page[match(e$evidence_id,v$evidence_id)]
out <- 'analysis/expanded';dir.create(out,recursive=TRUE,showWarnings=FALSE)
write.csv(n,file.path(out,'nodes.csv'),row.names=FALSE,fileEncoding='UTF-8')
write.csv(e,file.path(out,'edges.csv'),row.names=FALSE,fileEncoding='UTF-8')
write.csv(v,file.path(out,'evidence.csv'),row.names=FALSE,fileEncoding='UTF-8')
g <- graph_from_data_frame(e[c('source','target',setdiff(names(e),c('source','target')))],directed=TRUE,vertices=data.frame(name=n$id,label=n$name,n[setdiff(names(n),c('id','name'))],check.names=FALSE))
stopifnot(identical(V(g)$name,n$id),ecount(g)==nrow(e))
saveRDS(list(nodes=n,edges=e,graph=g,evidence=v,node_updates=us),file.path(out,'expanded_network.rds'))
write_graph(g,file.path(out,'expanded_network.graphml'),format='graphml')
writeLines(c(sprintf('PASS: %d nodes; %d relation assertions; %d excerpt records',nrow(n),nrow(e),nrow(v)),paste('Batches:',paste(basename(paths),collapse=', ')),'PASS: unique keys, complete edge endpoints, evidence foreign keys, exported graph IDs and sourced node updates.','One assertion is not necessarily one independent event: repeated testimonies can support the same event.','Excluded/retracted allegations as facts and candidate identity matches are NOT graph edges.','Attributed speech, disputed accounts, hearsay and beliefs ARE explicitly marked: filter evidence_mode before analysis.','GraphML is a directed storage container: honor edge attribute directed=false for symmetric ties.','Full reading does not certify exhaustive person/edge extraction or accuracy of testimony.','Earlier five figures remain core_v1 snapshots; expansion_02 figure is a selected C014 view.'),file.path(out,'validation.txt'))
cat(readLines(file.path(out,'validation.txt')),sep='\n')
