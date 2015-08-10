python3 train_local.py data_for_kush/train$1;
python3 formattrainingdata.py data/$1\.local.training ;
~/libsvm-3.18/svm-train -q -b 1 -c 100 data/$1\.local.data data/$1\.local.m ;
python3 train_global.py data_for_kush/train$1 data/$1\.local.m > mute;
~/libsvm-3.18/svm-train -q -b 1 -c 1000 data/$1\.global.data data/$1\.global.m ;
python3 newinference.py data_for_kush/test$1 data/$1\.local.m data/$1\.global.m > results/fold$1\.txt ;
