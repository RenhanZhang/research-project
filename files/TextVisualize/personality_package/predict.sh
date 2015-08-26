
# EXAMPLE
# ./predict.sh /home/public/weka-3-7-12/weka.jar functions.LinearRegression test.arff models/openness.linear-regression.model 

if [ -z $1 ];
    then 
        echo "Usage: ./predict.sh <classifier_name> <path_to_weka.jar> <test_arff> <path_to_saved_model>";
    else
        java -cp $1 weka.classifiers.$2 -T $3 -l $4 -p 0;
fi
