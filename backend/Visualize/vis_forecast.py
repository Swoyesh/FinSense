import matplotlib.pyplot as plt
import pandas as pd

def visualize_forecast(monthly_data, forecasts, model_summary):

    exp_cate = [col for col in monthly_data if not col.endswith(' %') and col != 'Total']

    n_col = 2
    cat_len = len(exp_cate)
    n_row = (cat_len + 1) // n_col + ((cat_len + 1) % n_col > 0)

    fig, axes = plt.subplots(n_row, n_col, figsize = (15, 5*n_row))
    axes = axes.flatten() if n_row > 1 else [axes] if n_col == 1 else axes

    for i, category in enumerate(exp_cate):
        ax = axes[i]

        monthly_data[category].plot(ax = ax, label = "Historical", marker = 'x')

        if category in forecasts:
            forecast_month = monthly_data.index[-1] + pd.DateOffset(month=1)
            ax.scatter(forecast_month, forecasts[category], color = 'red', s = 100, zorder = 5, label = 'Forecast')

            if category in model_summary:
                lower_bound = model_summary[category]['lower_bound']
                upper_bound = model_summary[category]['upper_bound']
                ax.fill_between([forecast_month, forecast_month], [lower_bound, upper_bound], alpha = 0.3, label = 'Confidence Interval')

        ax.set_title(f'{category}: Forecast')
        ax.set_ylabel('Amount')
        ax.legend()
        ax.grid(True, alpha = 0.3)

    plt.tight_layout()
    return plt