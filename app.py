import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from ohto_simulate import compare_tax_by_year, simulate_tax

st.set_page_config(
    page_title="日本の税金シミュレーター（学生向け）",
    page_icon="💴",
    layout="wide",
)

st.title("💴 日本の税金シミュレーター（学生向け）")
st.caption("文京区在住・国民健康保険・国民年金加入を前提に計算します。")


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("📝 入力")

    year = st.selectbox("対象年", [2024, 2025, 2026, 2027], index=1)

    st.subheader("給与収入")
    num_salaries = int(st.number_input("勤務先数", min_value=1, max_value=5, value=1, step=1))
    salaries = []
    for i in range(num_salaries):
        s = st.number_input(
            f"給与収入 {i + 1}（万円）",
            min_value=0.0, max_value=5000.0,
            value=200.0 if i == 0 else 0.0,
            step=1.0,
        )
        salaries.append(s)

    st.subheader("雑所得（副業・フリーランス）")
    zassyotoku_revenue = st.number_input("収入（万円）", 0.0, 5000.0, 0.0, step=1.0)
    zassyotoku_expenses = st.number_input("必要経費（万円）", 0.0, 5000.0, 0.0, step=1.0)
    aoiro = st.checkbox("青色申告特別控除（65万円）を適用する")

    st.subheader("国民年金")
    nenkin_freq = st.selectbox(
        "支払い頻度",
        ["毎月納付", "当月末振替", "6カ月前納", "1年前納", "2年前納"],
        index=3,
    )
    if nenkin_freq == "当月末振替":
        nenkin_method = "口座振替"
        st.caption("当月末振替は口座振替のみ対応")
    else:
        nenkin_method = st.selectbox(
            "支払い方法",
            ["口座振替", "納付書払い", "クレジットカード払い"],
        )

    st.subheader("iDeCo")
    ideco_getsu = st.number_input("月額掛金（万円）", 0.0, 6.8, 0.0, step=0.1)

    fukkou = st.checkbox("復興特別所得税（2.1%）を含める")


# ── 計算 ─────────────────────────────────────────────────────────────────────

result = simulate_tax(
    salaries=salaries,
    zassyotoku_revenue=zassyotoku_revenue,
    zassyotoku_expenses=zassyotoku_expenses,
    year=year,
    nenkin_frequency=nenkin_freq,
    nenkin_method=nenkin_method,
    ideco_getsu=ideco_getsu,
    aoiro_tokubetsu_kojo=aoiro,
    include_fukkou=fukkou,
)

gross = result["給与収入合計"] + result["雑所得収入"]
total_tax = result["所得税額"] + result["住民税額（所得割）"]
total_shakai = result["国保年額（文京区）"] + result["年金年額"]
total_out = total_tax + total_shakai
take_home = gross - result["雑所得経費"] - total_out
effective_rate = (total_out / gross * 100) if gross > 0 else 0.0


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📊 シミュレーション結果", "📈 収入別シミュレーション", "📅 年度比較"])


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1: シミュレーション結果
# ─────────────────────────────────────────────────────────────────────────────

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("総収入", f"{gross:.1f} 万円")
    c2.metric("手取り収入", f"{take_home:.1f} 万円")
    c3.metric("税金 + 社会保険", f"{total_out:.1f} 万円")
    c4.metric("実質負担率", f"{effective_rate:.1f}%")

    st.divider()

    col_wf, col_pie = st.columns(2)

    with col_wf:
        # ウォーターフォールチャート
        expenses_val = result["雑所得経費"]
        wf_x = ["総収入"]
        wf_y = [gross]
        wf_m = ["absolute"]

        if expenses_val > 0:
            wf_x.append("雑所得経費")
            wf_y.append(-expenses_val)
            wf_m.append("relative")

        wf_x += ["国民健康保険", "国民年金", "所得税", "住民税", "手取り"]
        wf_y += [
            -result["国保年額（文京区）"],
            -result["年金年額"],
            -result["所得税額"],
            -result["住民税額（所得割）"],
            take_home,
        ]
        wf_m += ["relative", "relative", "relative", "relative", "total"]

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=wf_m,
            x=wf_x,
            y=wf_y,
            connector={"line": {"color": "#cccccc"}},
            decreasing={"marker": {"color": "#EF5350"}},
            increasing={"marker": {"color": "#42A5F5"}},
            totals={"marker": {"color": "#66BB6A"}},
            text=[f"{abs(v):.1f}万" for v in wf_y],
            textposition="outside",
        ))
        fig_wf.update_layout(
            title="収入・控除の内訳",
            yaxis_title="万円",
            showlegend=False,
            height=400,
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    with col_pie:
        # 支出内訳の円グラフ
        pie_labels = ["手取り", "所得税", "住民税", "国民健康保険", "国民年金"]
        pie_values = [
            max(0.0, take_home),
            result["所得税額"],
            result["住民税額（所得割）"],
            result["国保年額（文京区）"],
            result["年金年額"],
        ]
        fig_pie = go.Figure(go.Pie(
            labels=pie_labels,
            values=pie_values,
            hole=0.45,
            marker_colors=["#66BB6A", "#AB47BC", "#7E57C2", "#EF5350", "#EC407A"],
            textinfo="label+percent",
        ))
        fig_pie.update_layout(
            title="支出の割合",
            height=400,
            margin=dict(t=50, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 詳細テーブル
    st.subheader("詳細内訳")
    detail_rows = [
        ("給与収入合計",       result["給与収入合計"]),
        ("雑所得収入",         result["雑所得収入"]),
        ("雑所得経費",         result["雑所得経費"]),
        ("給与所得合計",       result["給与所得合計"]),
        ("雑所得",             result["雑所得"]),
        ("合計所得金額",       result["合計所得金額"]),
        ("─ 控除 ─",          None),
        ("基礎控除（所得税）", result["基礎控除（所得税）"]),
        ("基礎控除（住民税）", result["基礎控除（住民税）"]),
        ("社会保険料控除",     result["社会保険料控除"]),
        ("iDeCo控除（年額）",  result["iDeCo控除（年額）"]),
        ("青色申告特別控除",   result["青色申告特別控除"]),
        ("─ 課税所得 ─",      None),
        ("課税所得（所得税）", result["課税所得（所得税）"]),
        ("課税所得（住民税）", result["課税所得（住民税）"]),
        ("─ 税額・保険料 ─",  None),
        ("所得税額",           result["所得税額"]),
        ("住民税額（所得割）", result["住民税額（所得割）"]),
        ("国保年額（文京区）", result["国保年額（文京区）"]),
        ("国民年金年額",       result["年金年額"]),
        ("─ まとめ ─",        None),
        ("合計納税額",         result["合計納税額"]),
        ("合計社会保険料",     round(total_shakai, 4)),
        ("手取り収入",         round(take_home, 4)),
    ]
    df_detail = pd.DataFrame(detail_rows, columns=["項目", "金額（万円）"])
    df_detail["金額（万円）"] = df_detail["金額（万円）"].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else ""
    )
    st.dataframe(df_detail, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2: 収入別シミュレーション
# ─────────────────────────────────────────────────────────────────────────────

with tab2:
    st.subheader("収入額に対する手取りの変化")
    st.caption("雑所得・iDeCo・年金設定はサイドバーの値を使用します。給与1社のみ変化させます。")

    max_salary = st.slider("シミュレーション最大収入（万円）", 100, 1000, 400, step=50)

    @st.cache_data
    def compute_salary_range(
        max_sal, rev, exp, yr, nfreq, nmethod, ideco, ao, fk
    ):
        sal_range = np.arange(0, max_sal + 1, 5, dtype=float)
        take_homes, taxes, shakais = [], [], []
        for s in sal_range:
            r = simulate_tax(
                salaries=[s],
                zassyotoku_revenue=rev,
                zassyotoku_expenses=exp,
                year=yr,
                nenkin_frequency=nfreq,
                nenkin_method=nmethod,
                ideco_getsu=ideco,
                aoiro_tokubetsu_kojo=ao,
                include_fukkou=fk,
            )
            g = s + r["雑所得収入"]
            tout = r["所得税額"] + r["住民税額（所得割）"] + r["国保年額（文京区）"] + r["年金年額"]
            take_homes.append(g - r["雑所得経費"] - tout)
            taxes.append(r["所得税額"] + r["住民税額（所得割）"])
            shakais.append(r["国保年額（文京区）"] + r["年金年額"])
        return sal_range, take_homes, taxes, shakais

    sal_range, take_homes, taxes, shakais = compute_salary_range(
        max_salary, zassyotoku_revenue, zassyotoku_expenses,
        year, nenkin_freq, nenkin_method, ideco_getsu, aoiro, fukkou,
    )

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=sal_range, y=sal_range,
        name="収入（参考）",
        line=dict(color="#90A4AE", width=1, dash="dash"),
    ))
    fig_line.add_trace(go.Scatter(
        x=sal_range, y=take_homes,
        name="手取り収入",
        line=dict(color="#66BB6A", width=2.5),
    ))
    fig_line.add_trace(go.Scatter(
        x=sal_range, y=taxes,
        name="税金合計",
        line=dict(color="#AB47BC", width=1.5),
    ))
    fig_line.add_trace(go.Scatter(
        x=sal_range, y=shakais,
        name="社会保険料合計",
        line=dict(color="#EF5350", width=1.5),
    ))

    # 収入の壁
    walls = {"103万の壁": 103, "130万の壁": 130, "160万の壁": 160, "201万の壁": 201}
    for label, xv in walls.items():
        if xv <= max_salary:
            fig_line.add_vline(
                x=xv, line_dash="dot", line_color="#FF9800", line_width=1.2,
                annotation_text=label, annotation_position="top right",
                annotation_font_size=11,
            )

    fig_line.update_layout(
        xaxis_title="給与収入（万円）",
        yaxis_title="金額（万円）",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        height=500,
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig_line, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3: 年度比較
# ─────────────────────────────────────────────────────────────────────────────

with tab3:
    st.subheader("年度別 納税額・手取り比較")

    compare_years = [2024, 2025, 2026, 2027]
    results_by_year = compare_tax_by_year(
        salaries=salaries,
        zassyotoku_revenue=zassyotoku_revenue,
        zassyotoku_expenses=zassyotoku_expenses,
        years=compare_years,
        nenkin_frequency=nenkin_freq,
        nenkin_method=nenkin_method,
        ideco_getsu=ideco_getsu,
        aoiro_tokubetsu_kojo=aoiro,
        include_fukkou=fukkou,
    )

    years_label      = [f"{y}年" for y in compare_years]
    income_tax_vals  = [results_by_year[y]["所得税額"] for y in compare_years]
    juminzei_vals    = [results_by_year[y]["住民税額（所得割）"] for y in compare_years]
    kokuho_vals      = [results_by_year[y]["国保年額（文京区）"] for y in compare_years]
    nenkin_vals      = [results_by_year[y]["年金年額"] for y in compare_years]
    take_home_vals   = []
    for y in compare_years:
        r = results_by_year[y]
        g = r["給与収入合計"] + r["雑所得収入"]
        tout = r["所得税額"] + r["住民税額（所得割）"] + r["国保年額（文京区）"] + r["年金年額"]
        take_home_vals.append(g - r["雑所得経費"] - tout)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="所得税",      x=years_label, y=income_tax_vals, marker_color="#AB47BC"))
    fig_bar.add_trace(go.Bar(name="住民税",      x=years_label, y=juminzei_vals,   marker_color="#7E57C2"))
    fig_bar.add_trace(go.Bar(name="国民健康保険", x=years_label, y=kokuho_vals,     marker_color="#EF5350"))
    fig_bar.add_trace(go.Bar(name="国民年金",    x=years_label, y=nenkin_vals,      marker_color="#EC407A"))
    fig_bar.update_layout(
        barmode="stack",
        yaxis_title="万円",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        height=380,
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    df_compare = pd.DataFrame({
        "年度":          years_label,
        "所得税（万円）": [f"{v:.2f}" for v in income_tax_vals],
        "住民税（万円）": [f"{v:.2f}" for v in juminzei_vals],
        "国保（万円）":   [f"{v:.2f}" for v in kokuho_vals],
        "年金（万円）":   [f"{v:.2f}" for v in nenkin_vals],
        "手取り（万円）": [f"{v:.2f}" for v in take_home_vals],
    })
    st.dataframe(df_compare, use_container_width=True, hide_index=True)
