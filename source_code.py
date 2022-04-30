import pandas as pd
import tabulate
import numpy as np

df = pd.read_csv('/Users/xinyiyue/Desktop/Chicago_Building.csv', low_memory=False)

# Detect Duplicate Rows
duplicate_row = df[df.duplicated()]
print(f"Duplicate Rows : {duplicate_row}")

# Detect Duplicate Building_ID
duplicate_PM = df[df['Building_ID'].duplicated()]
print(f"Duplicate Primary Keys : {duplicate_PM}")

# Find max and min community number
Community_Num = df["Community_Area_Number"]
max_value = Community_Num.max()
min_value = Community_Num.min()
print(f"Max Community Area Number : {max_value}")
print(f"Min Community Area Number : {min_value}")

# Find max and min Ward
ward = df["Ward"]
max_value = ward.max()
min_value = ward.min()
print(f"Max Ward : {max_value}")
print(f"Min Ward : {min_value}")

# Detect Missing Values
na_val = df.isna().sum()
print(na_val)

# Detect Duplicate Address
duplicate_add = df[df['Address'].duplicated()]
print(f"Duplicate Address : {duplicate_add}")

# Detect Duplicate Location
duplicate_loc = df[df['Location'].duplicated()]
duplicate_loc = duplicate_loc[['Address', 'Location']]
duplicate_loc = duplicate_loc.sort_values('Location')
print(duplicate_loc)

# Count ward 0
df_ward = df[df['Ward'] == 0]
df_ward = df_ward[['Building_ID', 'Address', 'Ward']]
row_count = df_ward.shape[0]
print(df_ward.to_markdown(index=False))
print(f"Number of rows: {row_count}")

# Clean New Dataset
building_permits = pd.read_csv('/Users/xinyiyue/Desktop/Building_Permits.csv', low_memory=False)
building_permits['STREET_NAME'] = building_permits['STREET_NAME'].fillna('')
building_permits['SUFFIX'] = building_permits['SUFFIX'].fillna('')
building_permits['STREET_IDX'] = (building_permits['STREET_NAME'] + ' ' + building_permits['SUFFIX']).str.strip()
building_permits['STREET_IDX'].head()
building_permits['SUFFIX'].value_counts()

# Divide Address Column to Street, Street Number and Street Direction
building = pd.read_csv('/Users/xinyiyue/Desktop/Chicago_Building.csv')
building.head()
dup = building[building.duplicated(['Location'], keep=False)]
dup['Street Number'] = dup['Address'].str.split(pat=" ", n=1, expand=True)[0]
# Keep only one Street Number
dup['Street Number'] = dup['Street Number'].str.replace('[^0-9]+.*', '', regex=True)
dup['Street'] = dup['Address'].str.split(pat=" ", n=1, expand=True)[1]
dup['Street'] = dup['Street'].str.replace('^[- 0-9]+', '', regex=True)
dir = ['N', 'S', 'W', 'E']


# Get Street Dirction
def getStreetDir(x):
    first = x.split(" ", 1)[0]
    if first in dir:
        return first
    else:
        return ''


dup['Street Dir'] = dup['Street'].apply(getStreetDir)


# Get Street(Convert to Capital Letter)
def getStreet(x):
    first = x.split(" ", 1)[0]
    if first in dir:
        return x.split(" ", 1)[1].upper()
    else:
        return x.upper()


dup['Street'] = dup['Street'].apply(getStreet)
dup['Street Number'] = dup['Street Number'].astype('int64')

# Abr function
abv_map = {
    'AVENUE': 'AVE',
    'STREET': 'ST',
    'DRIVE': 'DR',
    'ROAD': 'RD',
    'PLACE': 'PL',
    'PLAZA': 'PLZ',
    'BOULEVARD': 'BLVD',
    'PARKWAY': 'PKWY',
    'COURT': 'CT',
    'TERRACE': 'TER',
    'HIGHWAY': 'HWY',
    'LANE': 'LN',
    'SQUARE': 'SQ',
}


def get_abv_street(street):
    line = street.split(' ')
    suffix = line[-1]
    if suffix in abv_map.keys():
        line[-1] = abv_map[suffix]
    return ' '.join(line)


def get_location(x):
    street_num = dup[dup['Building_ID'] == x]['Street Number'].values[0]
    street_dir = dup[dup['Building_ID'] == x]['Street Dir'].values[0]
    street = dup[dup['Building_ID'] == x]['Street'].values[0]
    street = get_abv_street(street)
    same_street = building_permits[building_permits['STREET DIRECTION'] == street_dir]
    same_street = same_street[same_street['STREET_IDX'] == street]
    same_street['NUM_DIFF'] = (same_street['STREET_NUMBER'] - street_num).abs()
    same_street = same_street.dropna(subset=['LONGITUDE', 'LATITUDE'])
    closest = same_street.sort_values(by=['NUM_DIFF']).head(1)
    if closest.empty:
        return ''
    loc_x = str(closest['Zip'].values[0])
    loc_y = str(closest['LONGITUDE'].values[0])
    return '(' + loc_x + ',' + loc_y + ')'


def missing_value(x):
    street_num = dup[dup['Building_ID'] == x]['Street Number'].values[0]
    street_dir = dup[dup['Building_ID'] == x]['Street Dir'].values[0]
    street = dup[dup['Building_ID'] == x]['Street'].values[0]
    street = get_abv_street(street)
    same_street = building_permits[building_permits['STREET DIRECTION'] == street_dir]
    same_street = same_street[same_street['STREET_IDX'] == street]
    same_street['NUM_DIFF'] = (same_street['STREET_NUMBER'] - street_num).abs()
    same_street = same_street.dropna(subset=['LONGITUDE', 'LATITUDE'])
    closest = same_street.sort_values(by=['NUM_DIFF']).head(1)
    if closest.empty:
        return ''
    comm = str(closest['COMMUNITY_AREA'].values[0])
    comm_num = str(closest['COMMUNITY_AREA_NUM'].values[0])
    ward = str(closest['WARD'].values[0])
    return comm, comm_num, ward


dup['Location'] = dup['Building_ID'].apply(get_location)
dup[dup.duplicated(['Location'], keep=False)]
rowCount = dup[dup.duplicated(['Location'], keep=False)].shape[0]
print(f'Number of rows with duplicated location: {rowCount}')

