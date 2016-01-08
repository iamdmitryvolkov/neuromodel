if [ $# == 0 ]
then
echo Enter args:
read args
python activity_analizer.py $args
else
python activity_analizer.py $@
fi
read foo