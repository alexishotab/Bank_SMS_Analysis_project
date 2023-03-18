import sqlite3


class Database:
    
    def __init__(self,database_file:str)->None: #database_file - path to database
        self.connection=sqlite3.connect(database_file,check_same_thread = False)
        self.cursor =self.connection.cursor()

    """Занос данных в БД, согласно типу операции
    """
    def add_info(self,sp:list)->None:
        with self.connection:
            if sp[3].lower() == 'покупка':
                self.cursor.execute("INSERT INTO `purchases` (`purchases_id`,`card`,`timing`,`cost`,`place`,`balance`,`date`) VALUES(?,?,?,?,?,?,?)",(sp[0],sp[1],sp[2],sp[4],sp[5],sp[6],sp[7]))
                self.cursor.execute("INSERT INTO `training_5month` (`train_id`,`card`,`timing`,`cost`,`place`,`balance`,`date`) VALUES(?,?,?,?,?,?,?)",(sp[0],sp[1],sp[2],sp[4],sp[5],sp[6],sp[7]))
                self.connection.commit()
            elif sp[3].lower() == 'выдача':
                self.cursor.execute("INSERT INTO `extraditions` (`extraditions_id`,`card`,`timing`,`cost`,`balance`,`date`) VALUES(?,?,?,?,?,?)",(sp[0],sp[1],sp[2],sp[4],sp[6],sp[7]))
                self.connection.commit()
            elif sp[3].lower() == 'перевод':
                self.cursor.execute("INSERT INTO `transfers` (`transfers_id`,`card`,`timing`,`cost`,`balance`,`date`) VALUES(?,?,?,?,?,?)",(sp[0],sp[1],sp[2],sp[4],sp[6],sp[7]))
                self.connection.commit()
            elif sp[3].lower() == 'зачисление':
                self.cursor.execute("INSERT INTO `creditions` (`creditions_id`,`card`,`timing`,`cost`,`balance`,`date`) VALUES(?,?,?,?,?,?)",(sp[0],sp[1],sp[2],sp[4],sp[6],sp[7]))
                self.connection.commit()
                
    """Занос данных для анализа последних 14 дней 
    """
    def add_14days(self,sp:list)->None:
        with self.connection:
            if sp[3].lower() == 'покупка':
                self.cursor.execute("INSERT INTO `train_14days` (`train_id`,`card`,`timing`,`cost`,`place`,`balance`,`date`) VALUES(?,?,?,?,?,?,?)",(sp[0],sp[1],sp[2],sp[4],sp[5],sp[6],sp[7]))
                self.connection.commit()
            
    def delete_info(self)->None:
        with self.connection:
                self.cursor.execute("DELETE FROM `purchases`")
                self.connection.commit()
                self.cursor.execute("DELETE FROM `extraditions`")
                self.connection.commit()
                self.cursor.execute("DELETE FROM `transfers`")
                self.connection.commit()
                self.cursor.execute("DELETE FROM `creditions`")
                self.connection.commit()
                self.cursor.execute("DELETE FROM `train_14days`")
                self.connection.commit()
                #некоторые данные заносились вручную, их train_id<0  их не трогать лучше
                self.cursor.execute("DELETE FROM `training_5month` WHERE `train_id`>0")  
                self.connection.commit()
                
