python3 jAll_train_local.py ;
python3 formattrainingdata.py data/3.local.training ;
~/libsvm-3.18/svm-train -b 1 -c 100 data/3.local.data data/3.local.m ;
python3 jAll_train_global.py ;
~/libsvm-3.18/svm-train -b 1 -c 1000 data/3.global.data data/3.global.m ;
python3 jAll_newinf.py > jAll.errors.txt
