#!/usr/bin/env Rscript
args <- commandArgs(FALSE); f <- sub('^--file=', '', args[grepl('^--file=', args)])
if(length(f)) setwd(dirname(normalizePath(f[1])))
suppressPackageStartupMessages(library(igraph))
read <- function(p) read.csv(p,fileEncoding='UTF-8-BOM',stringsAsFactors=FALSE,check.names=FALSE)
base_n <- read('data/nodes.csv'); base_e <- read('data/edges.csv')
prefix <- 'research/expansion_01/'
new_n <- read(paste0(prefix,'new_nodes.csv')); new_e <- read(paste0(prefix,'assertions.csv'))
v <- read(paste0(prefix,'evidence.csv'))
stopifnot(!anyDuplicated(v$evidence_id),all(new_e$evidence_id %in% v$evidence_id))
base_n$dataset <- 'core_v1'; new_n$dataset <- 'expansion_01'
n <- rbind(base_n,new_n)
base_e$dataset <- 'core_v1'; new_e$dataset <- 'expansion_01'
base_e$provenance_level <- 'legacy_page_level';new_e$provenance_level <- 'excerpt_and_pdf_page'
cols <- union(names(base_e),names(new_e))
for(col in setdiff(cols,names(base_e))) base_e[[col]] <- ''
for(col in setdiff(cols,names(new_e))) new_e[[col]] <- ''
e <- rbind(base_e[cols],new_e[cols])
stopifnot(!anyDuplicated(n$id),!anyDuplicated(e$edge_id),all(e$source %in% n$id),all(e$target %in% n$id),all(nzchar(new_e$printed_pages)))
e$directed <- tolower(as.character(e$directed)) == 'true'
e$evidence_pdf_page <- v$pdf_page[match(e$evidence_id,v$evidence_id)]
out <- 'analysis/expanded';dir.create(out,recursive=TRUE,showWarnings=FALSE)
write.csv(n,file.path(out,'nodes.csv'),row.names=FALSE,fileEncoding='UTF-8')
write.csv(e,file.path(out,'edges.csv'),row.names=FALSE,fileEncoding='UTF-8')
g <- graph_from_data_frame(e[c('source','target',setdiff(names(e),c('source','target')))],directed=TRUE,vertices=data.frame(name=n$id,label=n$name,n[setdiff(names(n),c('id','name'))],check.names=FALSE))
stopifnot(identical(V(g)$name,n$id),ecount(g)==nrow(e))
saveRDS(list(nodes=n,edges=e,graph=g,evidence=v),file.path(out,'expanded_network.rds'))
write_graph(g,file.path(out,'expanded_network.graphml'),format='graphml')
writeLines(c(sprintf('PASS: %d nodes; %d relation assertions',nrow(n),nrow(e)),sprintf('New: %d nodes; %d assertions; %d excerpt records',nrow(new_n),nrow(new_e),nrow(v)),'PASS: unique keys, complete edge endpoints, evidence foreign keys, exported graph IDs.','Excluded/retracted claims and candidate identity matches are NOT graph edges.','Earlier five figures are core_v1 snapshots, NOT updated full-corpus visualizations.'),file.path(out,'validation.txt'))
cat(readLines(file.path(out,'validation.txt')),sep='\n')
