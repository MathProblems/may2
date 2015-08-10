python3 javad_train_local.py ;
python3 formattrainingdata.py data/ixl.local.training ;
~/libsvm-3.18/svm-train -b 1 -c 100 data/ixl.local.data data/ixl.local.m ;
python3 javad_train_global.py ;
~/libsvm-3.18/svm-train -b 1 -c 1000 data/ixl.global.data data/ixl.global.m ;
python3 javad_newinference.py > ma2.errors.txt;
