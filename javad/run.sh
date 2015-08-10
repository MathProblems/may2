#p kushman_formatter.py emnlp.reduced.kushformat.txt > data_for_kush/questions.json

for i in {0..4};
do
    echo $i;
    python3 fold_train_test.py $i train

    python3 train_local.py data_for_kush/train$i;
    python3 formattrainingdata.py data/fold$i\.local.training ;
    ~/libsvm-3.18/svm-train -b 1 -c 100 data/fold$i\.local.data data/fold$i\.local.m ;
    #python3 train_global.py data_for_kush/train$i data/fold$i\.local.m 4 fold$i ;
    #~/libsvm-3.18/svm-train -b 1 -c 100 data/fold$i\.global.data data/fold$i\.global.m ;
    python3 inference.py data_for_kush/test$i data/fold$i\.local.m data/fold$i\.global.m > results/fold$i\.txt ;
done

