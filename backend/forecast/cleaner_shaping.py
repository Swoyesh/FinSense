import pandas as pd

def cleaner_function(df):
    df.columns = df.columns.str.strip()
    df = df.dropna(subset = ["Date Time", "Dr.", "Cr.", "Category"])
    df["Date Time"] = pd.to_datetime(df["Date Time"])
    df.set_index("Date Time", inplace = True)
    df.sort_index(inplace = True)
    return df

def reshaping(df):
    monthly = df.groupby([pd.Grouper(freq = "M"), "Category"])["Dr."].sum().unstack(fill_value=0)

    for cat in monthly.columns:
        if sum(monthly[cat]) == 0:
            monthly.drop([cat], axis = 1, inplace=True)
    
    def summation(row):
        total_sum = 0
        for value in row:
            total_sum = total_sum + value
        return total_sum
    
    monthly['Total'] = monthly.apply(lambda x: summation(x), axis = 1)
    
    def percentage(row, col):
        percent = ((row[col] / row["Total"]) * 100)
        return percent
    
    for col in monthly.columns:
        monthly[f"{col} %"] = monthly.apply(lambda x: percentage(x, col), axis = 1)
    
    return monthly