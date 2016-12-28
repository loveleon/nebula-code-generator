## 生成data目录下的所有文件到gen/cpp目录

for file in ../data/* 
do
    python ../dbgen/gen.py -i $file -o ../gen/cpp
done