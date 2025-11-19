import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

def analyze_trends(monthly_data):

    if 'Total' in monthly_data.columns:
        total_expense = monthly_data['Total']

    if len(total_expense) > 4:
        decomposition = seasonal_decompose(total_expense, model = 'additive', period=3)
        
        fig, axes = plt.subplots(4, 1, figsize = (12, 10))
        decomposition.observed.plot(ax = axes[0], title = 'Original')
        decomposition.trend.plot(ax = axes[1], title = 'trend')
        decomposition.seasonal.plot(ax = axes[2], title = 'seasonality')
        decomposition.resid.plot(ax = axes[3], title = 'Residual')
        plt.tight_layout()
        plt.show()

    return fig