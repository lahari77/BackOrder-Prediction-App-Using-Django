import pandas
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader_prediction
from application_logging import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
import os


class prediction:

    def __init__(self,path):
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()
        self.pred_data_val = Prediction_Data_validation(path)

    def predictionFromModel(self):

        try:
            self.pred_data_val.deletePredictionFile() #deletes the existing prediction file from last run
            self.log_writer.log(self.file_object,'Deleted previous predictions file')
            self.log_writer.log(self.file_object,'Start of Prediction')
            data_getter=data_loader_prediction.Data_Getter_Pred(self.file_object,self.log_writer)
            data=data_getter.get_data()
            data1=data
            print("From DB :",data1.head())
            preprocessor=preprocessing.Preprocessor(self.file_object,self.log_writer)
            data = preprocessor.remove_columns(data, ["index_product", "sku","oe_constraint"]) #removing oe_constraint as it was removed in training

            data = preprocessor.encodeCategoricalValuesPred(data)
            is_null_present=preprocessor.is_null_present(data)
            if(is_null_present):
                # data=preprocessor.impute_missing_values(data)
                data1 = data1.dropna()
                data = data.dropna()

            #cols_to_drop=preprocessor.get_columns_with_zero_std_deviation(data)
            #data=preprocessor.remove_columns(data,cols_to_drop)

            data = preprocessor.scale_numerical_columns(data)

            data = preprocessor.pcaTransformation(data)
            #data=data.to_numpy()
            file_loader=file_methods.File_Operation(self.file_object,self.log_writer)
            # kmeans=file_loader.load_model('KMeans')

            ##Code changed
            #pred_data = data.drop(['Wafer'],axis=1)
            #clusters=kmeans.predict(data.drop(['Wafer'],axis=1))#drops the first column for cluster prediction
            #data['clusters']=clusters
            ##for i in clusters:
            #cluster_data= data[data['clusters']==i]
            #wafer_names = list(cluster_data['Wafer'])
            ##cluster_data = cluster_data.drop(['clusters'],axis=1)
            model_name = file_loader.find_correct_model_file()

            model = file_loader.load_model(model_name)
            result=list(model.predict(data))
            #result = pandas.DataFrame(list(zip(wafer_names,result)),columns=['Wafer','Prediction'])
            result = pandas.DataFrame(result, columns=['Prediction'])
            print("Result head: ",result.head())
            result["Prediction"] = result["Prediction"].map({ 0 : "Yes", 1: "No"})
            print(len(result["Prediction"]))
            print(len(data1["index_product"]))
            result = pandas.concat([data1, result], axis=1)
            print(result.head())
            path="Prediction_Output_File/Predictions.csv"
            result.to_csv("Prediction_Output_File/Predictions.csv",header=True,mode='a+') #appends result to prediction file
            print(os.path.exists('Prediction_Output_File/Predictions.csv'))
            self.log_writer.log(self.file_object,'End of Prediction')
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occured while running the prediction!! Error:: %s' % ex)
            raise ex
        return path

            # old code
            # i=0
            # for row in data:
            #     cluster_number=kmeans.predict([row])
            #     model_name=file_loader.find_correct_model_file(cluster_number[0])
            #
            #     model=file_loader.load_model(model_name)
            #     #row= sparse.csr_matrix(row)
            #     result=model.predict([row])
            #     if (result[0]==-1):
            #         category='Bad'
            #     else:
            #         category='Good'
            #     self.predictions.write("Wafer-"+ str(wafer_names[i])+','+category+'\n')
            #     i=i+1
            #     self.log_writer.log(self.file_object,'The Prediction is :' +str(result))
            # self.log_writer.log(self.file_object,'End of Prediction')
            #print(result)




