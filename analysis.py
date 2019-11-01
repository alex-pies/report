import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

fake_files = ['2013.csv', '2014.csv', '2015.csv']
files = ['2013_result.csv', '2014_result.csv', '2015_result.csv']


def clean_data():
    """
    清洗数据
    将非正常考试和没有数字成绩的数据清除出去以便于分析数据
    :return: None
    """

    for fake_file, file in zip(fake_files, files):
        df = pd.read_csv(fake_file, index_col='学号')
        df = df[(df.考试性质 == '正常考试') & (df.课程名称 != '创新实践活动') & (df.课程性质 != '素质拓展环节') &  (df.课程性质 != '其它环节')]
        # 至于为什么要一个个排除呢，因为学艺不精目前还没找到的排除方法。。。 你们找吧
        df.to_csv(file)
    print('clean data done')


def single_subject_compare(subject):
    """
    单个学科各年级比较，平均分，最高分，最低分，中位数等
    :param subject: 学科名称
    :return: None
    """
    dfs = []
    for file in files:
        if not os.path.isfile(file):
            # 检查文件是否存在
            print('file: %s not found' % file)
            exit(1)
        df = pd.read_csv(file, index_col='学号')
        if subject not in df.课程名称.unique():
            # 检查这个科目是否存在
            print('subject: %s not found in file: %s' % (subject, file))
            exit(1)
        df = df[df.课程名称 == subject][['总成绩']]
        df['总成绩'] = df['总成绩'].astype('float64')
        print(df.describe())
        print(df.mean())
        dfs.append(df)
    # todo: 根据describe结果进行数据的记录和生成统计图
    plt_df = pd.DataFrame({
        'mean': [df.总成绩.mean() for df in dfs],
        'max': [df.总成绩.max() for df in dfs],
        'min': [df.总成绩.min() for df in dfs],
        'median': [df.总成绩.median() for df in dfs]
    }, index=[file[:4] for file in files])
    print(plt_df)
    plt_df.plot.bar().get_figure().savefig(os.path.join('images', 'single_subject.png'))
    print('single-subject-compare bar figure done.')
    # todo: 各年级分数段占比的饼状图

    def level(a):
        if a >= 90:
            return '[90, 100)'
        elif 80 <= a < 90:
            return '[80, 90)'
        elif 70 <= a < 80:
            return '[70, 80)'
        elif 60 <= a < 70:
            return '[60, 70)'
        else:
            return '[0, 60)'

    pie_index = ['[90, 100)', '[80, 90)', '[70, 80)', '[60, 70)', '[0, 60)']
    for index, df in enumerate(dfs):
        counts = []
        df['级别'] = df.apply(lambda x: level(x.总成绩), axis=1)
        for item in pie_index:
            counts.append(df[df==item].count()['级别'])
        s = pd.Series(data=counts, index=pie_index, name='数量')
        print(s)
        s.plot.pie()
        title = 'single_subject_%s_pie' % (files[index][:4],)
        plt.title(title)
        # todo: 饼图会和之前的直方图重叠
        plt.savefig(os.path.join('images', title+'.png'))


def general_subject_analysis():
    """
    通识选修课近三年的占比走势
    :return:
    """
    rates = []
    for file in files:
        df = pd.read_csv(file, index_col='学号')
        df.课程性质, df.课程名称, df.学分 = df.课程性质.astype(str), df.课程名称.astype(str), df.学分.astype('float64')
        df['课程形式'] = df.apply(lambda x: '网课' if '尔雅网课' in x.课程名称 else '传统', axis=1)
        df['课程性质'] = df.apply(lambda x: '通识选修课' if '通识' in x.课程性质 else '非', axis=1)
        df = df[(df.课程名称 != 'nan') & (df.课程性质 == '通识选修课')]
        print(df[['学分', '课程形式']])
        df = df[['学分', '课程形式']]
        print(pd.DataFrame(data={
            '总学分': [df.学分.sum()],
            '传统学分': [df[df.课程形式 == '传统'].学分.sum()],
            '网课学分': [df[df.课程形式 == '网课'].学分.sum()]
        }))
        rates.append(df[df.课程形式 == '网课'].学分.sum() / df.学分.sum())
    print(rates)
    rates_df = pd.Series(rates, index=[file[:4] for file in files])
    rates_df.plot.line().get_figure().savefig(os.path.join('images', '通识选修所有学生修得学分占比折线图'+'.png'))


def general_subject_credit_warnings(grade, no, std_credits):
    """
    通识选修课没够的人
    :return:  列表，列表元素是 没够的人 + 不够的不同学科的学分
    """
    file = grade + '_result.csv'
    if not os.path.isfile(file):
        print('no such file')
        return
    df = pd.read_csv(file, index_col='学号')
    df.课程性质, df.课程名称, df.学分 = df.课程性质.astype(str), df.课程名称.astype(str), df.学分.astype('float64')
    df = df.loc[no]
    if df.shape[0] == 0:
        print('no such student.')
        return
    df['课程性质'] = df.apply(lambda x: x.课程性质[5:].replace('(', '').replace(')', '') if '通识' in x.课程性质 else 'nan', axis=1)
    df = df[df.课程性质 != 'nan']
    print(df[['课程性质', '课程名称', '学分']])
    dff = df[['课程性质', '课程名称', '学分']]
    print(dff.groupby('课程性质').agg({'学分': 'sum'}).sort_index())
    student_result = dff.groupby('课程性质').agg({'学分': 'sum'})

    std_df = pd.DataFrame(data={'标准': [item[1] for item in std_credits]}, index=[item[0] for item in std_credits])
    print('std: ', std_df)
    print(std_df.join(student_result))

    real_result = std_df.join(student_result)
    sub = (real_result.标准 - real_result.学分)
    print(sub[sub > 0])


if __name__ == '__main__':
    clean_data()
    # single_subject_compare('大学英语Ⅰ')
    # general_subject_analysis()
    general_subject_credit_warnings('2014', 201414010426, [('人文', 19.0), ('自然', 20.0), ('艺体', 21.0)])
