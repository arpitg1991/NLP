#! /bin/sh

#replace with _RARE and generate new train file
echo "replaceing words that have count < 5 with _RARE_"

python count_cfg_freq.py parse_train.dat > cfg.counts

python replaceRare.py cfg.counts parse_train.dat rare_train.dat

python count_cfg_freq.py rare_train.dat > rare.counts


#run normal CKY on parse_dev
echo "running CKY on non markovised rules. q5results.dat will be generated"

python CKY.py rare.counts parse_dev.dat q5results.dat


#run CKY on vertically markovised rules
echo "running CKY on markovised rules. q6results.dat will be generated"

python count_cfg_freq.py parse_train_vert.dat > vert.counts

python replaceRare.py vert.counts parse_train_vert.dat vert_rare_train.dat

python count_cfg_freq.py vert_rare_train.dat > vert_rare.counts

python markovCKY.py vert_rare.counts parse_dev.dat q6results.dat
