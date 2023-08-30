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

# 実施状況を読み込む
df = load_csv('data/result.csv')

# dateを日付にする。CSVのdateは'YYYY-MM-DD'の形式なので、それをpd.to_datetimeで日付型に変換
df.date = pd.to_datetime(df['date'], format='%Y-%m-%d')

# nameとdateでグループ化して、countで集計
df = df.groupby(['name', 'date'], as_index=False).count()
# nameのリストを抽出
names_in_result = df.name.unique().tolist()

# データをピボットする
df = df.pivot(index='date', columns='name', values='sequence')
df = df.reset_index()
# NaNを0に変換
df = df.fillna(0)

# 問題集の情報に記載されているnameのリストを作成
names_in_info = [info[i]['name'] for i in range(len(info))]
# それぞれのnameのリストに共通のものを抽出
name_list = set(names_in_result) & set(names_in_info)

# グラフを描画
st.title('問題集の実施状況')
with st.expander('data'):
    st.dataframe(df)
st.bar_chart(df, x='date', y=name_list)

# 問題集の情報を用いて実施率を計算
labels = []
for name in name_list:
    # 問題集の情報を取得
    total = 0
    for i in range(len(info)):
        if info[i]['name'] == name:
            total = info[i]['amount']
    # 問題集の情報に問題数が記載されていなければスキップ
    if total <= 0:
        continue

    # 実施率を計算
    # 累計和を計算
    cumsom = df[name].cumsum()
    label = 'complete(%):' + name
    df[label] = cumsom / total * 100
    labels.append(label)

# グラフを描画
st.title('問題集の実施率')
with st.expander('data'):
    st.dataframe(df)
st.line_chart(df, x='date', y=labels)