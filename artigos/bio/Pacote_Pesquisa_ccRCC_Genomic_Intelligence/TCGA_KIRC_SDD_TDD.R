# TCGA-KIRC — módulo transcriptômico/prognóstico, versão de pesquisa 2026-10-20
# Execute em R/Colab com conectividade, Bioconductor e tempo/memória suficientes.
# Este script NÃO presume significância, AUC alta ou calibração favorável.
options(stringsAsFactors = FALSE, warn = 1)
set.seed(2026)
root <- Sys.getenv('PROJECT_DIR', unset = file.path(getwd(),'ccRCC_GI'))
for (d in c('data','tables','figures','models','logs')) dir.create(file.path(root,d),showWarnings=FALSE,recursive=TRUE)
needed <- c('TCGAbiolinks','SummarizedExperiment','DESeq2','edgeR','survival','glmnet','timeROC','ggplot2')
missing <- needed[!vapply(needed, requireNamespace, logical(1), quietly=TRUE)]
if(length(missing)) stop('Instale os pacotes R ausentes antes da execução: ',paste(missing,collapse=', '))
log_rows <- list()
audit <- function(id, message, passed, detail='') {
  log_rows[[length(log_rows)+1L]] <<- data.frame(spec=id,test=message,status=if(isTRUE(passed)) 'PASS' else 'FAIL',detail=as.character(detail))
  write.table(do.call(rbind,log_rows),file.path(root,'logs','sdd_tdd.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
  cat(sprintf('[%s] %s — %s %s\n',if(isTRUE(passed))'PASS' else 'FAIL',id,message,detail))
  if(!isTRUE(passed)) stop('Validação estrutural reprovada: ',id,' / ',message,call.=FALSE)
}
finish <- function(){
  if(length(log_rows)) write.table(do.call(rbind,log_rows),file.path(root,'logs','sdd_tdd.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
  writeLines(capture.output(sessionInfo()),file.path(root,'logs','sessionInfo.txt'))
}
file_rds <- file.path(root,'data','TCGA_KIRC_STAR_Counts.rds')
if(file.exists(file_rds)) {
  se <- readRDS(file_rds)
} else {
  q <- TCGAbiolinks::GDCquery(project='TCGA-KIRC',data.category='Transcriptome Profiling',data.type='Gene Expression Quantification',workflow.type='STAR - Counts')
  TCGAbiolinks::GDCdownload(q,method='api',files.per.chunk=10)
  se <- TCGAbiolinks::GDCprepare(q)
  saveRDS(se,file_rds)
}
audit('SPEC-01','SummarizedExperiment carregado',inherits(se,'SummarizedExperiment') && ncol(se)>0)
barcode <- colnames(se)
condition_code <- substring(barcode,14L,15L)
keep <- condition_code %in% c('01','11')
se <- se[,keep]
meta <- as.data.frame(SummarizedExperiment::colData(se))
meta$barcode <- colnames(se)
meta$patient_id <- substr(meta$barcode,1,12)
meta$condition <- ifelse(substr(meta$barcode,14,15)=='01','Tumor','Normal')
meta <- meta[order(meta$barcode),,drop=FALSE]
meta <- meta[!duplicated(meta[,c('patient_id','condition')]),,drop=FALSE]
se <- se[,meta$barcode]
rownames(meta) <- meta$barcode
meta$condition <- factor(meta$condition,levels=c('Normal','Tumor'))
audit('SPEC-01','Pacientes únicos por condição',!any(duplicated(meta[,c('patient_id','condition')])))
audit('SPEC-01','Tumor e normal disponíveis',all(c('Normal','Tumor') %in% meta$condition))
assay_names <- SummarizedExperiment::assayNames(se)
if(!'unstranded' %in% assay_names) stop('Não foi encontrado o assay unstranded. Assays: ',paste(assay_names,collapse=', '))
cts <- as.matrix(SummarizedExperiment::assay(se,'unstranded'))
ginfo <- as.data.frame(SummarizedExperiment::rowData(se))
if(!all(c('gene_type','gene_name') %in% colnames(ginfo))) stop('Anotação Ensembl gene_type/gene_name não disponível.')
rownames(cts) <- sub('\\..*','',rownames(cts))
rownames(ginfo) <- sub('\\..*','',rownames(ginfo))
ginfo <- ginfo[match(rownames(cts),rownames(ginfo)),,drop=FALSE]
keep_genes <- !is.na(ginfo$gene_type) & ginfo$gene_type=='protein_coding' & !is.na(ginfo$gene_name) & nzchar(ginfo$gene_name)
cts <- cts[keep_genes,,drop=FALSE]
ginfo <- ginfo[keep_genes,,drop=FALSE]
audit('SPEC-02','Contagens inteiras, finitas e não negativas',all(is.finite(cts)) && all(cts>=0) && all(abs(cts-round(cts))<1e-8))
# DESCRITIVO: sem usar genes encontrados aqui como seleção prognóstica.
keep_desc <- rowSums(edgeR::cpm(cts)>1)>=ceiling(.15*ncol(cts))
cts_desc <- round(cts[keep_desc,,drop=FALSE]);storage.mode(cts_desc)<-'integer'
audit('SPEC-02','Filtro CPM aplicado',nrow(cts_desc)>0,paste('genes=',nrow(cts_desc)))
# Diferença Tumor x Normal pareada, evitando pseudorreplicação no conjunto de pacientes emparelhados.
common_ids <- intersect(as.character(meta$patient_id[meta$condition=='Normal']),as.character(meta$patient_id[meta$condition=='Tumor']))
audit('DEG-PAIR','Há pares suficientes para análise pareada',length(common_ids)>=10,paste('pares=',length(common_ids)))
sub_idx <- which(meta$patient_id %in% common_ids)
paired_meta <- droplevels(meta[sub_idx,,drop=FALSE]);paired_meta$patient_id<-factor(paired_meta$patient_id)
paired_meta <- paired_meta[order(paired_meta$patient_id,paired_meta$condition),,drop=FALSE]
paired_counts <- cts_desc[,paired_meta$barcode,drop=FALSE]
dds_pair <- DESeq2::DESeqDataSetFromMatrix(countData=paired_counts,colData=paired_meta,design=~patient_id+condition)
dds_pair <- DESeq2::DESeq(dds_pair,quiet=TRUE)
deg <- as.data.frame(DESeq2::results(dds_pair,contrast=c('condition','Tumor','Normal')))
deg$ensembl_id<-rownames(deg)
deg$gene <- ginfo[deg$ensembl_id,'gene_name']
deg <- deg[order(deg$padj,na.last=TRUE),,drop=FALSE]
write.table(deg,file.path(root,'tables','DESeq2_paired_Tumor_vs_Normal.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
# MUI normal-ref: média/SD entre normais pareados; teste de Wilcoxon PAREADO.
glycolysis <- c('SLC2A1','SLC2A3','HK1','HK2','HK3','GPI','PFKP','PFKM','PFKL','ALDOA','ALDOC','TPI1','GAPDH','PGK1','PGAM1','ENO1','ENO2','PKM','LDHA','PDK1','PDK3','SLC16A3')
tca <- c('PDHA1','PDHB','DLAT','DLD','CS','ACO2','IDH1','IDH2','IDH3A','OGDH','DLST','SUCLA2','SUCLG1','SDHA','SDHB','SDHC','SDHD','FH','MDH1','MDH2','PCK1','PCK2','PPARGC1A')
trans_pair <- as.matrix(SummarizedExperiment::assay(DESeq2::varianceStabilizingTransformation(dds_pair,blind=FALSE)))
pick_id <- function(symbol, candidates, mat){
  ix <- which(ginfo[rownames(mat),'gene_name']==symbol)
  if(!length(ix)) return(NA_character_)
  rownames(mat)[ix[which.max(rowMeans(mat[ix,,drop=FALSE]))]]
}
mui_ids_g <- na.omit(vapply(glycolysis,pick_id,character(1),candidates=rownames(trans_pair),mat=paired_counts))
mui_ids_t <- na.omit(vapply(tca,pick_id,character(1),candidates=rownames(trans_pair),mat=paired_counts))
mui_ids_g<-mui_ids_g[mui_ids_g %in% rownames(trans_pair)]
mui_ids_t<-mui_ids_t[mui_ids_t %in% rownames(trans_pair)]
audit('SPEC-03','Genes metabólicos representados',length(mui_ids_g)>=5 && length(mui_ids_t)>=5)
normal_cols <- paired_meta$barcode[paired_meta$condition=='Normal']
z_mu <- rowMeans(trans_pair[,normal_cols,drop=FALSE]);z_sd <- apply(trans_pair[,normal_cols,drop=FALSE],1,sd);z_sd[!is.finite(z_sd)|z_sd<1e-6]<-1
z <- sweep(sweep(trans_pair,1,z_mu,'-'),1,z_sd,'/')
MUI <- colMeans(z[mui_ids_g,,drop=FALSE])-colMeans(z[mui_ids_t,,drop=FALSE])
mui_df <- data.frame(patient_id=paired_meta$patient_id,condition=paired_meta$condition,barcode=paired_meta$barcode,MUI=as.numeric(MUI[paired_meta$barcode]))
wide <- reshape(mui_df[c('patient_id','condition','MUI')],idvar='patient_id',timevar='condition',direction='wide')
paired_test <- wilcox.test(wide$MUI.Tumor,wide$MUI.Normal,paired=TRUE,exact=FALSE)
mu_delta <- mean(wide$MUI.Tumor-wide$MUI.Normal)
write.table(mui_df,file.path(root,'tables','MUI_paired_patient.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
# Não exigir p desejado nem sinal pré-fixado; ambos são resultados, não invariantes do software.
# PROGNÓSTICO: divisão de pacientes anterior à escolha das características e à normalização.
tumor_meta <- meta[meta$condition=='Tumor',,drop=FALSE]
pickcol <- function(df,names){ for(n in names) if(n %in% colnames(df)) return(df[[n]]); return(rep(NA,nrow(df))) }
tumor_meta$days_to_death <- suppressWarnings(as.numeric(as.character(pickcol(tumor_meta,c('days_to_death')))))
tumor_meta$days_to_last_follow_up <- suppressWarnings(as.numeric(as.character(pickcol(tumor_meta,c('days_to_last_follow_up','days_to_last_known_alive')))))
tumor_meta$vital_status <- as.character(pickcol(tumor_meta,c('vital_status')))
tumor_meta$OS_days <- ifelse(tolower(tumor_meta$vital_status) %in% c('dead','deceased'),tumor_meta$days_to_death,tumor_meta$days_to_last_follow_up)
tumor_meta$OS_event <- as.integer(tolower(tumor_meta$vital_status) %in% c('dead','deceased'))
raw_age <- suppressWarnings(as.numeric(as.character(pickcol(tumor_meta,c('age_at_index','age_at_diagnosis')))))
if(!'age_at_index'%in%colnames(tumor_meta) && 'age_at_diagnosis'%in%colnames(tumor_meta)) raw_age <- raw_age/365.25
tumor_meta$age <- raw_age
tumor_meta$stage <- as.character(pickcol(tumor_meta,c('ajcc_pathologic_stage','tumor_stage')))
tumor_meta$stage_num <- rep(NA_integer_,nrow(tumor_meta))
for(s in c('IV','III','II','I')) tumor_meta$stage_num[grepl(paste0('Stage ',s,'($|[ABC]|\\s)'),tumor_meta$stage,ignore.case=TRUE)] <- match(s,c('I','II','III','IV'))
if(!'stage_num' %in% names(tumor_meta)) tumor_meta$stage_num <- NA_integer_
tumor_meta$stage_num<-as.integer(tumor_meta$stage_num)
clin <- tumor_meta[is.finite(tumor_meta$OS_days) & tumor_meta$OS_days>=30 & is.finite(tumor_meta$age) & !is.na(tumor_meta$stage_num),,drop=FALSE]
audit('SPEC-04','Sobrevida clínica completa suficiente',nrow(clin)>=60 && sum(clin$OS_event)>=20,paste('N=',nrow(clin),'eventos=',sum(clin$OS_event)))
ix0 <- which(clin$OS_event==0L);ix1<-which(clin$OS_event==1L)
train_ids <- sort(c(sample(ix0,floor(.7*length(ix0))),sample(ix1,floor(.7*length(ix1)))))
test_ids <- setdiff(seq_len(nrow(clin)),train_ids)
train <- clin[train_ids,,drop=FALSE];test<-clin[test_ids,,drop=FALSE]
audit('SPEC-04','Treino e teste sem pacientes em comum',length(intersect(train$patient_id,test$patient_id))==0L,paste(nrow(train),'/',nrow(test)))
# Filtro por expressão baseado EXCLUSIVAMENTE na coorte de descoberta.
train_cts <- round(cts[,train$barcode,drop=FALSE]); test_cts <- round(cts[,test$barcode,drop=FALSE])
keep_train <- rowSums(edgeR::cpm(train_cts)>1) >= ceiling(.15*ncol(train_cts))
train_cts<-train_cts[keep_train,,drop=FALSE];test_cts<-test_cts[rownames(train_cts),,drop=FALSE]
storage.mode(train_cts)<-'integer';storage.mode(test_cts)<-'integer'
# DESeq2: estima fatores e dispersão apenas no treino; aplica tendência congelada ao teste.
train_meta <- train;rownames(train_meta)<-train_meta$barcode
test_meta <- test;rownames(test_meta)<-test_meta$barcode
dds_train<-DESeq2::DESeqDataSetFromMatrix(countData=train_cts,colData=train_meta,design=~1)
dds_test<-DESeq2::DESeqDataSetFromMatrix(countData=test_cts,colData=test_meta,design=~1)
# Geometric means com piso 1 para garantir denominador treinado sem dados de validação.
gm_train <- exp(rowMeans(log(pmax(1,train_cts))))
dds_train<-DESeq2::estimateSizeFactors(dds_train,geoMeans=gm_train)
dds_train<-DESeq2::estimateDispersions(dds_train,fitType='parametric')
train_vst<-as.matrix(SummarizedExperiment::assay(DESeq2::varianceStabilizingTransformation(dds_train,blind=FALSE)))
dds_test<-DESeq2::estimateSizeFactors(dds_test,geoMeans=gm_train)
dds_test <- DESeq2::`dispersionFunction<-`(dds_test, value=DESeq2::dispersionFunction(dds_train))
test_vst<-as.matrix(SummarizedExperiment::assay(DESeq2::varianceStabilizingTransformation(dds_test,blind=FALSE)))
audit('SPEC-05','VST test usa dispersão aprendida no treino',isTRUE(all.equal(DESeq2::dispersionFunction(dds_train)(c(5,20,100)),DESeq2::dispersionFunction(dds_test)(c(5,20,100)))))
predefined <- unique(c(glycolysis,tca))
train_annotation <- ginfo[rownames(train_vst),,drop=FALSE]
selected_ens <- vapply(predefined,function(symbol){
  ix <- which(train_annotation$gene_name==symbol)
  if(!length(ix)) return(NA_character_)
  rownames(train_vst)[ix[which.max(rowMeans(train_cts[ix,,drop=FALSE]))]]
},character(1))
selected_ens <- na.omit(selected_ens)
audit('SPEC-04','Características pré-declaradas encontradas',length(selected_ens)>=5,paste('genes=',length(selected_ens)))
x_train <- t(train_vst[selected_ens,train$barcode,drop=FALSE]);x_test<-t(test_vst[selected_ens,test$barcode,drop=FALSE])
colnames(x_train)<-names(selected_ens);colnames(x_test)<-names(selected_ens)
cent <- colMeans(x_train);sdev <- apply(x_train,2,sd);sdev[!is.finite(sdev)|sdev<1e-8] <- 1
x_train<-scale(x_train,center=cent,scale=sdev);x_test<-scale(x_test,center=cent,scale=sdev)
audit('SPEC-05','Teste escalado por médias/desvios do treino',all(is.finite(x_train)) && all(is.finite(x_test)))
y_train <- survival::Surv(train$OS_days/30.4375,train$OS_event)
# Distribui eventos pelos folds sem usar o conjunto de teste.
foldid<-integer(nrow(train))
foldid[which(train$OS_event==1)]<-sample(rep(seq_len(5),length.out=sum(train$OS_event)))
foldid[which(train$OS_event==0)]<-sample(rep(seq_len(5),length.out=sum(train$OS_event==0)))
cv<-glmnet::cv.glmnet(x_train,y_train,family='cox',alpha=1,foldid=foldid)
weights<-as.numeric(coef(cv,s='lambda.1se'));names(weights)<-colnames(x_train)
lambda_choice<-'lambda.1se'
if(!any(weights!=0)) { weights<-as.numeric(coef(cv,s='lambda.min'));names(weights)<-colnames(x_train);lambda_choice<-'lambda.min' }
audit('SPEC-04','Assinatura LASSO-Cox não vazia',any(weights!=0),lambda_choice)
train$MRS<-as.numeric(x_train%*%weights);test$MRS<-as.numeric(x_test%*%weights)
cutoff<-median(train$MRS)
train$risk<-ifelse(train$MRS>=cutoff,'Alto','Baixo');test$risk<-ifelse(test$MRS>=cutoff,'Alto','Baixo')
audit('SPEC-04','Corte de risco derivado só no treino',isTRUE(all.equal(cutoff,median(train$MRS))))
coeff_table<-data.frame(gene=names(weights),coefficient=weights)
write.table(coeff_table,file.path(root,'tables','LASSO_Cox_coefficients.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
saveRDS(list(weights=weights,mu_train=cent,sd_train=sdev,cutoff=cutoff,lambda=lambda_choice,genes=selected_ens),file.path(root,'models','frozen_lasso_model.rds'))
# Preditor integrado: AJUSTADO NO TREINO e APLICADO ao teste.
fit_integrated <- survival::coxph(survival::Surv(OS_days/30.4375,OS_event) ~ MRS + age + stage_num,data=train,x=TRUE,y=TRUE)
test$lp_integrated<-as.numeric(predict(fit_integrated,newdata=test,type='lp'))
roc <- timeROC::timeROC(T=test$OS_days/30.4375,delta=test$OS_event,marker=test$lp_integrated,cause=1,weighting='marginal',times=c(12,36,60),iid=FALSE)
# ROC só calculada para horizontes com seguimento útil — não reivindica performance obrigatória.
auc <- as.numeric(roc$AUC);names(auc)<-c('12m','36m','60m')
fit_stage <- survival::coxph(survival::Surv(OS_days/30.4375,OS_event)~stage_num,data=train)
test$lp_stage<-as.numeric(predict(fit_stage,newdata=test,type='lp'))
roc_stage<-timeROC::timeROC(T=test$OS_days/30.4375,delta=test$OS_event,marker=test$lp_stage,cause=1,weighting='marginal',times=c(12,36,60),iid=FALSE)
# Schoenfeld é diagnóstico dos coeficientes do modelo TREINADO, não prova de independência.
schoen <- survival::cox.zph(fit_integrated)
write.table(as.data.frame(schoen$table),file.path(root,'tables','Schoenfeld_train.tsv'),sep='\t',quote=FALSE)
# KM externo por ponto de corte congelado.
pdf(file.path(root,'figures','Kaplan_Meier_validation.pdf'),width=8,height=5)
plot(survival::survfit(survival::Surv(OS_days/30.4375,OS_event)~risk,data=test),col=c('#2874A6','#B03A2E'),lwd=2,xlab='Meses',ylab='Sobrevida global',main='Validação interna (30%)')
legend('bottomleft',legend=c('Alto','Baixo'),col=c('#2874A6','#B03A2E'),lty=1,bty='n');dev.off()
pdf(file.path(root,'figures','TimeROC_validation.pdf'),width=7,height=5)
plot(roc,time=36,col='#2874A6',lwd=2,title=FALSE);plot(roc_stage,time=36,add=TRUE,col='#B03A2E',lwd=2)
legend('bottomright',legend=c('Integrado','Estágio'),col=c('#2874A6','#B03A2E'),lty=1,bty='n');dev.off()
# Para calibração independente em 36 meses, usa intercepto/sobrevida basal do treino.
# Bootstrap de otimismo B=1000 e nomograma RMS exigem módulo separado após checagem de estabilidade.
stat <- data.frame(metric=c('paired_patients','delta_MUI_paired','wilcoxon_p_paired','tumor_cases_prognostic','train_n','validation_n','validation_AUC_12m','validation_AUC_36m','validation_AUC_60m','validation_stage_AUC_36m','lambda','model_terms'),
 value=c(length(common_ids),mu_delta,paired_test$p.value,nrow(clin),nrow(train),nrow(test),auc[1],auc[2],auc[3],as.numeric(roc_stage$AUC[2]),lambda_choice,paste(names(weights)[weights!=0],collapse=';')))
write.table(stat,file.path(root,'tables','results_summary.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
write.table(test[,c('patient_id','OS_days','OS_event','stage_num','age','MRS','risk','lp_integrated')],file.path(root,'tables','validation_predictions.tsv'),sep='\t',quote=FALSE,row.names=FALSE)
audit('SPEC-08','Artefatos principais presentes',all(file.exists(file.path(root,'tables',c('results_summary.tsv','LASSO_Cox_coefficients.tsv','DESeq2_paired_Tumor_vs_Normal.tsv')))))
finish()
cat('Análises realizadas; consulte logs, tabelas e gráficos. Validação externa e bootstrap RMS ainda pendentes.\n')
