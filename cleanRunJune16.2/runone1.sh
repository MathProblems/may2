python3 train_local3.py data_for_kush/train2;
python3 formattrainingdata1.py data/2.local.training.3 ;
~/libsvm-3.18/svm-train -q -b 1 -c 100 data/2.local.training.3.data data/2.local.3.m ;
python3 train_global3.py data_for_kush/train2 data/2.local.3.m > mute;
~/libsvm-3.18/svm-train -q -b 1 -c 1000 data/2.global.data.3 data/2.global.3.m ;
python3 newinference3.py data_for_kush/test2 data/2.local.3.m data/2.global.3.m > results/ablat3.txt ;
