import numpy as np
import pandas as pd


def main():
    df = pd.read_csv('2014.csv', index_col='学号')

    print(df['上课院系'].unique())
    print(df['课程性质'].unique())
    print(df['课程属性'].unique())

    print(df[df.课程名称 == '大学英语Ⅰ'])

    english_df = df[df.课程名称 == '大学英语Ⅰ']
    print(english_df[english_df.总成绩.astype('float')<60])


def clean_data():
    """
    清洗数据
    将非正常考试和没有数字成绩的数据清除出去以便于分析数据
    :return: None
    """
    files = ['2013.csv', '2014.csv', '2015.csv']
    for file in files:
        df = pd.read_csv(file, index_col='学号')
        df = df[(df.考试性质 == '正常考试') & (df.课程名称 != '创新实践活动')]
        df.to_csv(file.split('.')[0]+'result.csv')


def re_file():
    files = ['2013成绩列表.csv', '2014成绩列表.csv', '2015成绩列表.csv']
    for file in files:
        with open(file, 'r', encoding='gbk') as f:
            with open(file[:4]+'.csv', 'w', encoding='utf-8') as ff:
                print('start', file)
                ff.write(f.read())


if __name__ == '__main__':
    # main()
    clean_data()
