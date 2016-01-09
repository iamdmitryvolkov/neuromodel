if [ $# == 0 ]
then
echo Enter args:
read args
python activity_analyzer.py $args
else
python activity_analyzer.py $@
fi
read foo