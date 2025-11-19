import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')


def validate_time_series(data, min_length=3):
    if data is None or len(data) < min_length:
        return False
    if data.isna().all():
        return False
    if (data == 0).all():
        return False
    return True


def check_stationarity(timeseries, alpha=0.05):
    try:
        if not validate_time_series(timeseries):
            return False
        
        result = adfuller(timeseries, autolag="AIC")
        p_value = result[1]
        
        return p_value < alpha
    except Exception as e:
        print(f"Stationarity test failed: {e}")
        return False


def detect_trend(data):
    if len(data) < 3:
        return 'flat'
    
    x = np.arange(len(data)).reshape(-1, 1)
    y = data.values
    
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    
    avg_value = np.mean(y)
    threshold = 0.05 * avg_value
    
    if slope > threshold:
        return 'increasing'
    elif slope < -threshold:
        return 'decreasing'
    else:
        return 'flat'


def calculate_volatility(data):
    if len(data) < 2:
        return 0
    
    returns = data.pct_change().dropna()
    volatility = returns.std()
    
    return volatility


def forecast_simple_methods(data):
    forecasts = {}
    
    forecasts['mean'] = data.mean()
    forecasts['median'] = data.median()
    forecasts['last_value'] = data.iloc[-1]
    
    if len(data) >= 3:
        forecasts['ma3'] = data.tail(3).mean()
    else:
        forecasts['ma3'] = data.mean()
    
    if len(data) >= 2:
        recent_avg = data.tail(2).mean()
        older_avg = data.head(len(data) - 2).mean() if len(data) > 2 else data.mean()
        forecasts['weighted_avg'] = 0.7 * recent_avg + 0.3 * older_avg
    else:
        forecasts['weighted_avg'] = data.mean()
    
    trend = detect_trend(data)
    if trend == 'increasing':
        growth_rate = (data.iloc[-1] / data.iloc[0]) ** (1 / len(data)) if len(data) > 1 else 1
        forecasts['trend_adjusted'] = data.iloc[-1] * growth_rate
    elif trend == 'decreasing':
        decay_rate = (data.iloc[-1] / data.iloc[0]) ** (1 / len(data)) if len(data) > 1 else 1
        forecasts['trend_adjusted'] = data.iloc[-1] * decay_rate
    else:
        forecasts['trend_adjusted'] = data.mean()
    
    return forecasts


def forecast_exponential_smoothing(data):
    try:
        if len(data) < 4:
            return None
        
        model = ExponentialSmoothing(data, trend='add', seasonal=None)
        fitted = model.fit()
        forecast = fitted.forecast(steps=1)
        
        return forecast.iloc[0]
    except Exception as e:
        return None


def select_best_arima_order(data, max_p=2, max_d=2, max_q=2):
    best_aic = np.inf
    best_order = None
    
    for p in range(max_p + 1):
        for d in range(max_d + 1):
            for q in range(max_q + 1):
                try:
                    if len(data) < (p + d + q + 3):
                        continue
                    
                    model = ARIMA(data, order=(p, d, q))
                    fitted = model.fit()
                    
                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                except:
                    continue
    
    return best_order, best_aic


def forecast_arima(data):
    try:
        if len(data) < 5:
            return None, None
         
        best_order, best_aic = select_best_arima_order(data)
         
        if best_order is None:
            return None, None
         
        model = ARIMA(data, order=best_order)
        fitted = model.fit()
        forecast = fitted.forecast(steps=1)
        conf_int = fitted.get_forecast(steps=1).conf_int()
         
        forecast_value = forecast.iloc[0]
        lower_bound = conf_int.iloc[0, 0]
        upper_bound = conf_int.iloc[0, 1]
         
        return forecast_value, {
            'order': best_order,
            'aic': best_aic,
            'lower': lower_bound,
            'upper': upper_bound
        }
    except Exception as e:
        return None, None


def ensemble_forecast(data, category):
    if not validate_time_series(data):
        return data.mean() if len(data) > 0 else 0, {}
    
    simple_forecasts = forecast_simple_methods(data)
    
    arima_forecast, arima_info = forecast_arima(data)
    exp_smooth_forecast = forecast_exponential_smoothing(data)
    
    all_forecasts = []
    weights = []
    
    volatility = calculate_volatility(data)
    trend = detect_trend(data)
    
    if volatility < 0.2:
        all_forecasts.append(simple_forecasts['ma3'])
        weights.append(0.3)
        all_forecasts.append(simple_forecasts['weighted_avg'])
        weights.append(0.2)
    else:
        all_forecasts.append(simple_forecasts['weighted_avg'])
        weights.append(0.25)
    
    if arima_forecast is not None and arima_forecast > 0:
        all_forecasts.append(arima_forecast)
        weights.append(0.35)
    
    if exp_smooth_forecast is not None and exp_smooth_forecast > 0:
        all_forecasts.append(exp_smooth_forecast)
        weights.append(0.25)
    
    if trend != 'flat':
        all_forecasts.append(simple_forecasts['trend_adjusted'])
        weights.append(0.2)
    
    weights = np.array(weights)
    weights = weights / weights.sum()
    
    final_forecast = np.average(all_forecasts, weights=weights)
    
    min_reasonable = data.quantile(0.1)
    max_reasonable = data.quantile(0.9) * 1.2
    final_forecast = np.clip(final_forecast, min_reasonable, max_reasonable)
    
    info = {
        'forecast': final_forecast,
        'trend': trend,
        'volatility': volatility,
        'simple_forecasts': simple_forecasts,
        'arima_forecast': arima_forecast,
        'exp_smooth_forecast': exp_smooth_forecast,
        'arima_info': arima_info,
        'confidence_lower': arima_info['lower'] if arima_info else data.quantile(0.25),
        'confidence_upper': arima_info['upper'] if arima_info else data.quantile(0.75)
    }
    
    return final_forecast, info


def allocate_budget_proportional(forecasts, available_budget):
    total_forecast = sum(forecasts.values())
    
    if total_forecast == 0:
        equal_share = available_budget / len(forecasts)
        return {cat: equal_share for cat in forecasts.keys()}
    
    budget = {}
    for category, forecast_value in forecasts.items():
        proportion = forecast_value / total_forecast
        budget[category] = min(proportion * available_budget, forecast_value) 
    return budget


def allocate_budget_priority(forecasts, available_budget, category_priorities=None):
    if category_priorities is None:
        category_priorities = {
            'Utilities & Bills': 1,
            'Groceries & Shopping': 2,
            'Health & Medical': 3,
            'Travel': 4,
            'Dining & Food': 5,
            'Entertainment': 6,
            'Others': 7
        }
    
    sorted_cats = sorted(forecasts.items(), 
                        key=lambda x: (category_priorities.get(x[0], 999), -x[1]))
    
    budget = {}
    remaining = available_budget
    
    for category, forecast_value in sorted_cats:
        if remaining <= 0:
            budget[category] = 0
            continue
        
        allocation = min(forecast_value, remaining)
        budget[category] = allocation
        remaining -= allocation
    
    if remaining > 0:
        for category in budget.keys():
            budget[category] += remaining / len(budget)
    
    return budget


def allocate_budget_balanced(forecasts, available_budget, min_reduction=0.1, max_reduction=0.4):
    total_forecast = sum(forecasts.values())
    deficit = total_forecast - available_budget
    
    if deficit <= 0:
        return forecasts.copy()
    
    reduction_needed = deficit / total_forecast
    
    sorted_categories = sorted(forecasts.items(), key=lambda x: -x[1])
    
    budget = {}
    remaining_deficit = deficit
    
    for i, (category, forecast_value) in enumerate(sorted_categories):
        priority_weight = 1 / (i + 1)
        
        max_cut = forecast_value * max_reduction
        min_cut = forecast_value * min_reduction
        
        reduction = min(
            max_cut,
            max(min_cut, priority_weight * remaining_deficit)
        )
        
        new_value = forecast_value - reduction
        budget[category] = max(0, new_value)
        remaining_deficit -= reduction
        
        if remaining_deficit <= 0:
            break
    
    for category in forecasts.keys():
        if category not in budget:
            budget[category] = forecasts[category]

    total_budget = sum(budget.values())
    if total_budget > available_budget:
        scale_factor = available_budget / total_budget
        for category in budget:
            budget[category] *= scale_factor
    
    return budget


def create_budget_forecast(monthly_data, income, target_savings):
    if monthly_data.shape[0] < 3:
        return {}, {}, {}
    
    available_for_expenses = income - target_savings
    
    forecasts = {}
    model_summary = {}
    
    category_columns = [col for col in monthly_data.columns 
                    if col not in ['Income', 'Total'] and not col.endswith(' %')]

    print("\n" + "="*80)
    print("FORECASTING ANALYSIS")
    print("="*80)
    
    for category in category_columns:
        if category not in monthly_data.columns:
            continue
        
        data = monthly_data[category].dropna()
        
        forecast_value, info = ensemble_forecast(data, category)
        forecasts[category] = forecast_value
        model_summary[category] = info
        
        print(f"\n{category}:")
        print(f"  Historical avg: Rs. {data.mean():,.2f}")
        print(f"  Trend: {info['trend']}")
        print(f"  Volatility: {info['volatility']:.2%}")
        print(f"  Forecast: Rs. {forecast_value:,.2f}")
        print(f"  Confidence: Rs. {info['confidence_lower']:,.2f} - Rs. {info['confidence_upper']:,.2f}")
    
    total_forecast = sum(forecasts.values())
    surplus_deficit = available_for_expenses - total_forecast
    
    print("\n" + "="*80)
    print("BUDGET ALLOCATION")
    print("="*80)
    print(f"Total Income: Rs. {income:,.2f}")
    print(f"Target Savings: Rs. {target_savings:,.2f}")
    print(f"Available for Expenses: Rs. {available_for_expenses:,.2f}")
    print(f"Total Forecast: Rs. {total_forecast:,.2f}")
    print(f"Surplus/Deficit: Rs. {surplus_deficit:,.2f}")
    
    if surplus_deficit >= 0:
        print("\n✓ Budget is balanced with surplus")
        budget = allocate_budget_proportional(forecasts, available_for_expenses)
    else:
        print("\n⚠ Budget deficit detected - applying intelligent allocation")
        budget = allocate_budget_balanced(forecasts, available_for_expenses)
    
    print("\n" + "="*80)
    print("FINAL BUDGET")
    print("="*80)
    
    for category in sorted(budget.keys(), key=lambda x: -budget[x]):
        forecast_val = forecasts[category]
        budget_val = budget[category]
        difference = budget_val - forecast_val
        pct_change = (difference / forecast_val * 100) if forecast_val > 0 else 0
        
        print(f"{category:25} | Forecast: Rs. {forecast_val:>8,.2f} | "
              f"Budget: Rs. {budget_val:>8,.2f} | "
              f"Change: {pct_change:>6.1f}%")
    
    total_budget = sum(budget.values())
    print(f"\n{'TOTAL':25} | Rs. {total_budget:>8,.2f}")
    print(f"Savings: Rs. {income - total_budget:>8,.2f}")
    print("="*80 + "\n")
    
    return forecasts, model_summary, budget