#!/usr/bin/python
# -*- coding: utf-8 -*-
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import datetime

"""
The class contains methods for analyzing the last 14 days of user spending
"""
class Short_analyse:

    def __init__(self)->None:
        self.conn = sqlite3.connect('db.db')
        self.data2 = pd.read_sql('SELECT * FROM train_14days',
                                 self.conn)
        self.data2 = self.data2.sort_values('date')

    """The method is needed to calculate the day from the beginning of observations
    """
    def __transform2(self, string: str)->int:
        try:
            a = datetime.datetime.strptime(string, '%Y-%m-%d') \
                - datetime.datetime.strptime(self.start_time, '%Y-%m-%d'
                    )
            chislo = ''
            for i in str(a):
                if i == ' ':
                    break
                else:
                    chislo += i
            return int(chislo)
        except ValueError:
            return 0
        
    """ Writes grouped observations to df2 without outliers
        and incrementing window_rolling_sum
    """
    def getting_groupped_data(self)->pd.DataFrame:
        try:
            self.df2 = self.data2[['date', 'cost']]
            self.start_time = self.df2['date'].min()
            self.df2 = self.df2.groupby('date',
                                        as_index=False).agg({'cost': 'sum'})
            self.df2['window_rolling_sum'] = self.df2['cost'].cumsum()
            self.df2['day'] = self.df2['date'].apply(self.__transform2)  # finding day from start
            self.df2['day'][0] = 1
            self.df2 = self.df2[self.df2.cost <= 3000]
            return self.df2
        except Exception as e: print('Ошибка', e)


    def training_model(self)->tuple:
        try:
            self.model2 = LinearRegression(fit_intercept=False)
            (X, y) = (self.df2.day, self.df2.window_rolling_sum)
            X = np.array(X).reshape(-1, 1)
            self.model2.fit(X, y)
            self.y_pred = self.model2.predict(np.array(range(0,
                    28)).reshape(-1, 1))
            return (self.y_pred, self.model2)
        except Exception as e: print('Ошибка', e)
    
    """ Saves the spending schedule for the last 14 days
        and builds a forecast for the next 14 days
    """
    def saving_graphic_of_model(self, day: int)->None:
        try:
            sns.set_style('darkgrid')
            sns.lineplot(x=range(0, 28), y=self.y_pred, color='red')
            sns.scatterplot(data=self.df2, x='day', y='window_rolling_sum')
            
            #Decorate our plot - add lines and target
            sns.scatterplot(data={'day': np.array(range(13+day, 13+day+1)),
                                  'sum': self.y_pred[13+day:13+day+1]},
                            x = 'day',y = 'sum', color = ".2")
            #plus 13, because we have expenses every 14 days before
            plt.grid(True)
            plt.title("Прогноз расходов в случае 'линейного' поведения в сфере покупок")
            plt.text(13, self.y_pred[13+day:13+day+1] + 400,
                     f'Ваш прогноз трат - {round(float(self.y_pred[13+day:13+day+1]),2)} р',
                     ha = 'right') 
            plt.text(17, self.y_pred[13+day:13+day+1]/3,
                     'Вы здесь',
                     ha = 'right')
            
            plt.axhline(y = self.y_pred[13+day:13+day+1], color = 'black',
                        xmax = (13+day)/28, linestyle = '--')#level of expenses
            plt.axvline(x = range(13,14), color = 'black',
                        ymax = 0.45, linestyle = '--')#static line, show our position (14 day)
            
            plt.ylabel("Сумма трат за месяц")
            plt.xlabel("День")
            plt.savefig('Selecting_regression.png')
            plt.close()
        except Exception as e: print('Ошибка', e)


    def __check_time_part(self, time:str)->str:
        try:
            a = int(time[:2]) + 3 #Convert Grinvich time to Moscow time
            if a >= 19 and a < 24:
                return 'evening'
            elif a >= 13 and a < 19:
                return 'day'
            elif a >= 7 and a < 13:
                return 'morning'
            else:
                return 'night'
        except Exception as e: print('Ошибка', e)
        
    """ The function generates inscriptions on the pie plot - value and percentage
    """
    def __lettering_on_pie(self,pct:float, allvals:pd.Series)-> str:
        try:
            absolute = int(np.round(pct / 100. * np.sum(allvals)))
            return f"{pct:.1f}%\n({absolute:d} Руб.)"
        except Exception as e: print('Ошибка', e)
    
    """Groups data for the next 3 functions"""
    def preparing_data_for_timegraphics(self)->None:
        try:
            self.data2['time_of_day'] = self.data2['timing'
                    ].apply(self.__check_time_part)
            self.mean_amount = self.data2.groupby('time_of_day')['cost'].mean()
            self.time_amount = self.data2[['time_of_day', 'timing', 'cost'
                                          ]].sort_values('timing')
            self.sum_amount = self.data2.groupby('time_of_day')['cost'].sum()
        except Exception as e: print('Ошибка', e)


    """saving 2 graphics"""
    def bar_graphics(self)->None:
        try:
            (fig, ax) = plt.subplots()
            self.mean_amount.plot(kind='bar').set_ylabel('Mean expenses per day')
            plt.xticks(rotation=0)
            plt.title("Средние расходы за 2 недели, распределенные по времени дня")
            plt.savefig('barplot.png')
            plt.close()
            self.time_amount.plot(x='time_of_day', y='timing', kind='scatter',
                                  sizes=self.time_amount['cost'] / 10)
            plt.title("Все траты за последние 2 недели, распределенные по времени")
            plt.savefig('scatterplot.png')
            plt.close()
        except Exception as e: print('Ошибка', e)


    """saving 1 graphic"""
    def pie_graphic(self)->None:
        try:
            times = list(self.sum_amount.index)
            (fig, ax) = plt.subplots(figsize=(15, 7.5),
                                     subplot_kw=dict(aspect='equal'))
            (wedges, texts, autotexts) = ax.pie(self.sum_amount,
                    autopct=lambda pct: self.__lettering_on_pie(pct,
                    self.sum_amount))
            plt.setp(autotexts, size=8, weight='bold')
            ax.legend(wedges, times, title='Time of day', loc='center left',
                      bbox_to_anchor=(1, 0, 0.5, 1))
            plt.setp(autotexts, size=16, weight='bold')
            plt.title("Все траты за последние 2 недели, распределенные по времени дня")
            plt.savefig('pieplot.png')
            plt.close()
        except Exception as e: print('Ошибка', e)

"""
The class contains methods for analyzing the full data of user spending
"""
class Long_analyse:

    def __init__(self):
        self.conn = sqlite3.connect('db.db')
        self.data = pd.read_sql('SELECT * FROM training_5month',
                                self.conn)  # not 5 month - full data
        self.data = self.data.sort_values('date')

    """ Eliminates missing data from February so that the model trains correctly.
        The offset does not affect the rest of the information
    """
    def __transform(self, string:str)->int:
        try:
            if string[:4] == '2023':
                string = datetime.datetime.strptime(string, '%Y-%m-%d')
                string = str(datetime.datetime.date(string)
                             - datetime.timedelta(days=33))
            a = datetime.datetime.strptime(string, '%Y-%m-%d') \
                - datetime.datetime.strptime(self.start_time, '%Y-%m-%d')
            chislo = ''
            for i in str(a):
                if i == ' ':
                    break
                else:
                    chislo += i
            return int(chislo)
        except ValueError:
            return 0

    """Preparing_data"""
    def getting_groupped_data(self)->None:
        try:
            self.df = self.data[['date', 'cost']]
            self.df = self.df.groupby('date').agg({'cost': 'sum'})
            self.df['date'] = self.data['date'].unique()
            self.start_time = self.df['date'][0]
            self.df['day'] = self.df['date'].apply(self.__transform)
            self.df['window_rolling_sum'] = self.df['cost'].cumsum()
            self.df.day[0] = 0
            self.d = self.df[self.df.cost > 2000]
            self.df = self.df[self.df.cost <= 2000]
            self.df['day'] = self.df['date'].apply(self.__transform)
            self.df['window_rolling_sum'] = self.df['cost'].cumsum()
        except Exception as e: print('Ошибка', e)

    def preparing_data_for_model(self)->None:
        try:
            (X, y) = (self.df.day, self.df.window_rolling_sum)
            (self.X_train, self.X_test, self.y_train, self.y_test) = (X[X % 4
                    != 0], X[X % 4 == 0], y[X % 4 != 0], y[X % 4 == 0])
            self.X_train = np.array(self.X_train).reshape(-1, 1)
            self.y_train = np.array(self.y_train)
            self.X_test = np.array(self.X_test).reshape(-1, 1)
            self.y_test = np.array(self.y_test)
        except Exception as e: print('Ошибка', e)


    """Returns list of expenses next 30, 90, 365 days"""
    def training_model(self)->list:
        try:
            self.model = LinearRegression(fit_intercept=False)
            self.model.fit(self.X_train, self.y_train)
            temp = list(self.model.predict([[30], [90], [365]]))
            return temp
        except Exception as e: print('Ошибка', e)
    
    """Returns DataFrame with Data outliers (purchases > 3000p)"""
    def unusual_days(self)->pd.DataFrame:
        try:
            self.d = self.d.drop('day', axis=1)
            self.d.index = range(0, len(self.d))
            self.d = self.d.drop('window_rolling_sum', axis=1)
            self.d = self.d[['date', 'cost']]
            return self.d
        except Exception as e: print('Ошибка', e)

    """Returns the string of information about expenses"""
    def statistic_by_day(self, spis:list)->str:
        try:
            self.vrem = self.data.groupby('date',
                                          as_index=False).agg({'cost': 'sum'})
            temp = float(self.vrem.mean() + 1.96 * self.vrem.std()
                         / np.sqrt(len(self.vrem)))
            tem = float(self.vrem.mean() - 1.96 * self.vrem.std()
                        / np.sqrt(len(self.vrem)))
            return f'- За месяц вы обычно тратите {round(spis[0])} рублей, за сезон {round(spis[1])} рублей,\
за год {round(spis[2])} рублей\n\
- Ваша дневная норма трат: от {round(tem)} до {round(temp)} рублей\n\
- Количество дней превышения нормы: {len(self.vrem[self.vrem["cost"]>temp])}\n\
- В эти дни вы позволяете себе превышать норму в среднем в {round(self.vrem[self.vrem["cost"]>temp].mean()[0]/temp,1)} раза'
        except Exception as e: print('Ошибка', e)

    def saving_bar_strip_plot(self)->None:
        try:
            sns.barplot(x=self.vrem['cost'],
                        palette='hls',
                        linewidth=3,
                        edgecolor=".5",
                        facecolor=(0, 0, 0, 0),
                        errcolor=(0.75,0,0,0.5),
                        capsize=.4)
            sns.stripplot(x=self.vrem['cost'],
                          marker="d",
                          linewidth=1,
                          alpha=0.4,
                          color="yellow")
            plt.savefig('boxplot.png')
            plt.close()
        except Exception as e: print('Ошибка', e)

    def top_13_expenses(self)->None:
        try:
            depends = self.data.groupby(self.data.place,
                                        as_index=False).agg({'cost': ['sum',
                                                            'mean'], 'date': 'max'})
            depends = depends.sort_values(('cost', 'sum'), ascending=False)[:13]
            depends.columns = ['place', 'sum', 'avg', 'last_visit']
            depends.avg = depends.avg.apply(round)
            depends["sum"] = depends["sum"].apply(round)
            depends.index = range(1, len(depends) + 1)
            #save table as png
            fig, ax = plt.subplots(figsize = (20,4))
            ax.axis('off')
            ax.table(cellText = depends.values,
                     colLabels = depends.columns,
                     loc = 'center',
                     colWidths = [0.2,0.05,0.05,0.1])
            plt.savefig('dataframe.png',bbox_inches = 'tight', pad_inches = 0.5)
            plt.close()
        except Exception as e: print('Ошибка', e)

    """Converts data into month and return month"""
    def __transform_month(self,string:str)->int:
        try:
            a=datetime.datetime.strptime(string, '%Y-%m-%d')
            return int(str(a)[5:7])
        except Exception as e: print('Ошибка', e)

    def prepare_data_for_ttest_month(self, spis:list)->tuple:
        try:
            temp = self.data.groupby(self.data.place,
                                        as_index=False).agg({'cost': ['sum',
                                                            'mean'], 'date': 'max'})
            temp.columns=['place','cost','mean','maxi']
            temp['month'] = temp.maxi.astype(str).apply(self.__transform_month)
            m_1, m_2 = spis.split()
            m_1, m_2 = int(m_1), int(m_2)
            list_1 = temp[temp['month'] == m_1]
            list_2 = temp[temp['month'] == m_2]
            return list_1, list_2, m_1, m_2
        except Exception as e: print('Ошибка', e)
        

    """ The function performs a t-test and returns a decision
        on the difference in expenses in two different months
    """
    def ttest_month(self, list_1:list, list_2:list, m_1:int, m_2:int)->str:
        try:
            mean1 = np.mean(list_1.cost)
            mean2 = np.mean(list_2.cost)
            p_value= round(stats.ttest_ind(a=list_1.cost, b=list_2.cost, equal_var=True)[1]*100,3)
            if p_value<20:
                return f'Среднее значение трат намного выше в {m_1 if mean1>mean1 else m_2} \
месяце и это не случайность. Мы уверены что не ошиблись с вероятностью {100-p_value}%'
            else:
                return 'Данные двух месяцев слишком похожи, чтобы сделать какие-то выводы \
насчет ваших трат. В любом случае, старайтесь тратить меньше!'
        except Exception as e: print('Ошибка', e)

