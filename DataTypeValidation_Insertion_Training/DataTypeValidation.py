import shutil
# import sqlite3
from datetime import datetime
from os import listdir
import os
import csv
from application_logging.logger import App_Logger
from django.db import connection



class dBOperation:
    """
      This class shall be used for handling all the SQL operations.


      """
    def __init__(self):
        # self.path = 'Training_Database/'
        # self.path = 'Project_Database/'
        # self.path = ''
        self.badFilePath = "Training_Raw_files_validated/Bad_Raw"
        self.goodFilePath = "Training_Raw_files_validated/Good_Raw"
        self.logger = App_Logger()


    def dataBaseConnection(self,DatabaseName):

        """
                Method Name: dataBaseConnection
                Description: This method creates the database with the given name and if Database already exists then opens the connection to the DB.
                Output: Connection to the DB
                On Failure: Raise ConnectionError

                """
        try:
            # conn = sqlite3.connect(self.path+DatabaseName+'.db')
            # conn = sqlite3.connect(DatabaseName+'.db')
            conn = connection
            print("Connection object: ",conn)
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Opened %s database successfully" % DatabaseName)
            file.close()
        except ConnectionError:
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Error while connecting to database: %s" %ConnectionError)
            file.close()
            raise ConnectionError
        return conn

    def createTableDb(self,DatabaseName,column_names):
        """
                        Method Name: createTableDb
                        Description: This method creates a table in the given database which will be used to insert the Good data after raw data validation.
                        Output: None
                        On Failure: Raise Exception

                        """
        try:
            conn = self.dataBaseConnection(DatabaseName)
            c=conn.cursor()
            c.execute("DROP TABLE IF EXISTS good_raw_data_training")
            print("The cursor in create table func :",c)
            c.execute("SELECT count(tablename)  FROM pg_tables WHERE tablename = 'good_raw_data_training'")
            row = c.fetchone()
            print(row)
            tab_count = row[0]
            if tab_count ==1:
                conn.close()
                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()

                file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                file.close()

            else:

                for key in column_names.keys():
                    type = column_names[key]

                    #in try block we check if the table exists, if yes then add columns to the table
                    # else in catch block we will create the table
                    try:
                        #cur = cur.execute("SELECT name FROM {dbName} WHERE type='table' AND name='Good_Raw_Data'".format(dbName=DatabaseName))
                        c.execute('ALTER TABLE good_raw_data_training ADD COLUMN "{column_name}" {dataType}'.format(column_name=key,dataType=type))
                    except:
                        c.execute('CREATE TABLE  good_raw_data_training ({column_name} {dataType})'.format(column_name=key, dataType=type))


                    # try:
                    #     #cur.execute("SELECT name FROM {dbName} WHERE type='table' AND name='Bad_Raw_Data'".format(dbName=DatabaseName))
                    #     conn.execute('ALTER TABLE Bad_Raw_Data ADD COLUMN "{column_name}" {dataType}'.format(column_name=key,dataType=type))
                    #
                    # except:
                    #     conn.execute('CREATE TABLE Bad_Raw_Data ({column_name} {dataType})'.format(column_name=key, dataType=type))


                conn.close()

                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()

                file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                self.logger.log(file, "Closed %s database successfully" % DatabaseName)
                file.close()

        except Exception as e:
            file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
            self.logger.log(file, "Error while creating table: %s " % e)
            file.close()
            conn.close()
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Closed %s database successfully" % DatabaseName)
            file.close()
            raise e


    def insertIntoTableGoodData(self,Database):

        """
                               Method Name: insertIntoTableGoodData
                               Description: This method inserts the Good data files from the Good_Raw folder into the
                                            above created table.
                               Output: None
                               On Failure: Raise Exception

        """

        conn = self.dataBaseConnection(Database)
        goodFilePath= self.goodFilePath
        badFilePath = self.badFilePath
        onlyfiles = [f for f in listdir(goodFilePath)]
        log_file = open("Training_Logs/DbInsertLog.txt", 'a+')
        c=conn.cursor()

        for file in onlyfiles:
            try:
                    # path = goodFilePath + '/' + file
                    # query_str = r"\copy good_raw_data_training from '{}' with delimiter as ',' NULL AS 'null' csv".format(path)
                with open(goodFilePath+'/'+file, "r") as f:
                    # c.execute(query_str)
                    # conn.commit()
                    next(f)
                    reader = csv.reader(f, delimiter="\n")
                    for line in enumerate(reader):
                        for list_ in (line[1]):
                            try:
                                c.execute('INSERT INTO good_raw_data_training values ({values})'.format(values=(list_)))
                                self.logger.log(log_file," %s: File loaded successfully!!" % file)
                                conn.commit()
                            except Exception as e:
                                raise e
                            

            except Exception as e:

                conn.rollback()
                self.logger.log(log_file,"Error while inserting into table: %s " % e)
                shutil.move(goodFilePath+'/' + file, badFilePath)
                self.logger.log(log_file, "File Moved Successfully %s" % file)
                log_file.close()
                conn.close()

        conn.close()
        log_file.close()


    def selectingDatafromtableintocsv(self,Database):

        """
                               Method Name: selectingDatafromtableintocsv
                               Description: This method exports the data in GoodData table as a CSV file. in a given location.
                                            above created .
                               Output: None
                               On Failure: Raise Exception


        """

        self.fileFromDb = 'Training_FileFromDB/'
        self.fileName = 'InputFile.csv'
        log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
        try:
            conn = self.dataBaseConnection(Database)
            sqlSelect = "SELECT *  FROM good_raw_data_training"
            cursor = conn.cursor()

            cursor.execute(sqlSelect)
            print("Started selecting data from data base")
            results = cursor.fetchall()

            # Get the headers of the csv file
            headers = [i[0] for i in cursor.description]

            if os.path.isdir(self.fileFromDb):
                shutil.rmtree(self.fileFromDb)
            #Make the CSV ouput directory
            if not os.path.isdir(self.fileFromDb):
                os.makedirs(self.fileFromDb)

            # Open CSV file for writing.
            csvFile = csv.writer(open(self.fileFromDb + self.fileName, 'w', newline=''),delimiter=',', lineterminator='\r\n',quoting=csv.QUOTE_ALL, escapechar='\\')

            # Add the headers and data to the CSV file.
            
            csvFile.writerow(headers)
            csvFile.writerows(results)

            self.logger.log(log_file, "File exported successfully!!!")
            log_file.close()

        except Exception as e:
            self.logger.log(log_file, "File exporting failed. Error : %s" %e)
            log_file.close()





