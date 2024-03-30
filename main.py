import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def read_data(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print("File not found.")
        return None

impression_multipliers = {"SF": {"HZ": 1650, "OZ": 1075}, "LA": {"HZ": 1050, "OZ": 650}, "NY": {"HZ": 2500, "OZ": 1300}, "CHI": {"HZ": 850, "OZ": 450}, "DAL": {"HZ": 704, "OZ": 450}}

cpms = {"SF": {"HZ": 6, "OZ": 4}, "LA": {"HZ": 7, "OZ": 5}, "NY": {"HZ": 8, "OZ": 5}, "CHI": {"HZ": 5, "OZ": 4}, "DAL": {"HZ": 4, "OZ": 3}}

def calculate_impressions(dh_list, hz_list, city):
    oz_list = []
    impressions_hot_zone = 0
    impressions_other_zone = 0

    for dh, hz in zip(dh_list, hz_list):
        oz = (dh - (dh * hz)) / 100
        oz_list.append(oz)

    for dh, hz, oz in zip(dh_list, hz_list, oz_list):
        impressions_hot_zone += (dh * hz) * impression_multipliers[city]["HZ"]
        impressions_other_zone += (dh * oz) * impression_multipliers[city]["OZ"]

    impressions_hot_zone + impressions_other_zone

    return impressions_hot_zone, impressions_other_zone

def calculate_profit(impressions_hot_zone, impressions_other_zone, city):
    profit = (impressions_hot_zone * cpms[city]["HZ"] / 1000) + (impressions_other_zone * cpms[city]["OZ"] / 1000)

    return profit

def calculate_cost(dh_list):
    cost = 0
    
    for dh in dh_list:
        if dh != 0:
            cost += 50

    return cost

def recruit_drivers(df):
    profits_by_city = {city: [] for city in df["City"].unique()}

    for index, row in df.iterrows():
        if row["Driver Status"] == 0:
            i_hot_zone, i_other_zone = calculate_impressions([row[f'Week {i}_DrivingHours'] for i in range(1, 6)], [row[f'Week {i}_HotZone'] for i in range(1, 6)], row["City"])

            profit = calculate_profit(i_hot_zone, i_other_zone, row["City"])
            cost = calculate_cost([row[f'Week {i}_DrivingHours'] for i in range(1, 6)])

            total_profit = profit - cost
            profits_by_city[row["City"]].append((row["Drivers"], total_profit))

    for city, profits in profits_by_city.items():
        profits.sort(key=lambda x: x[1], reverse=True)

        print(f"Top 10 Most Profitable Drivers in {city}:")
        for i, (driver, profit) in enumerate(profits[:10], 1):
            print(f"{i}. {driver}: ${profit}")
        print()

def uninstall_drivers(df):
    profits = []

    for index, row in df.iterrows():
        if row["Driver Status"] == 1:
            i_hot_zone, i_other_zone = calculate_impressions([row[f'Week {i}_DrivingHours'] for i in range(1, 6)], [row[f'Week {i}_HotZone'] for i in range(1, 6)], row["City"])

            profit = calculate_profit(i_hot_zone, i_other_zone, row["City"])
            cost = calculate_cost([row[f'Week {i}_DrivingHours'] for i in range(1, 6)])

            total_profit = profit - cost
            profits.append((row["Drivers"], total_profit))

    profits.sort(key=lambda x: x[1])

    print("20 Lowest Profitable Drivers:")
    for i in range(min(20, len(profits))):
        driver, profit = profits[i]
        print(f"{driver}: ${profit}")

def calculate_most_profitable_city(df):
    city_profits = {}

    for city in df["City"].unique():
        total_profit_city = 0
        for index, row in df[df["City"] == city].iterrows():
            i_hot_zone, i_other_zone = calculate_impressions([row[f'Week {i}_DrivingHours'] for i in range(1, 6)], [row[f'Week {i}_HotZone'] for i in range(1, 6)], city)
            profit = calculate_profit(i_hot_zone, i_other_zone, city)
            cost = calculate_cost([row[f'Week {i}_DrivingHours'] for i in range(1, 6)])
            total_profit_city += profit - cost

        city_profits[city] = total_profit_city

    most_profitable_city = max(city_profits, key=city_profits.get)

    print(f"The most profitable city based on 5 weeks of data is {most_profitable_city} with a total profit of ${city_profits[most_profitable_city]}")

def process_drivers(df):
    all_drivers = []

    for index, row in df.iterrows():
        i_hot_zone, i_other_zone = calculate_impressions([row[f'Week {i}_DrivingHours'] for i in range(1, 6)], [row[f'Week {i}_HotZone'] for i in range(1, 6)], row["City"])

        profit = calculate_profit(i_hot_zone, i_other_zone, row["City"])
        cost = calculate_cost([row[f'Week {i}_DrivingHours'] for i in range(1, 6)])

        total_profit = profit - cost
        all_drivers.append((row["Drivers"], row["Driver Status"], row["City"], total_profit))

    df_all = pd.DataFrame(all_drivers, columns=["Drivers", "Status", "City", "Total Profit"])

    return df_all

if __name__ == "__main__":
    file_path = 'data/data_set.xlsx'
    df = read_data(file_path)
    if df is not None:
        recruit_drivers(df)
        uninstall_drivers(df)
        calculate_most_profitable_city(df)

        all_drivers_df = process_drivers(df)
        all_drivers_df.to_excel('data/all_drivers.xlsx', index=False)
        
        city_profits = all_drivers_df.groupby('City')['Total Profit'].sum()
        city_profits.plot(kind='bar', color='skyblue')
        plt.title('Total Profit by City')
        plt.xlabel('City')
        plt.ylabel('Total Profit ($)')
        plt.xticks(rotation=45)
        
        def format_func(value, tick_number):
            if value >= 1000:
                value /= 1000
                return f'{value:,.0f}K'
            else:
                return f'{value:,.0f}'
        
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        
        plt.show()

