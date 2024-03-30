import pandas as pd

file_path = 'data_set.xlsx'

df = pd.read_excel(file_path)

impression_multipliers = {"SF": {"HZ": 1650, "OZ": 1075}, "LA": {"HZ": 1050, "OZ": 650}, "NY": {"HZ": 2500, "OZ": 1300}, "CHI": {"HZ": 850, "OZ": 450}, "DAL": {"HZ": 704, "OZ": 450}}

cpms = {"SF": {"HZ": 6, "OZ": 4}, "LA": {"HZ": 7, "OZ": 5}, "NY": {"HZ": 8, "OZ": 5}, "CHI": {"HZ": 5, "OZ": 4}, "DAL": {"HZ": 4, "OZ": 3}}

def calculate_impressions(dh_list, hz_list, city):
    oz_list = []
    impressions_hot_zone = 0
    impressions_other_zone = 0
    total_impressions = 0

    for dh, hz in zip(dh_list, hz_list):
        oz = (dh - (dh * hz)) / 100
        oz_list.append(oz)

    for dh, hz, oz in zip(dh_list, hz_list, oz_list):
        impressions_hot_zone += (dh * hz) * impression_multipliers[city]["HZ"]
        impressions_other_zone += (dh * oz) * impression_multipliers[city]["OZ"]

    total_impressions = impressions_hot_zone + impressions_other_zone

    return total_impressions

dh_list = [100, 86, 88, 111, 128]
hz_list = [0.38, 0.83, 0.01, 0.1, 0.72]
city = "NY"

print(calculate_impressions(dh_list, hz_list, city))

for index, row in df.iterrows():
    print(calculate_impressions([row["Week 1_DrivingHours"], row["Week 2_DrivingHours"], row["Week 3_DrivingHours"], row["Week 4_DrivingHours"], row["Week 5_DrivingHours"]], [row["Week 1_HotZone"], row["Week 2_HotZone"], row["Week 3_HotZone"], row["Week 4_HotZone"], row["Week 5_HotZone"]], row["City"]))