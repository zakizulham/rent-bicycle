# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set seaborn style
sns.set(style='dark')

# Define the Ddate_df function
def Ddate_df(df):
    # Resample the data frame on a daily basis
    Ddate_df = df.resample(rule='D', on='dteday').agg({
        'casual_x': 'sum',
        'registered_x': 'sum',
        'cnt_x': 'sum'
    })
    # Reset index and rename columns
    Ddate_df = Ddate_df.reset_index()
    Ddate_df.rename(columns={
        'casual_x': 'casual',
        'registered_x': 'anggota',
        "cnt_x": "jumlah_pengguna"
    }, inplace=True)
    
    return Ddate_df

# Load the main_data.csv file
main_data = pd.read_csv("https://github.com/zakizulham/rent-bicycle/blob/main/dashboard/main_data.csv")

# Sort and reset index for main_data
main_data.sort_values(by="dteday", inplace=True)
main_data.reset_index(inplace=True)
 
# Convert 'dteday' column to datetime
main_data['dteday'] = pd.to_datetime(main_data['dteday'])
    
# Sidebar with date filter widget
min_date = main_data['dteday'].min()
max_date = main_data['dteday'].max()

with st.sidebar:
    # Get start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter the data and save it to main_df
    main_df = main_data[(main_data['dteday'] >= str(start_date)) & 
                        (main_data['dteday'] <= str(end_date))]

    # Helper function to generate a visualization DataFrame
    Dteday = Ddate_df(main_df)

# Header and subheaders
st.header('Dicoding Rent Bicycle Dashboard :sparkles:')
st.subheader('Tren Penggunaan Sepeda dalam Beberapa Bulan')

# Metrics in three columns
col1, col2, col3= st.columns(3)

with col1:
    total_peminjam = Dteday.jumlah_pengguna.sum()
    st.metric("Total Pengguna Sepeda", value=total_peminjam)
 
with col2:
    total_registered = Dteday.anggota.sum()
    st.metric("Total Pengguna Terdaftar", value=total_registered)

with col3:
    total_casual = Dteday.casual.sum()
    st.metric("Total Pengguna Casual", value=total_casual)

# Line plot
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    Dteday["dteday"],
    Dteday["jumlah_pengguna"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.plot(
    Dteday["dteday"], 
    Dteday["anggota"], 
    marker='o', 
    linewidth=2, 
    color="#48bf11"
)
ax.plot(
    Dteday["dteday"], 
    Dteday["casual"], 
    marker='o', 
    linewidth=2, 
    color="#1114bf"
)
ax.legend(["Jumlah pengguna", "anggota","casual"], loc="lower right") 
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Pie chart for daily rentals distribution
st.subheader('Visualisasi Pengguna Sepeda Terdaftar dan Casual')

rent_day_df = pd.DataFrame({
    'casual': [Dteday['casual'].sum()],
    'terdaftar': [Dteday['anggota'].sum()]
})

# Convert values to float
rent_day_df = rent_day_df.astype(float)

fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.pie(rent_day_df.iloc[0], labels=rent_day_df.columns, autopct='%1.1f%%', startangle=90)
ax1.set_title('Distribusi Peminjaman Harian')

st.pyplot(fig1)

# Bar plot for bicycle rentals based on holiday and weekday
st.subheader('Visualisasi Peminjaman Sepeda pada Hari Libur dan Hari Biasa')

grouped_rentals = main_df.groupby(['holiday_x', 'weekday_x'])['cnt_x'].sum().unstack()

fig2, ax2 = plt.subplots(figsize=(12, 6))
grouped_rentals.plot(kind='bar', width=0.8, color=['gray', 'orange', 'blue', 'green', 'red', 'purple', 'brown'], ax=ax2)
ax2.set_title('Peminjaman Sepeda Berdasarkan Hari Libur dan Hari Biasa')  
ax2.set_xlabel('Hari Libur / Hari Biasa') 
ax2.set_ylabel('Total Peminjaman')
ax2.legend(['Minggu','Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'], title='Hari')
ax2.set_xticks([0, 1])
ax2.set_xticklabels(['Bukan Hari Libur', 'Hari Libur'], rotation=0)

st.pyplot(fig2)

# Heatmap for average duration of bicycle rentals
st.subheader('Visualisasi Rata-rata Durasi Peminjaman Sepeda')

fig3, ax3 = plt.subplots(figsize=(15, 8))

pivot_table = main_df.pivot_table(values='hr', index=['weekday_x', 'holiday_x', 'workingday_x'], aggfunc='mean')

sns.heatmap(pivot_table, cmap='YlGnBu', annot=True, fmt=".1f", cbar_kws={'label': 'Rata-rata Durasi (jam)'})

ax3.set_title('Rata-rata Durasi Peminjaman Sepeda per Jam, Hari, dan Hari Libur')
ax3.set_xlabel('Jam')
ax3.set_ylabel('Hari / Hari Libur')

st.pyplot(fig3)

# Scatter plot and regression line for temperature correlation
main_df['original_atemp_x'] = main_df['atemp_x'] * 50
main_df['original_atemp_y'] = main_df['atemp_y'] * 50

st.subheader('Visualisasi Korelasi antara Suhu yang Dirasakan dan Banyak Pengguna Sepeda')

col4, col5 = st.columns(2)

with col4:
    fig4, ax4= plt.subplots(figsize=(15, 8))
    sns.scatterplot(x='original_atemp_x', y='cnt_x', data=main_df)
    sns.regplot(x='original_atemp_x', y='cnt_x', data=main_df, ci=None, line_kws={"color": "red"})
    ax4.set_xlabel('Suhu yang Dirasakan (Derajat Celcius)')
    ax4.set_ylabel('Banyak Pengguna Sepeda (Keseluruhan)')
    ax4.set_title('Korelasi antara Suhu yang Dirasakan dan Banyak Pengguna Sepeda berdasarkan Jam', fontsize=20)
    st.pyplot(fig4)

with col5:
    fig5, ax5 = plt.subplots(figsize=(15, 8))
    sns.scatterplot(x='original_atemp_y', y='cnt_y', data=main_df)
    sns.regplot(x='original_atemp_y', y='cnt_y', data=main_df, ci=None, line_kws={"color": "red"})
    ax5.set_xlabel('Suhu yang Dirasakan (Derajat Celcius)')
    ax5.set_ylabel('Banyak Pengguna Sepeda (Keseluruhan)')
    ax5.set_title('Korelasi antara Suhu yang Dirasakan dan Banyak Pengguna Sepeda berdasarkan Hari', fontsize=20)
    st.pyplot(fig5)

# Correlation coefficients
korelasi_jam = main_df['atemp_x'].corr(main_df['cnt_x']) * 100
korelasi_hari = main_df['atemp_y'].corr(main_df['cnt_y']) * 100

# Display correlation coefficients in percentage
st.write(f'Korelasi untuk berdasarkan jam dan banyak pengguna sepeda: {korelasi_jam:.2f}%')
st.write(f'Korelasi untuk berdasarkan hari dan banyak pengguna sepeda: {korelasi_hari:.2f}%')

main_df['original_hum_x'] = main_df['hum_x'] * 100
main_df['original_hum_y'] = main_df['hum_y'] * 100

st.subheader('Visualisasi Korelasi antara Kelembaban dan Banyak Pengguna Sepeda')

col6, col7 = st.columns(2)

with col6:
    fig6, ax6 = plt.subplots(figsize=(15, 8))
    sns.scatterplot(x='original_hum_x', y='cnt_x', data=main_df)
    sns.regplot(x='original_hum_x', y='cnt_x', data=main_df, ci=None, line_kws={"color": "red"})
    ax6.set_xlabel('Kelembaban')
    ax6.set_ylabel('Banyak Pengguna Sepeda (Keseluruhan)')
    ax6.set_title('Korelasi antara Kelembaban dan Banyak Pengguna Sepeda berdasarkan Jam', fontsize=20)
    st.pyplot(fig6)

with col7:
    fig7, ax7 = plt.subplots(figsize=(15, 8))
    sns.scatterplot(x='original_hum_y', y='cnt_y', data=main_df)
    sns.regplot(x='original_hum_y', y='cnt_y', data=main_df, ci=None, line_kws={"color": "red"})
    ax7.set_xlabel('Kelembaban')
    ax7.set_ylabel('Banyak Pengguna Sepeda (Keseluruhan)')
    ax7.set_title('Korelasi antara Kelembaban dan Banyak Pengguna Sepeda berdasarkan Hari', fontsize=20)
    st.pyplot(fig7)

# Correlation coefficients
korelasi_jam = main_df['hum_x'].corr(main_df['cnt_x']) * 100
korelasi_hari = main_df['hum_y'].corr(main_df['cnt_y']) * 100

# Display correlation coefficients in percentage
st.write(f'Korelasi untuk berdasarkan jam dan banyak pengguna sepeda: {korelasi_jam:.2f}%')
st.write(f'Korelasi untuk berdasarkan hari dan banyak pengguna sepeda: {korelasi_hari:.2f}%')
