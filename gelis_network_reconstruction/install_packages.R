packages <- c('igraph','ggplot2','ggrepel')
missing <- packages[!vapply(packages, requireNamespace, quietly=TRUE, FUN.VALUE=logical(1))]
if(length(missing)) install.packages(missing,repos='https://cloud.r-project.org')
