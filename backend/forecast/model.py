import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
import time
warnings.filterwarnings('ignore')

def check_stationary(timeseries, title):
    print(f"Result of Dickey-Fuller Test for {title}: ")
    if len(timeseries) < 3:
        return False
    dftest = adfuller(timeseries, autolag = "AIC")
    dfoutput = pd.Series(dftest[0:4], index = ["Test Statistics", "p-value", "#Lags Used", "Number of Obersvations Used"])
    for key, value in dftest[4].items():
        dfoutput['Critical value (%s)'%key] = value
    print(dfoutput)
    print("Is Stationary:", dftest[1] <= 0.05)
    return dftest[1] <= 0.05

def find_best_arima_model(data, max_p = 3, max_d = 3, max_q = 3):
    best_aic = np.inf
    best_order = None

    for p in range(max_p + 1):
        for d in range(max_d + 1):
            for q in range(max_q + 1):
                try:
                    arima_model = ARIMA(data, order = (p, d, q))
                    fit_model = arima_model.fit()
                    aic = fit_model.aic
    
                    if aic < best_aic:
                        best_aic = aic
                        best_order = (p, d, q)
                except:
                    continue
    
    return best_order, best_aic

def forecast_arima(data, order, steps = 1):
    arima_model = ARIMA(data, order=order)
    fitted_model = arima_model.fit()
    forecast = fitted_model.forecast(steps = steps)
    conf_int = fitted_model.get_forecast(steps = steps).conf_int()

    return forecast, conf_int, fitted_model

def create_budget_forecast(monthly_data, income, target_savings):
    forecasts = {}
    model_summary = {}

    start_time = time.time()

    cols = {col for col in monthly_data.columns if not col.endswith(" %") and col != "Total"}
    print("Monthly Data")
    print(monthly_data)

    if (monthly_data.shape[0] < 3):
        budget = None
        forecast = None
        model_summary = None
        print("Data not sufficient")
        return {}, model_summary, {}
    
    for col in cols:
        if col in monthly_data.columns:


            data = monthly_data[col].dropna()

            if(len(data) < 3):
                print(f"{col} has insufficient data for ARIMA modelling!!")
                forecasts[col] = data.mean() if len(data) > 0 else 0

            is_stationary = check_stationary(data, col)
    
            best_order, best_aic = find_best_arima_model(data)
    
            forecast, conf_int, fitted_model = forecast_arima(data, best_order)

            if (forecast.iloc[0] < 0):

                forecast = data.mean()
                forecasts[col] = forecast

                model_summary[col] = {
                'forecast': forecast,
                'aic': 0,
                'order': [0, 0, 0],
                'lower_bound': data.min(),
                'upper_bound': data.max()
                }

                print(f"{col}:")
                print(f"Forecast: {forecast}")
                print(f"Lower Bound: {data.min()}")
                print(f"Upper Bound: {data.max()}")

            else: 
                
                forecasts[col] = forecast.iloc[0]
        
                model_summary[col] = {
                'forecast': forecast.iloc[0],
                'aic': best_aic,
                'order': best_order,
                'lower_bound': conf_int.iloc[0, 0],
                'upper_bound': conf_int.iloc[0, 1]
                }

                print(f"{col}:")
                print(f"Best order: {best_order}")
                print(f"AIC: {best_aic}")
                print(f"Forecast: {forecast.iloc[0]}")
                print(f"Lower Bound: {conf_int.iloc[0, 0]}")
                print(f"Upper Bound: {conf_int.iloc[0, 1]}")

    total_forecast = sum(forecasts.values())
    budget = forecasts.copy()

    available_for_expenses = income - target_savings
    budget_surplus_deficit = available_for_expenses - total_forecast

    print(available_for_expenses)
    print(budget_surplus_deficit)

    if(budget_surplus_deficit > 0):
        print(f"Surplus: {budget_surplus_deficit}")
    elif(budget_surplus_deficit < 0):
        print(f"Deficit: {budget_surplus_deficit}")
    else:
        print("Balanced!!")

    cat_percent = {}

    for category, forecast_value in forecasts.items():
        percentage = (forecast_value / total_forecast) * 100
        cat_percent[category] = percentage
        print(f"{category:<20}: Rs. {forecast_value:>8,.2f} ({percentage:>5.1f}%)")

    endtime = time.time()

    if budget_surplus_deficit < 0:
        sorted_categories = sorted(forecasts.items(), key = lambda x:x[1], reverse=True)

        while budget_surplus_deficit < 0:
            made_progress = False 
        
            for i, (category, value) in enumerate(sorted_categories):
                current_value = budget.get(category, 0)
        
                if current_value <= 0:
                    continue

                current_value = budget.get(category, 0)
        
            #     categ_percent = cat_percent[category]

            #     deduction_amount = (categ_percent/100) * value

            #     new_value = current_value - deduction_amount

            #     budget[category] = new_value

            #     budget_surplus_deficit += new_value

            # if budget_surplus_deficit >= -1e-2:
            #     break 
        
                p = 50 / (i + 1)
                twt = (20 / 100) * current_value 
        
                if ((p / 100) * abs(budget_surplus_deficit)) < twt:
                    deduction_amount = (p / 100) * abs(budget_surplus_deficit)
                elif (((p / 2) / 100) * abs(budget_surplus_deficit)) < twt:
                    deduction_amount = ((p / 2) / 100) * abs(budget_surplus_deficit)
                elif (((p / 4) / 100) * abs(budget_surplus_deficit)) < twt:
                    deduction_amount = ((p / 4) / 100) * abs(budget_surplus_deficit)
                else:
                    deduction_amount = ((p / 8) / 100) * abs(budget_surplus_deficit)
        
                deduction_amount = min(deduction_amount, current_value)
        
                if deduction_amount <= 0:
                    continue 
        
                new_value = current_value - deduction_amount
                budget[category] = new_value
                budget_surplus_deficit += deduction_amount
                made_progress = True
        
                print(f"\nReducing {category}")
                print(f"Original: {current_value:.2f}")
                print(f"Deduction: {deduction_amount:.2f}")
                print(f"New Value: {new_value:.2f}")
                print(f"Updated Deficit: {budget_surplus_deficit:.2f}")
        
                if budget_surplus_deficit >= 0:
                    break
        
            if not made_progress:
                print("⚠️ No further deductions possible.")
                break

        endtime = time.time()

    elapsed_time = endtime - start_time
    print(elapsed_time)
             
    return forecasts, model_summary, budget