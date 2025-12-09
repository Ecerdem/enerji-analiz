"""
Enerji Tüketim Görselleştirme Modülü
Plotly kullanarak interaktif grafikler ve analizler oluşturur.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict


class EnergyVisualizer:
    """
    Enerji verilerini görselleştiren sınıf.
    Plotly ile interaktif grafikler oluşturur.
    """
    
    def __init__(self):
        """Görselleştirici başlat"""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8'
        }
    
    def plot_consumption_trend(self, df: pd.DataFrame) -> go.Figure:
        """
        Aylık tüketim trend grafiği oluştur

        Args:
            df: Tüketim verilerini içeren DataFrame

        Returns:
            Plotly Figure objesi
        """
        # Aylık bazda gruplama - accrual_term_id bazında unique toplam
        df_unique = df.drop_duplicates(subset=['accrual_term_id'])

        # NaN ve null değerleri temizle
        df_unique = df_unique[df_unique['total_consumption'].notna()]
        df_unique = df_unique[df_unique['year'].notna()]
        df_unique = df_unique[df_unique['month'].notna()]

        monthly = df_unique.groupby(['year', 'month'])['total_consumption'].sum().reset_index()

        # Negatif ve sıfır değerleri filtrele
        monthly = monthly[monthly['total_consumption'] > 0]

        if len(monthly) == 0:
            # Veri yoksa boş grafik döndür
            fig = go.Figure()
            fig.add_annotation(
                text="Gösterilecek veri bulunamadı",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='Enerji Tüketim Trendi (Aylık Veriler)',
                xaxis_title='Tarih',
                yaxis_title='Tüketim (kWh)',
                template='plotly_white',
                height=500
            )
            return fig

        # Tarih sütunu oluştur ve sırala
        monthly['date'] = pd.to_datetime(monthly[['year', 'month']].assign(day=1))
        monthly = monthly.sort_values('date')

        # Outlier tespiti (isteğe bağlı - çok aşırı değerleri işaretle)
        Q1 = monthly['total_consumption'].quantile(0.25)
        Q3 = monthly['total_consumption'].quantile(0.75)
        IQR = Q3 - Q1
        outlier_threshold = Q3 + 3 * IQR

        # Grafik oluştur
        fig = go.Figure()

        # Normal değerler
        normal_data = monthly[monthly['total_consumption'] <= outlier_threshold]
        if len(normal_data) > 0:
            fig.add_trace(go.Scatter(
                x=normal_data['date'],
                y=normal_data['total_consumption'],
                mode='lines+markers',
                name='Tüketim',
                line=dict(color=self.color_scheme['primary'], width=3),
                marker=dict(size=8),
                hovertemplate='<b>Tarih:</b> %{x|%B %Y}<br>' +
                             '<b>Tüketim:</b> %{y:,.0f} kWh<br>' +
                             '<extra></extra>'
            ))

        # Outlier değerler gösterilmiyor (temiz görünüm için filtrelendi)

        # Trend çizgisi ekle (sadece normal değerlerden, en az 3 nokta varsa)
        if len(normal_data) >= 3:
            z = np.polyfit(range(len(normal_data)), normal_data['total_consumption'], 1)
            p = np.poly1d(z)

            fig.add_trace(go.Scatter(
                x=normal_data['date'],
                y=p(range(len(normal_data))),
                mode='lines',
                name='Trend',
                line=dict(color=self.color_scheme['danger'], width=2, dash='dash'),
                hovertemplate='<b>Trend:</b> %{y:,.0f} kWh<br><extra></extra>'
            ))

        fig.update_layout(
            title='Enerji Tüketim Trendi',
            xaxis_title='Tarih',
            yaxis_title='Tüketim (kWh)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig
    
    def plot_cost_analysis(self, df: pd.DataFrame) -> go.Figure:
        """
        Maliyet analizi grafiği oluştur

        Args:
            df: Maliyet verilerini içeren DataFrame

        Returns:
            Plotly Figure objesi
        """
        # Aylık bazda gruplama - accrual_term_id bazında unique toplam
        df_unique = df.drop_duplicates(subset=['accrual_term_id'])

        # NaN değerleri temizle
        df_unique = df_unique[df_unique['year'].notna()]
        df_unique = df_unique[df_unique['month'].notna()]

        # term_total_cost varsa onu kullan
        cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'

        # Gerekli sütunların varlığını kontrol et
        if cost_column not in df_unique.columns:
            # Boş grafik döndür
            fig = go.Figure()
            fig.add_annotation(
                text=f"Gerekli sütun bulunamadı: {cost_column}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            fig.update_layout(
                title='Aylık Maliyet Analizi',
                template='plotly_white',
                height=500
            )
            return fig

        monthly = df_unique.groupby(['year', 'month']).agg({
            cost_column: 'sum'
        }).reset_index()

        # Sütun isimlerini standardize et
        monthly.rename(columns={cost_column: 'total_cost'}, inplace=True)

        # Negatif değerleri 0'a çek
        monthly['total_cost'] = monthly['total_cost'].clip(lower=0)

        # Boş değerleri filtrele
        monthly = monthly[monthly['total_cost'] > 0]

        if len(monthly) == 0:
            # Veri yoksa boş grafik döndür
            fig = go.Figure()
            fig.add_annotation(
                text="Gösterilecek maliyet verisi bulunamadı",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='Aylık Maliyet Analizi',
                xaxis_title='Tarih',
                yaxis_title='Tutar (TL)',
                template='plotly_white',
                height=500
            )
            return fig

        # Tarih sütunu oluştur ve sırala
        monthly['date'] = pd.to_datetime(monthly[['year', 'month']].assign(day=1))
        monthly = monthly.sort_values('date')

        # Grafik oluştur
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=monthly['date'],
            y=monthly['total_cost'],
            name='Toplam Maliyet',
            marker_color=self.color_scheme['primary'],
            hovertemplate='<b>Maliyet:</b> ₺%{y:,.2f}<br><extra></extra>'
        ))

        # Trend çizgisi ekle (doğru trend hesaplama)
        if len(monthly) >= 3:
            z = np.polyfit(range(len(monthly)), monthly['total_cost'], 1)
            p = np.poly1d(z)

            fig.add_trace(go.Scatter(
                x=monthly['date'],
                y=p(range(len(monthly))),
                name='Trend',
                mode='lines',
                line=dict(color=self.color_scheme['danger'], width=2, dash='dash'),
                hovertemplate='<b>Trend:</b> ₺%{y:,.2f}<br><extra></extra>'
            ))

        fig.update_layout(
            title='Aylık Maliyet Analizi (KDV Hariç)',
            xaxis_title='Tarih',
            yaxis_title='Tutar (₺)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig

    def plot_yearly_comparison(self, df: pd.DataFrame) -> go.Figure:
        """
        Yıllık karşılaştırma grafiği

        Args:
            df: Yıllık verileri içeren DataFrame

        Returns:
            Plotly Figure objesi
        """
        # Yıllık toplam tüketim ve maliyet - unique term bazında
        df_unique = df.drop_duplicates(subset=['accrual_term_id'])

        # NaN değerleri temizle
        df_unique = df_unique[df_unique['year'].notna()]

        # term_total_cost varsa onu kullan, yoksa amount kullan
        cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'

        # DEBUG: Hangi sütun kullanılıyor?
        print(f"[GRAFIK DEBUG] Kullanilan maliyet sutunu: {cost_column}")
        print(f"[GRAFIK DEBUG] Mevcut sutunlar: {df_unique.columns.tolist()}")

        # Gerekli sütunları kontrol et
        if 'total_consumption' not in df_unique.columns or cost_column not in df_unique.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Gerekli veri sütunları bulunamadı",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            fig.update_layout(
                title='Yıllık Tüketim ve Maliyet Karşılaştırması',
                template='plotly_white',
                height=500
            )
            return fig

        yearly = df_unique.groupby('year').agg({
            'total_consumption': 'sum',
            cost_column: 'sum'
        }).reset_index()

        # Sütun isimlerini standardize et
        yearly.rename(columns={cost_column: 'total_cost'}, inplace=True)

        # Negatif değerleri temizle
        yearly['total_consumption'] = yearly['total_consumption'].clip(lower=0)
        yearly['total_cost'] = yearly['total_cost'].clip(lower=0)

        # Boş değerleri filtrele
        yearly = yearly[(yearly['total_consumption'] > 0) | (yearly['total_cost'] > 0)]

        if len(yearly) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Gösterilecek yıllık veri bulunamadı",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='Yıllık Tüketim ve Maliyet Karşılaştırması',
                template='plotly_white',
                height=500
            )
            return fig

        # Yılları sırala
        yearly = yearly.sort_values('year')

        # Yıl-yıl değişim oranını hesapla
        yearly['consumption_change'] = yearly['total_consumption'].pct_change() * 100
        yearly['cost_change'] = yearly['total_cost'].pct_change() * 100

        # İki Y eksenli grafik oluştur
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Tüketim (sol Y ekseni) - değişim oranına göre renklendirme
        colors = []
        for _, row in yearly.iterrows():
            if pd.notna(row['consumption_change']):
                if row['consumption_change'] > 0:
                    colors.append(self.color_scheme['danger'])  # Artış kırmızı
                else:
                    colors.append(self.color_scheme['success'])  # Azalış yeşil
            else:
                colors.append(self.color_scheme['primary'])  # İlk yıl mavi

        fig.add_trace(
            go.Bar(
                x=yearly['year'].astype(int),
                y=yearly['total_consumption'],
                name='Tüketim',
                marker_color=colors,
                text=[f"{change:+.1f}%" if pd.notna(change) else "İlk Yıl"
                      for change in yearly['consumption_change']],
                textposition='outside',
                hovertemplate='<b>Yıl:</b> %{x}<br>' +
                             '<b>Tüketim:</b> %{y:,.0f} kWh<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )

        # Maliyet (sağ Y ekseni) - KDV Hariç
        fig.add_trace(
            go.Scatter(
                x=yearly['year'].astype(int),
                y=yearly['total_cost'],
                name='Maliyet (KDV Hariç)',
                mode='lines+markers',
                line=dict(color=self.color_scheme['warning'], width=3),
                marker=dict(size=12),
                hovertemplate='<b>Yıl:</b> %{x}<br>' +
                             '<b>Maliyet:</b> ₺%{y:,.2f}<br>' +
                             '<extra></extra>'
            ),
            secondary_y=True
        )

        fig.update_xaxes(
            title_text="Yıl",
            dtick=1,  # Her yıl göster
            type='linear'
        )
        fig.update_yaxes(title_text="Tüketim (kWh)", secondary_y=False)
        fig.update_yaxes(title_text="Maliyet (TL)", secondary_y=True)

        fig.update_layout(
            title='Yıllık Tüketim ve Maliyet Karşılaştırması',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )

        return fig
    
    def plot_monthly_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """
        Aylık tüketim ısı haritası

        Args:
            df: Aylık verileri içeren DataFrame

        Returns:
            Plotly Figure objesi
        """
        # Unique term bazında pivot tablo oluştur (yıl x ay)
        df_unique = df.drop_duplicates(subset=['accrual_term_id'])
        pivot = df_unique.pivot_table(
            values='total_consumption',
            index='year',
            columns='month',
            aggfunc='sum',
            fill_value=0
        )

        # Tüm 12 ayı garanti et (eksik ayları 0 ile doldur)
        all_months = list(range(1, 13))
        pivot = pivot.reindex(columns=all_months, fill_value=0)

        # Ay isimlerini ekle
        month_names = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz',
                      'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']

        # Değerleri text olarak hazırla (0'ları gösterme)
        text_values = []
        for row in pivot.values:
            text_row = []
            for val in row:
                if val > 0:
                    text_row.append(f'{val:,.0f}')
                else:
                    text_row.append('')
            text_values.append(text_row)

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=month_names,
            y=pivot.index.astype(int),
            text=text_values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorscale='YlOrRd',  # Sarı-Turuncu-Kırmızı (düşük-orta-yüksek)
            hovertemplate='<b>Yıl:</b> %{y}<br>' +
                         '<b>Ay:</b> %{x}<br>' +
                         '<b>Tüketim:</b> %{z:,.0f} kWh<br>' +
                         '<extra></extra>',
            colorbar=dict(
                title="Tüketim (kWh)"
            ),
            zmin=0  # Minimum değeri 0'dan başlat
        ))

        fig.update_layout(
            title='Aylık Tüketim Isı Haritası',
            xaxis_title='Ay',
            yaxis_title='Yıl',
            template='plotly_white',
            height=500,
            xaxis=dict(side='bottom'),
            yaxis=dict(autorange='reversed')  # Yılları yukarıdan aşağıya sırala
        )

        return fig
    
    def plot_prediction_vs_actual(self, comparison_df: pd.DataFrame) -> go.Figure:
        """
        Tahmin vs Gerçek karşılaştırma grafiği
        
        Args:
            comparison_df: Karşılaştırma verilerini içeren DataFrame
            
        Returns:
            Plotly Figure objesi
        """
        fig = go.Figure()
        
        # Gerçek değerler
        fig.add_trace(go.Scatter(
            x=comparison_df['Tarih'],
            y=comparison_df['Gercek_Tuketim'],
            mode='lines+markers',
            name='Gerçek Tüketim',
            line=dict(color=self.color_scheme['primary'], width=3),
            marker=dict(size=8)
        ))
        
        # Tahmin değerleri
        fig.add_trace(go.Scatter(
            x=comparison_df['Tarih'],
            y=comparison_df['Tahmin_Tuketim'],
            mode='lines+markers',
            name='Tahmin',
            line=dict(color=self.color_scheme['danger'], width=3, dash='dash'),
            marker=dict(size=8, symbol='diamond')
        ))
        
        fig.update_layout(
            title='Tahmin vs Gerçek Tüketim Karşılaştırması',
            xaxis_title='Tarih',
            yaxis_title='Tüketim (kWh)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_future_predictions(self, predictions_df: pd.DataFrame) -> go.Figure:
        """
        Gelecek tahminleri grafiği
        
        Args:
            predictions_df: Tahmin verilerini içeren DataFrame
            
        Returns:
            Plotly Figure objesi
        """
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Tüketim tahmini
        fig.add_trace(
            go.Bar(
                x=predictions_df['Tarih'],
                y=predictions_df['Tahmini_Tuketim_kWh'],
                name='Tahmini Tüketim',
                marker_color=self.color_scheme['info'],
                hovertemplate='<b>Tarih:</b> %{x}<br>' +
                             '<b>Tüketim:</b> %{y:,.0f} kWh<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Maliyet tahmini
        fig.add_trace(
            go.Scatter(
                x=predictions_df['Tarih'],
                y=predictions_df['Tahmini_Maliyet_TL'],
                name='Tahmini Maliyet',
                mode='lines+markers',
                line=dict(color=self.color_scheme['danger'], width=3),
                marker=dict(size=10),
                hovertemplate='<b>Tarih:</b> %{x}<br>' +
                             '<b>Maliyet:</b> ₺%{y:,.2f}<br>' +
                             '<extra></extra>'
            ),
            secondary_y=True
        )
        
        fig.update_xaxes(title_text="Tarih")
        fig.update_yaxes(title_text="Tüketim (kWh)", secondary_y=False)
        fig.update_yaxes(title_text="Maliyet (TL)", secondary_y=True)
        
        fig.update_layout(
            title='Gelecek Ay Tahminleri',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def plot_seasonal_analysis(self, df: pd.DataFrame) -> go.Figure:
        """
        Mevsimsel analiz grafiği

        Args:
            df: Mevsimsel verileri içeren DataFrame

        Returns:
            Plotly Figure objesi
        """
        # DataFrame'i kopyala (orijinali değiştirmemek için)
        df_seasonal = df.copy()

        # NaN değerleri temizle
        df_seasonal = df_seasonal[df_seasonal['month'].notna()]
        df_seasonal = df_seasonal[df_seasonal['total_consumption'].notna()]
        df_seasonal = df_seasonal[df_seasonal['total_consumption'] > 0]

        if len(df_seasonal) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Mevsimsel analiz için yeterli veri yok",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='Mevsimsel Ortalama Tüketim',
                template='plotly_white',
                height=450
            )
            return fig

        # Mevsim tanımla
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Kış'
            elif month in [3, 4, 5]:
                return 'İlkbahar'
            elif month in [6, 7, 8]:
                return 'Yaz'
            else:
                return 'Sonbahar'

        df_seasonal['season'] = df_seasonal['month'].apply(get_season)

        # Unique term bazında hesapla
        df_unique = df_seasonal.drop_duplicates(subset=['accrual_term_id'])

        # Mevsimsel istatistikler
        seasonal = df_unique.groupby('season')['total_consumption'].agg(['mean', 'sum', 'count']).reset_index()
        seasonal.columns = ['season', 'avg_consumption', 'total_consumption', 'count']

        # Mevsim sıralaması
        season_order = ['Kış', 'İlkbahar', 'Yaz', 'Sonbahar']
        seasonal['season'] = pd.Categorical(seasonal['season'], categories=season_order, ordered=True)
        seasonal = seasonal.sort_values('season')

        # Renkler
        season_colors = {
            'Kış': '#3498db',
            'İlkbahar': '#2ecc71',
            'Yaz': '#f39c12',
            'Sonbahar': '#e74c3c'
        }

        fig = go.Figure()

        # Her mevsim için ayrı bar trace (legend'da her biri kendi rengiyle görünsün)
        for season in season_order:
            season_data = seasonal[seasonal['season'] == season]
            if len(season_data) > 0:
                fig.add_trace(go.Bar(
                    x=season_data['season'],
                    y=season_data['avg_consumption'],
                    name=season,
                    marker_color=season_colors[season],
                    text=season_data['avg_consumption'].apply(lambda x: f'{x:,.0f}'),
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Ortalama: %{y:,.0f} kWh<br>' +
                                 '<extra></extra>'
                ))

        # Toplam tüketim çizgisi (ikincil Y ekseni)
        fig.add_trace(go.Scatter(
            x=seasonal['season'],
            y=seasonal['total_consumption'],
            name='Toplam Tüketim',
            mode='lines+markers',
            line=dict(color='black', width=2, dash='dash'),
            marker=dict(size=10, symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>' +
                         'Toplam: %{y:,.0f} kWh<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title='Mevsimsel Tüketim Analizi',
            xaxis_title='Mevsim',
            yaxis_title='Ortalama Tüketim (kWh)',
            yaxis2=dict(
                title='Toplam Tüketim (kWh)',
                overlaying='y',
                side='right'
            ),
            template='plotly_white',
            height=450,
            showlegend=True,
            hovermode='x unified'
        )

        return fig
    
    def create_summary_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Özet metrikler oluştur

        Args:
            df: Veri DataFrame'i

        Returns:
            Metrikler dictionary'si
        """
        # Unique term bazında hesaplama yap - GROUPBY ile doğru toplama
        # Her accrual_term_id için toplam tüketim ve maliyeti hesapla
        cost_column = 'term_total_cost' if 'term_total_cost' in df.columns else 'amount'

        # ÖNEML İ: Her iki hesaplama da UNIQUE term bazında yapılmalı
        # Çünkü total_consumption ve cost her term'in tüm satırlarında aynı değeri içeriyor
        df_unique = df.drop_duplicates(subset=['accrual_term_id'])

        # TÜKETİM: Unique term bazında
        total_consumption = df_unique['total_consumption'].sum()

        # MALİYET: Unique term bazında
        total_cost = df_unique[cost_column].sum()

        # Aylık hesaplama için unique term bazında çalış
        df_grouped = df.groupby('accrual_term_id').agg({
            'total_consumption': 'first',
            cost_column: 'first',
            'year': 'first',
            'month': 'first'
        }).reset_index()

        df_unique = df_grouped  # Geriye dönük uyumluluk için

        # Aylık gruplamalar
        monthly_data = df_unique.groupby(['year', 'month']).agg({
            'total_consumption': 'sum',
            cost_column: 'sum'
        }).reset_index()

        # Sütun isimlerini standardize et
        monthly_data.rename(columns={cost_column: 'total_cost'}, inplace=True)

        # Boş değerleri filtrele
        monthly_data_filtered = monthly_data[monthly_data['total_consumption'] > 0]

        # AYLIK ORTALAMA: Toplam / Ay sayısı (mean() değil!)
        # Çünkü total_consumption zaten her kayda term toplamı olarak yazılıyor
        num_months = len(monthly_data_filtered)
        avg_monthly_consumption = total_consumption / num_months if num_months > 0 else 0
        avg_monthly_cost = total_cost / num_months if num_months > 0 else 0

        # En yüksek ve en düşük aylar
        if len(monthly_data_filtered) > 0:
            max_consumption_idx = monthly_data_filtered['total_consumption'].idxmax()
            min_consumption_idx = monthly_data_filtered['total_consumption'].idxmin()

            max_year = int(monthly_data_filtered.loc[max_consumption_idx, 'year'])  # type: ignore
            max_month = int(monthly_data_filtered.loc[max_consumption_idx, 'month'])  # type: ignore
            max_consumption_month = f"{max_year}-{max_month:02d}"
            max_consumption_value = monthly_data_filtered.loc[max_consumption_idx, 'total_consumption']

            min_year = int(monthly_data_filtered.loc[min_consumption_idx, 'year'])  # type: ignore
            min_month = int(monthly_data_filtered.loc[min_consumption_idx, 'month'])  # type: ignore
            min_consumption_month = f"{min_year}-{min_month:02d}"
            min_consumption_value = monthly_data_filtered.loc[min_consumption_idx, 'total_consumption']
        else:
            max_consumption_month = "N/A"
            max_consumption_value = 0
            min_consumption_month = "N/A"
            min_consumption_value = 0

        return {
            'total_consumption': total_consumption,
            'total_cost': total_cost,
            'avg_monthly_consumption': avg_monthly_consumption,
            'avg_monthly_cost': avg_monthly_cost,
            'max_consumption_month': max_consumption_month,
            'max_consumption_value': max_consumption_value,
            'min_consumption_month': min_consumption_month,
            'min_consumption_value': min_consumption_value
        }

    def analyze_tariff_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tarife kategorilerine göre maliyet analizi

        Args:
            df: Ana DataFrame (merged data)

        Returns:
            Tarife kategorisi analizi içeren DataFrame
        """
        # Fee verilerini al - df içinde fee bilgileri var
        if 'fee_code' not in df.columns:
            return pd.DataFrame()

        # Fee code'un ilk kısmını al (tarife kategorisi)
        df_analysis = df.copy()
        df_analysis['tariff_category'] = df_analysis['fee_code'].str.split('_').str[0]

        # Kategori isimlendirmeleri
        category_names = {
            '4AG': '4AG (Ev/İşyeri)',
            '4OG': '4OG (Sanayi)',
            'URT': 'URT (Üretim)',
            'KAG': 'KAG (Kamu-AG)',
            'KOG': 'KOG (Kamu-OG)',
            'AG': 'AG (Alçak Gerilim)',
            'OG': 'OG (Orta Gerilim)',
            'KCK': 'KCK (Kesinti)',
            'YLL': 'YLL (Yıllık)'
        }

        # Kategorilere göre groupby
        category_summary = df_analysis.groupby('tariff_category').agg({
            'amount': 'sum',
            'unit_price': 'mean',
            'consumption': 'sum'
        }).reset_index()

        category_summary.columns = ['Kategori Kodu', 'Toplam Maliyet (TL)',
                                    'Ort. Birim Fiyat (TL/kWh)', 'Toplam Tüketim (kWh)']

        # İsimleri ekle
        category_summary['Kategori Adı'] = category_summary['Kategori Kodu'].apply(
            lambda x: category_names.get(x, x)
        )

        # Sıralama: Toplam maliyete göre
        category_summary = category_summary.sort_values('Toplam Maliyet (TL)', ascending=False)

        # Sütun sıralaması
        category_summary = category_summary[['Kategori Adı', 'Toplam Maliyet (TL)',
                                            'Ort. Birim Fiyat (TL/kWh)', 'Toplam Tüketim (kWh)']]

        return category_summary

    def plot_tariff_categories(self, category_df: pd.DataFrame) -> go.Figure:
        """
        Tarife kategorileri bar chart

        Args:
            category_df: analyze_tariff_categories() sonucu

        Returns:
            Plotly Figure objesi
        """
        if category_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Tarife kategorisi verisi bulunamadı",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=category_df['Kategori Adı'],
            y=category_df['Toplam Maliyet (TL)'],
            marker_color=self.color_scheme['primary'],
            text=category_df['Toplam Maliyet (TL)'].apply(lambda x: f'₺{x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                         'Toplam: ₺%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title='Tarife Kategorilerine Göre Maliyet Dağılımı',
            xaxis_title='Tarife Kategorisi',
            yaxis_title='Toplam Maliyet (TL)',
            hovermode='x unified',
            showlegend=False,
            height=500
        )

        return fig

    def plot_tariff_categories_pie(self, df: pd.DataFrame) -> go.Figure:
        """
        Tarife kategorilerine göre maliyet dağılımı pasta grafiği

        Args:
            df: Veri DataFrame'i

        Returns:
            Plotly Figure objesi
        """
        if 'fee_code' not in df.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Tarife kategorisi verisi bulunamadı",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Fee code'dan kategori belirle
        df_analysis = df.copy()
        df_analysis['tariff_category'] = df_analysis['fee_code'].str.split('_').str[0]

        # Unique term bazında maliyet hesapla (her term bir kez)
        df_unique = df_analysis.drop_duplicates(subset=['accrual_term_id'])

        # term_total_cost varsa onu kullan
        cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'

        # Kategorilere göre maliyet topla
        category_costs = df_unique.groupby('tariff_category')[cost_column].sum()

        # Ana kategoriler ve isimleri
        pie_data = []
        pie_labels = []
        pie_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#8c564b']

        # 1. 4AG (Alçak Gerilim)
        if '4AG' in category_costs.index:
            pie_labels.append('4AG (Alçak Gerilim)<br>Evler ve küçük işletmeler')
            pie_data.append(category_costs['4AG'])

        # 2. 4OG (Orta Gerilim)
        if '4OG' in category_costs.index:
            pie_labels.append('4OG (Orta Gerilim)<br>Sanayi ve büyük işletmeler')
            pie_data.append(category_costs['4OG'])

        # 3. URT (Üretim)
        if 'URT' in category_costs.index:
            pie_labels.append('URT (Üretim)<br>Enerji üretim tesisleri')
            pie_data.append(category_costs['URT'])

        # 4. KAG/KOG (Kamu) - Birleşik
        kamu_total = 0
        if 'KAG' in category_costs.index:
            kamu_total += category_costs['KAG']
        if 'KOG' in category_costs.index:
            kamu_total += category_costs['KOG']
        if kamu_total > 0:
            pie_labels.append('KAG/KOG (Kamu)<br>Kamu kurumları')
            pie_data.append(kamu_total)

        # 5. Diğer kategoriler
        main_categories = ['4AG', '4OG', 'URT', 'KAG', 'KOG']
        other_total = 0
        for cat in category_costs.index:
            if cat not in main_categories:
                other_total += category_costs[cat]

        # Diğer kategorileri ekle
        if other_total > 0:
            pie_labels.append('Diğer Kategoriler<br>Özel durumlar')
            pie_data.append(other_total)

        # Pasta grafiği oluştur
        fig = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_data,
            marker=dict(colors=pie_colors[:len(pie_data)]),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Maliyet: ₺%{value:,.0f}<br>' +
                         'Oran: %{percent}<br>' +
                         '<extra></extra>'
        )])

        fig.update_layout(
            title='Tarife Kategorilerine Göre Toplam Maliyet Dağılımı',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )

        return fig