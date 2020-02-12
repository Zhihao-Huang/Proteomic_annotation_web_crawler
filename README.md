# Proteomic_annotation_web_crawler
get annotation from Uniprot
#How it works：
#Import gene names by csv file, then search Uniprot database, matching accession ID and GO annotation, and finally output as xls file.
#6 parameters：
#1. workpath; 2. geneID csv file; 3. output result file; 4. output mismatch file; 5. choose a database.
#Note:
#1. all geneID in one column in csv file;
#2. there may be mismatch accessionID when using gene symbol ID for searching. the 2nd column of result file is geneID from database,
#   which is used for proofing ID matching.
#3. python2.7.
#4. model: pyExcelerator。
#Version: Web_Crawler20180316; select GO database.
#author：zhihao.jnu@gmail.com
