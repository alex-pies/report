import os

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
        df = df[(df.考试性质 == '正常考试') & (df.课程名称 != '创新实践活动')]
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


def public_basic_courses_fail_compare():
    """
    公共基础课每个年级挂科情况
    每年挂科比例较高的科目
    较高的科目的老师是谁 哈哈
    :return: None
    """
    dfs = {}
    for file in files:
        df = pd.read_csv(file, index_col='学号')
        df = df[(df.课程性质 == '公共基础课')]
        print(df)
        df.总成绩 = df.总成绩.astype('float64')
        df = df[(df.总成绩 < 60)]
        dfs[file[:4]] = df
        print(df[['姓名', '课程名称', '总成绩']])
    # print(dfs)


def general_elective_courses_fail_analysis():
    """
    通识选修课学分不够的数据分析
    :return: None
    """
    pass


if __name__ == '__main__':
    clean_data()
    single_subject_compare('大学英语Ⅰ')
    # public_basic_courses_fail_compare()
