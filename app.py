import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from src import DEFAULT_INSURED_TYPE, IDECO_MAX_GETSU, KOKUHO_RATES
from src.simulator import SimulationInput, compare_tax_by_year, save_result, simulate_tax

st.set_page_config(
    page_title="日本の税金シミュレーター（学生向け）",
    page_icon="💴",
    layout="wide",
)

st.title("💴 日本の税金シミュレーター（学生向け）")
st.caption("国民健康保険・国民年金加入を前提に計算します。")


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

    if num_salaries > 1:
        main_salary_index = int(st.selectbox(
            "年末調整（甲欄）を受ける勤務先",
            options=list(range(num_salaries)),
            format_func=lambda i: f"給与収入 {i + 1}",
        ))
    else:
        main_salary_index = 0

    st.subheader("雑所得（副業・フリーランス・奨学金等）")
    zassyotoku_revenue = st.number_input("収入（万円）", 0.0, 5000.0, 0.0, step=1.0)
    zassyotoku_expenses = st.number_input("必要経費（万円）", 0.0, 5000.0, 0.0, step=1.0)
    aoiro = st.checkbox("青色申告特別控除（65万円）を適用する")
    scholarship_kyufugata = st.number_input(
        "給付型奨学金（非課税・万円/年）", 0.0, 5000.0, 0.0, step=1.0,
        help="給付型奨学金は所得税法上非課税のため、合計所得金額には含めず手取りにのみ加算します。",
    )

    st.subheader("世帯・社会保険")
    municipality = st.selectbox("自治体（国民健康保険）", list(KOKUHO_RATES.keys()))
    age = st.number_input("年齢", 0, 120, 22, step=1)
    num_persons = int(st.number_input("国民健康保険の被保険者数（世帯人数）", min_value=1, max_value=10, value=1, step=1))
    num_kaigo_persons = int(st.number_input(
        "うち介護分対象者数（40〜64歳）", min_value=0, max_value=num_persons, value=0, step=1,
    ))

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
    insured_type = st.selectbox("被保険者区分", list(IDECO_MAX_GETSU.keys()), index=list(IDECO_MAX_GETSU.keys()).index(DEFAULT_INSURED_TYPE))
    ideco_getsu = st.number_input(
        "月額掛金（万円）", 0.0, IDECO_MAX_GETSU[insured_type], 0.0, step=0.1,
    )

    st.subheader("勤労学生控除")
    is_student = st.checkbox("学校教育法上の学生・生徒に該当する")

    with st.expander("医療費控除 / セルフメディケーション税制"):
        iryouhi_shiharai = st.number_input("年間医療費の支払額（万円）", 0.0, 1000.0, 0.0, step=1.0)
        iryouhi_hoken_hoten = st.number_input("保険金等で補填された額（万円）", 0.0, 1000.0, 0.0, step=1.0)
        otc_shiharai = st.number_input("OTC医薬品の購入額（万円・セルフメディケーション税制）", 0.0, 100.0, 0.0, step=0.5)

    with st.expander("生命保険料控除 / 地震保険料控除"):
        seimei_hoken_ippan = st.number_input("一般生命保険料（年間支払額・万円）", 0.0, 100.0, 0.0, step=0.5)
        seimei_hoken_kaigo_iryou = st.number_input("介護医療保険料（年間支払額・万円）", 0.0, 100.0, 0.0, step=0.5)
        seimei_hoken_kojin_nenkin = st.number_input("個人年金保険料（年間支払額・万円）", 0.0, 100.0, 0.0, step=0.5)
        jishin_hoken = st.number_input("地震保険料（年間支払額・万円）", 0.0, 100.0, 0.0, step=0.5)

    with st.expander("ふるさと納税"):
        furusato_kifu = st.number_input("年間寄附額（万円）", 0.0, 100.0, 0.0, step=0.5)
        st.caption("ワンストップ特例を使わず確定申告する前提で計算します。")

    with st.expander("配偶者控除"):
        has_spouse = st.checkbox("配偶者がいる")
        spouse_income = st.number_input("配偶者の合計所得金額（万円）", 0.0, 1000.0, 0.0, step=1.0) if has_spouse else None

    fukkou = st.checkbox("復興特別所得税（2.1%）を含める")


# ── 計算 ─────────────────────────────────────────────────────────────────────

base_input = SimulationInput(
    salaries=salaries,
    main_salary_index=main_salary_index,
    zassyotoku_revenue=zassyotoku_revenue,
    zassyotoku_expenses=zassyotoku_expenses,
    aoiro_tokubetsu_kojo=aoiro,
    scholarship_kyufugata=scholarship_kyufugata,
    year=year,
    include_fukkou=fukkou,
    municipality=municipality,
    num_persons=num_persons,
    age=age,
    num_kaigo_persons=num_kaigo_persons,
    nenkin_frequency=nenkin_freq,
    nenkin_method=nenkin_method,
    ideco_getsu=ideco_getsu,
    insured_type=insured_type,
    is_student=is_student,
    iryouhi_shiharai=iryouhi_shiharai,
    iryouhi_hoken_hoten=iryouhi_hoken_hoten,
    otc_shiharai=otc_shiharai,
    seimei_hoken_ippan=seimei_hoken_ippan,
    seimei_hoken_kaigo_iryou=seimei_hoken_kaigo_iryou,
    seimei_hoken_kojin_nenkin=seimei_hoken_kojin_nenkin,
    jishin_hoken=jishin_hoken,
    furusato_kifu=furusato_kifu,
    spouse_gokei_shotoku=spouse_income,
)

try:
    result = simulate_tax(base_input)
except ValueError as e:
    st.error(f"入力値にエラーがあります: {e}")
    st.stop()

summary = result["サマリー"]
gross = summary["総収入（非課税収入含む）"]
take_home = summary["手取り収入"]
total_tax = result["所得税額"] + result["住民税額（所得割）"]
total_shakai = result["社会保険料控除"]
total_out = total_tax + total_shakai
effective_rate = summary["実効負担率(%)"]


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(["📊 シミュレーション結果", "📈 収入別シミュレーション", "📈 経費別シミュレーション", "📅 年度比較"])


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1: シミュレーション結果
# ─────────────────────────────────────────────────────────────────────────────

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("総収入（非課税含む）", f"{gross:.1f} 万円")
    c2.metric("手取り収入", f"{take_home:.1f} 万円")
    c3.metric("税金 + 社会保険", f"{total_out:.1f} 万円")
    c4.metric("実質負担率", f"{effective_rate:.1f}%")

    kanpu = result["還付追納"]
    if kanpu["還付額"] > 0:
        st.success(f"確定申告での還付見込み額: 約 {kanpu['還付額']:.2f} 万円（源泉徴収額 {kanpu['源泉徴収額合計']:.2f} 万円 − 算出所得税額 {kanpu['算出所得税額']:.2f} 万円）")
    elif kanpu["追納額"] > 0:
        st.warning(f"確定申告での追納見込み額: 約 {kanpu['追納額']:.2f} 万円")

    fuyou = result["扶養判定"]
    if fuyou["扶養対象"]:
        st.info(
            f"合計所得金額が{fuyou['所得要件（合計所得金額）']:.0f}万円以下のため、"
            f"親などの扶養親族（{fuyou['区分']}）の所得要件を満たしています。"
            f"（親の控除額の目安: 所得税 {fuyou['親が受けられる扶養控除額（所得税）']:.0f}万円 / "
            f"住民税 {fuyou['親が受けられる扶養控除額（住民税）']:.0f}万円）"
        )
    else:
        st.caption(f"合計所得金額が{fuyou['所得要件（合計所得金額）']:.0f}万円を超えているため、扶養親族の所得要件から外れています。")

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
            -result["国民健康保険"]["総保険料（年額）"],
            -result["国民年金"]["年換算額（万円）"],
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
            result["国民健康保険"]["総保険料（年額）"],
            result["国民年金"]["年換算額（万円）"],
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
        ("非課税収入（給付型奨学金）", result["奨学金内訳"]["非課税収入（給付型奨学金）"]),
        ("雑所得経費",         result["雑所得経費"]),
        ("給与所得合計",       result["給与所得合計"]),
        ("雑所得",             result["雑所得"]),
        ("合計所得金額",       result["合計所得金額"]),
        ("─ 所得控除 ─",      None),
        ("基礎控除（所得税）", result["基礎控除（所得税）"]),
        ("基礎控除（住民税）", result["基礎控除（住民税）"]),
        ("社会保険料控除",     result["社会保険料控除"]),
        ("iDeCo控除（年額）",  result["iDeCo控除（年額）"]),
        ("青色申告特別控除",   result["青色申告特別控除"]),
        ("勤労学生控除（所得税）", result["勤労学生控除"]["控除額（所得税）"]),
        ("勤労学生控除（住民税）", result["勤労学生控除"]["控除額（住民税）"]),
        ("医療費控除等（所得税・住民税共通）", result["医療費控除"]["控除額"]),
        ("生命保険料控除（所得税）", result["生命保険料控除"]["所得税"]),
        ("生命保険料控除（住民税）", result["生命保険料控除"]["住民税"]),
        ("地震保険料控除（所得税）", result["地震保険料控除"]["所得税"]),
        ("地震保険料控除（住民税）", result["地震保険料控除"]["住民税"]),
        ("配偶者控除（所得税）", result["配偶者控除"]["所得税"]),
        ("配偶者控除（住民税）", result["配偶者控除"]["住民税"]),
        ("─ 課税所得 ─",      None),
        ("課税所得（所得税）", result["課税所得（所得税）"]),
        ("課税所得（住民税）", result["課税所得（住民税）"]),
        ("調整控除（住民税）", result["調整控除（住民税）"]),
        ("─ 税額控除（ふるさと納税）─", None),
        ("ふるさと納税控除（所得税）", result["ふるさと納税控除"]["所得税控除額"]),
        ("ふるさと納税控除（住民税・基本分）", result["ふるさと納税控除"]["住民税控除額（基本分）"]),
        ("ふるさと納税控除（住民税・特例分）", result["ふるさと納税控除"]["住民税控除額（特例分）"]),
        ("─ 税額・保険料 ─",  None),
        ("所得税額",           result["所得税額"]),
        ("住民税額（所得割）", result["住民税額（所得割）"]),
        ("国保年額",           result["国民健康保険"]["総保険料（年額）"]),
        ("国民年金年額",       result["国民年金"]["年換算額（万円）"]),
        ("─ 還付・追納（概算）─", None),
        ("源泉徴収額合計（概算）", result["源泉徴収"]["合計"]),
        ("還付見込額",         result["還付追納"]["還付額"]),
        ("追納見込額",         result["還付追納"]["追納額"]),
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

    if result["国民健康保険"]["概算フラグ"] or result["国民年金"]["概算フラグ"]:
        st.caption("※ 対象年度の保険料率データが無いため、最新の既知年度のレートで概算しています。")

    st.divider()

    # 結果の保存（CLIの --save と同様に ./output に保存する）
    st.subheader("結果の保存")
    save_col1, save_col2, save_col3 = st.columns([2, 1, 1])
    with save_col1:
        save_label = st.text_input("ラベル（ファイル名のプレフィックス）", value="app")
    with save_col2:
        save_fmt = st.selectbox("保存形式", ["both", "json", "csv"], index=0)
    with save_col3:
        st.write("")
        st.write("")
        if st.button("./output に保存する"):
            saved_paths = save_result(result, output_dir="./output", label=save_label, fmt=save_fmt)
            for path in saved_paths.values():
                st.success(f"保存しました: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2: 収入別シミュレーション
# ─────────────────────────────────────────────────────────────────────────────

with tab2:
    st.subheader("収入額に対する手取りの変化")
    st.caption("給与1社目（年末調整あり）のみ変化させます。それ以外の設定はサイドバーの値を使用します。")

    max_salary = st.slider("シミュレーション最大収入（万円）", 100, 1000, 400, step=50)

    @st.cache_data
    def compute_salary_range(max_sal: float, base: SimulationInput):
        sal_range = np.arange(0, max_sal + 1, 5, dtype=float)
        take_homes, taxes, shakais = [], [], []
        for s in sal_range:
            other_salaries = list(base.salaries[1:])
            inp = SimulationInput(**{**base.__dict__, "salaries": [s, *other_salaries]})
            r = simulate_tax(inp)
            sm = r["サマリー"]
            take_homes.append(sm["手取り収入"])
            taxes.append(r["所得税額"] + r["住民税額（所得割）"])
            shakais.append(r["社会保険料控除"])
        return sal_range, take_homes, taxes, shakais

    sal_range, take_homes, taxes, shakais = compute_salary_range(max_salary, base_input)

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
    kyuyo_kojo_min = 65 if year >= 2025 else 55
    fuyou_gendo = 58 if year >= 2025 else 48
    walls = {
        "103万の壁": 103,
        "130万の壁": 130,
        "160万の壁": 160,
        "201万の壁": 201,
        f"扶養の目安（合計所得{fuyou_gendo}万円）": fuyou_gendo + kyuyo_kojo_min,
    }
    for label, xv in walls.items():
        if xv <= max_salary:
            fig_line.add_vline(
                x=xv, line_dash="dot", line_color="#FF9800", line_width=1.2,
                annotation_text=label, annotation_position="top right",
                annotation_font_size=11,
            )

    fig_line.update_layout(
        xaxis_title="給与収入（万円・1社目）",
        yaxis_title="金額（万円）",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        height=500,
        margin=dict(t=30, b=20),
    )
    st.plotly_chart(fig_line, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3: 経費別シミュレーション
# ─────────────────────────────────────────────────────────────────────────────

with tab3:
    st.subheader("経費の増加に対する手取り・税金等の変化")
    st.caption("雑所得（副業・フリーランス・奨学金等）の必要経費のみを変化させます。それ以外の設定はサイドバーの値で固定します。")

    if base_input.zassyotoku_revenue == 0.0:
        st.warning("現在、サイドバーで入力されている「雑所得の収入」が0万円です。経費による影響をシミュレーションするには、サイドバーの「雑所得」の「収入（万円）」に値を入力してください。")
    else:
        max_expenses = st.slider(
            "シミュレーション最大経費（万円）",
            min_value=1.0,
            max_value=max(10.0, float(base_input.zassyotoku_revenue * 1.5)),
            value=float(base_input.zassyotoku_revenue),
            step=1.0,
            help="必要経費をどこまで増やしてシミュレーションするかを設定します。"
        )

        @st.cache_data
        def compute_expense_range(max_exp: float, base: SimulationInput):
            step = 0.5 if max_exp <= 50.0 else (1.0 if max_exp <= 200.0 else 5.0)
            exp_range = np.arange(0, max_exp + step, step, dtype=float)
            take_homes, taxes, shakais, total_incomes = [], [], [], []
            
            for exp in exp_range:
                inp = SimulationInput(**{**base.__dict__, "zassyotoku_expenses": exp})
                r = simulate_tax(inp)
                sm = r["サマリー"]
                take_homes.append(sm["手取り収入"])
                taxes.append(r["所得税額"] + r["住民税額（所得割）"])
                shakais.append(r["社会保険料控除"])
                total_incomes.append(r["合計所得金額"])
            return exp_range, take_homes, taxes, shakais, total_incomes

        exp_range, take_homes, taxes, shakais, total_incomes = compute_expense_range(max_expenses, base_input)

        fig_exp = go.Figure()
        
        # 総収入
        fig_exp.add_trace(go.Scatter(
            x=exp_range, y=[gross] * len(exp_range),
            name="総収入（参考）",
            line=dict(color="#90A4AE", width=1, dash="dash"),
        ))
        
        fig_exp.add_trace(go.Scatter(
            x=exp_range, y=take_homes,
            name="手取り収入",
            line=dict(color="#66BB6A", width=2.5),
        ))
        
        fig_exp.add_trace(go.Scatter(
            x=exp_range, y=taxes,
            name="税金合計（所得税＋住民税）",
            line=dict(color="#AB47BC", width=1.5),
        ))
        
        fig_exp.add_trace(go.Scatter(
            x=exp_range, y=shakais,
            name="社会保険料合計（国保＋年金）",
            line=dict(color="#EF5350", width=1.5),
        ))
        
        fig_exp.add_trace(go.Scatter(
            x=exp_range, y=total_incomes,
            name="合計所得金額",
            line=dict(color="#29B6F6", width=1.5, dash="dash"),
        ))

        # 雑所得の収入額のライン
        if base_input.zassyotoku_revenue <= max_expenses:
            fig_exp.add_vline(
                x=base_input.zassyotoku_revenue, line_dash="dash", line_color="#E0E0E0", line_width=1.2,
                annotation_text="雑所得の収入額", annotation_position="top left",
                annotation_font_size=11,
            )

        # 扶養判定の閾値
        fuyou_gendo = result["扶養判定"]["所得要件（合計所得金額）"]
        kyuyo_shotoku_total = result["給与所得合計"]
        target_zasso = fuyou_gendo - kyuyo_shotoku_total
        
        if target_zasso >= 0:
            aoiro_val = 65.0 if base_input.aoiro_tokubetsu_kojo else 0.0
            border_expense = base_input.zassyotoku_revenue - aoiro_val - target_zasso
            if border_expense > 0 and border_expense <= max_expenses:
                fig_exp.add_vline(
                    x=border_expense, line_dash="dot", line_color="#FF9800", line_width=1.5,
                    annotation_text=f"扶養適用ライン（経費{border_expense:.1f}万以上）", annotation_position="top right",
                    annotation_font_size=11,
                )
            elif border_expense <= 0:
                fig_exp.add_annotation(
                    text="経費0でも扶養要件を満たしています",
                    xref="paper", yref="paper",
                    x=0.02, y=0.95, showarrow=False,
                    font=dict(size=11, color="#4CAF50"),
                    bgcolor="#E8F5E9",
                )

        fig_exp.update_layout(
            xaxis_title="雑所得の必要経費（万円）",
            yaxis_title="金額（万円）",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            height=500,
            margin=dict(t=30, b=20),
        )
        st.plotly_chart(fig_exp, use_container_width=True)
        
        st.info("💡 雑所得は、収入から経費（および青色申告特別控除）を引いた額がプラスの場合にのみ課税対象となります。そのため、経費を増やすことで合計所得金額が下がり、所得税・住民税・国民健康保険料が減少します。結果として手取りの減少が穏やかになります。また、合計所得金額が扶養の基準以下になると、親などの扶養に入ることができるため、世帯全体での税負担軽減効果が得られます。")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4: 年度比較
# ─────────────────────────────────────────────────────────────────────────────

with tab4:
    st.subheader("年度別 納税額・手取り比較")

    compare_years = [2024, 2025, 2026, 2027]
    results_by_year = compare_tax_by_year(base_input, years=compare_years)

    years_label      = [f"{y}年" for y in compare_years]
    income_tax_vals  = [results_by_year[y]["所得税額"] for y in compare_years]
    juminzei_vals    = [results_by_year[y]["住民税額（所得割）"] for y in compare_years]
    kokuho_vals      = [results_by_year[y]["国民健康保険"]["総保険料（年額）"] for y in compare_years]
    nenkin_vals      = [results_by_year[y]["国民年金"]["年換算額（万円）"] for y in compare_years]
    take_home_vals   = [results_by_year[y]["サマリー"]["手取り収入"] for y in compare_years]

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

    if any(results_by_year[y]["国民健康保険"]["概算フラグ"] or results_by_year[y]["国民年金"]["概算フラグ"] for y in compare_years):
        st.caption("※ 保険料率データが無い年度は、最新の既知年度のレートで概算しています。")
