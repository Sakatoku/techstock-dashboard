# techstock-dashboard

資格試験の問題集の実施状況を可視化するダッシュボード。  

## 環境構築

```sh
conda create -n streamlit python=3.10
conda activate streamlit
pip install streamlit
```

## データ

```data/result.csv```に実施状況を記載する。  

- デリミタ: ```,```
- ヘッダ: あり
- 文字コード: UTF-8

| name | sequence | correct | incorrect | date |
| --- | --- | --- | --- | --- |
| 資格試験名 | 問題番号 | 正解数 | 不正解数 | 実施日 |

```data/info.json```に問題集の情報を記載する。  

```json
[
    {
        "name": "資格試験名",
        "amount": (問題数)
    },
    {
        "name": "資格試験名",
        "amount": (問題数)
    }
]
```
