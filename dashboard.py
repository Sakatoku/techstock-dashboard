import streamlit as st # type:ignore
import pandas as pd # type:ignore
import altair as alt # type:ignore
import json

# JSONを読み込んでdictを返す関数
def load_json(path: str) -> dict:
    return json.load(open(path, 'r'))

# CSVを読み込む関数
def load_csv(path: str) -> pd.DataFrame:
    # 1行目をヘッダーとして読み込む
    return pd.read_csv(path, header=0)

# 問題集の情報を読み込む
info = load_json('data/info.json')
# 問題集名のリストを作成
testnames_in_info = [info[i]['name'] for i in range(len(info))]

# 実施状況を読み込む
base_df = load_csv('data/result.csv')

# dateを日付にする。CSVのdateは'YYYY-MM-DD'の形式なので、それをpd.to_datetimeで日付型に変換
base_df.date = pd.to_datetime(base_df['date'], format='%Y-%m-%d')

# 日ごとの演習回数を集計する関数
def count_by_date(df: pd.DataFrame) -> pd.DataFrame:
    # dateとnameでグループ化して、countで集計
    df = df.groupby(['date', 'name'], as_index=False).count()

    # データをピボットする
    df = df.pivot(index='date', columns='name', values='sequence')
    df = df.reset_index()
    # NaNを0に変換
    df = df.fillna(0)

    # date_listの日付を昇順にソート
    df = df.sort_values('date')

    return df

# 問題集の網羅率の推移を集計する関数
def coverage_by_date(df: pd.DataFrame) -> pd.DataFrame:
    # nameとsequenceでグループ化して、最も早いdateの行を抽出
    df = df.groupby(['name', 'sequence'], as_index=False).first()

    # dateとnameでグループ化して、countで集計
    df = df.groupby(['date', 'name'], as_index=False).count()

    # データをピボットする
    df = df.pivot(index='date', columns='name', values='sequence')
    df = df.reset_index()
    # NaNを0に変換
    df = df.fillna(0)

    # date_listの日付を昇順にソート
    df = df.sort_values('date')

    # 問題集の情報を用いて網羅率を計算
    labels = []
    for name in testnames_in_info:
        # 問題集の情報を取得
        total = 0
        for i in range(len(info)):
            if info[i]['name'] == name:
                total = info[i]['amount']
        # 問題集の情報に問題数が記載されていなければスキップ
        if total <= 0:
            continue

        # nameについて、日ごとの累計和を計算
        cumsom = df[name].cumsum()
        # 網羅率を計算してカラムを追加
        label = 'coverage(%):' + name
        df[label] = cumsom / total * 100
        # 網羅率のカラム名をリストに追加
        labels.append(label)

    return df, labels

# 正解率の推移を集計する関数
def accuracy_by_date(df: pd.DataFrame) -> pd.DataFrame:
    # dataのユニークな値を取得して昇順にソート
    date_list = df['date'].unique()
    date_list.sort()

    # dfから問題集名のリストを作成
    testnames_in_origin = df.name.unique().tolist()

    # dateと正解率を記録するための空のDataFrameを作成
    columns = ['date'] + testnames_in_origin
    accuracy_df = pd.DataFrame(columns=columns)

    # date_listの日付ごとに正解率を計算
    for i, date in enumerate(date_list):
        # date以前のデータを抽出
        date_df = df[df['date'] <= date]

        # nameとsequenceでグループ化して、最も遅いdateの行を抽出
        date_df = date_df.groupby(['name', 'sequence'], as_index=False).last()

        # nameごとにcorrectとincorrectを集計
        date_df = date_df.groupby(['name'], as_index=False).sum(numeric_only=True)

        # 正解率を計算
        date_df['accuracy'] = date_df['correct'] / (date_df['correct'] + date_df['incorrect']) * 100

        # dateと正解率を記録
        row = {'date': date}
        testnames_in_df = date_df.name.tolist()
        for name in testnames_in_origin:
            if name in testnames_in_df:
                row[name] = date_df[date_df['name'] == name]['accuracy'].values[0]
            else:
                row[name] = 0
        df_row = pd.DataFrame(row, index=[0])
        accuracy_df = pd.concat([accuracy_df, df_row], ignore_index=True)

    return accuracy_df


# 日ごとの演習回数を集計
count_df = count_by_date(base_df)
# 問題集名のリストをdfに含まれるものに絞る
testnames_in_df = [name for name in count_df.columns.tolist() if name != 'date']
testnames = set(testnames_in_info) & set(testnames_in_df)
# グラフを描画
st.title('日ごとの演習回数')
with st.expander('data'):
    st.dataframe(count_df)
st.bar_chart(count_df, x='date', y=testnames)

# 問題集の網羅率の推移を集計
coverage_df, coverage_labels = coverage_by_date(base_df)
# グラフを描画
st.title('問題集の網羅率')
with st.expander('data'):
    st.dataframe(coverage_df)
st.line_chart(coverage_df, x='date', y=coverage_labels)

# 正解率の推移を集計
accuracy_df = accuracy_by_date(base_df)
# 問題集名のリストをdfに含まれるものに絞る
testnames_in_df = [name for name in count_df.columns.tolist() if name != 'date']
testnames = set(testnames_in_info) & set(testnames_in_df)
# グラフを描画
st.title('正解率')
with st.expander('data'):
    st.dataframe(accuracy_df)
st.line_chart(accuracy_df, x='date', y=testnames)
