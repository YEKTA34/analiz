import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import io
from datetime import datetime, timedelta

# ----------------- Sayfa Ayarı -----------------
st.set_page_config(page_title="FLO Kampanya Paneli", layout="wide")

st.markdown("""
<style>
.metric-box {
    background-color: #2c3e50;
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
    transition: transform 0.3s, box-shadow 0.3s;
}
.metric-box:hover {
    transform: scale(1.05);
    box-shadow: 4px 4px 15px rgba(0,0,0,0.5);
}
.metric-label {
    font-size: 16px;
    color: white;
}
.metric-value {
    font-size: 22px;
    font-weight: bold;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 FLO Kampanya Analiz ve Optimizasyon Paneli")

# ----------------- Örnek Veri Oluştur -----------------
kampanya_tipi = ["İndirim", "Yeni Ürün", "Sezonluk", "Sadakat"]
sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]

data = []
for i in range(50):
    kampanya = f"Kampanya {i+1}"
    tip = random.choice(kampanya_tipi)
    sehir = random.choice(sehirler)
    baslangic = datetime(2025, random.randint(1,8), random.randint(1,28))
    bitis = baslangic + timedelta(days=random.randint(7,30))
    harcama = random.randint(5000,50000)
    satis = random.randint(10000,100000)
    data.append([kampanya, tip, sehir, baslangic, bitis, harcama, satis])

df = pd.DataFrame(data, columns=["Kampanya","Tip","Şehir","Başlangıç","Bitiş","Harcama","Satış"])
df["ROI"] = df["Satış"] / df["Harcama"]

# ----------------- Sidebar Filtreler -----------------
st.sidebar.header("Filtreler")
tarih_baslangic = st.sidebar.date_input("Başlangıç Tarihi", df["Başlangıç"].min())
tarih_bitis = st.sidebar.date_input("Bitiş Tarihi", df["Bitiş"].max())
selected_tip = st.sidebar.multiselect("Kampanya Tipi", kampanya_tipi, default=kampanya_tipi)
selected_sehir = st.sidebar.multiselect("Şehir", sehirler, default=sehirler)

# Filtrelenmiş DataFrame
df_filtered = df[(df["Başlangıç"] >= pd.to_datetime(tarih_baslangic)) &
                 (df["Bitiş"] <= pd.to_datetime(tarih_bitis)) &
                 (df["Tip"].isin(selected_tip)) &
                 (df["Şehir"].isin(selected_sehir))]

# ----------------- Özet Kartlar -----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class='metric-box'><div class='metric-label'>📊 Toplam Kampanya</div><div class='metric-value'>{df_filtered.shape[0]}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='metric-box'><div class='metric-label'>💰 Toplam Harcama</div><div class='metric-value'>{df_filtered['Harcama'].sum():,.0f} TL</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class='metric-box'><div class='metric-label'>🛒 Toplam Satış</div><div class='metric-value'>{df_filtered['Satış'].sum():,.0f} TL</div></div>""", unsafe_allow_html=True)
with col4:
    roi_toplam = (df_filtered['Satış'].sum()/df_filtered['Harcama'].sum()) if df_filtered['Harcama'].sum()>0 else 0
    st.markdown(f"""<div class='metric-box'><div class='metric-label'>📈 Toplam ROI</div><div class='metric-value'>{roi_toplam:.2f}</div></div>""", unsafe_allow_html=True)

# ----------------- Kampanya Bazlı Grafik -----------------
st.subheader("Kampanya Bazlı Performans")
fig1 = px.bar(df_filtered, x="Kampanya", y=["Harcama","Satış"], barmode='group', color_discrete_map={"Harcama":"#e74c3c","Satış":"#27ae60"})
fig1.update_traces(marker_line_width=1.5, marker_line_color="black", opacity=0.85)
st.plotly_chart(fig1, use_container_width=True)

# ----------------- ROI Grafiği -----------------
st.subheader("ROI Karşılaştırması")
fig2 = px.bar(df_filtered, x="Kampanya", y="ROI", color="Tip", color_discrete_sequence=px.colors.qualitative.Bold)
fig2.update_traces(marker_line_width=1.5, marker_line_color="black", opacity=0.85)
st.plotly_chart(fig2, use_container_width=True)

# ----------------- Segment Bazlı Analiz -----------------
st.subheader("Şehir Bazlı Performans")
segment_df = df_filtered.groupby("Şehir").agg({"Harcama":"sum","Satış":"sum","ROI":"mean"}).reset_index()
fig3 = px.bar(segment_df, x="Şehir", y=["Harcama","Satış"], barmode='group', color_discrete_sequence=['#e74c3c','#27ae60'])
fig3.update_traces(marker_line_width=1.5, marker_line_color="black", opacity=0.85)
st.plotly_chart(fig3, use_container_width=True)

# ----------------- Düşük ROI Kampanyaları -----------------
st.subheader("⚠️ Düşük ROI Kampanyaları")
dusuk_roi_df = df_filtered[df_filtered["ROI"] < 1]
st.dataframe(dusuk_roi_df[['Kampanya','Tip','Şehir','Harcama','Satış','ROI']], use_container_width=True)

# ----------------- Detaylı Tablo -----------------
st.subheader("📋 Detaylı Kampanya Listesi")
st.dataframe(df_filtered, use_container_width=True)

# ----------------- Rapor İndirme -----------------
st.subheader("💾 Rapor İndir")

# Excel indirme
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_filtered.to_excel(writer, index=False, sheet_name='Kampanya')
processed_data = output.getvalue()

st.download_button(
    label="Excel Olarak İndir",
    data=processed_data,
    file_name='kampanya_raporu.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# CSV indirme
csv_file = df_filtered.to_csv(index=False)
st.download_button(
    label="CSV Olarak İndir",
    data=csv_file,
    file_name='kampanya_raporu.csv',
    mime='text/csv'
)
