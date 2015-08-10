python3 train_local.py data_for_kush/train$1 t once1 ;
python3 formattrainingdata.py data/once1.local.training ;
~/libsvm-3.18/svm-train -b 1 -c 10 data/once1.local.data data/once1.local.m ;
python3 train_global.py data_for_kush/train$1 data/once1.local.m 4 once1 ;
#python3 train_global.py data_for_kush/train$1 data/fold$1\.local.m 4 once1 ;
~/libsvm-3.18/svm-train -b 1 -c 100 data/once1.global.data data/once1.global.m ;
python3 inference.py data_for_kush/test$1 data/once1.local.m data/once1.global.m > results/once$1\.txt ;
#python3 inference.py data_for_kush/test$1 data/fold$1\.local.m data/once1.global.m > results/once$1\.txt ;

