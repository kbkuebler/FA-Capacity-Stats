import urllib3
import pandas as pd
from datetime import datetime
from datetime import timedelta
from pypureclient import flasharray

############
# Add number of days to sample and desired output file name.
# You should start with < 30 days and go from there
############

num_days = 30  # <- Enter number of days here
file_name = 'Volume_Capacity_snaps_2.xlsx'  # <- Enter your file name here in quotes

# Suppress error warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


client = flasharray.Client('192.168.0.NN',
                           version='2.2',
                           private_key_file='rest-key.pem',
                           private_key_password='',
                           username='username',
                           client_id='XXX',
                           key_id='XXX',
                           issuer='issuerid')

# Set and format our sample period
start_date = datetime.now() - timedelta(days=num_days)
my_time = round(start_date.timestamp()) * 1000

# Set up placeholders for volume names and our dicts
volname = []
tcap = []
scap = []
# Get our volume information from the FlashArray
cvol = client.get_volumes_space(names=["*"], start_time=my_time, resolution=86400000).items

# Build out the list of volumes
myvol = []
for item in cvol:
    myvol.append(item)

# Create k/v entries for total physical space
def getTotals():
    for n in range(len(myvol)):
        vol = myvol[n]
        cdict = {'name': vol.name}
        try:
            for i in range(len(myvol)):
                if myvol[i].name == vol.name:
                    cdict.update({datetime.fromtimestamp(myvol[i].time / 1e3):
                                  round(myvol[i].space.total_physical / 1.074e+9, 4)})
            tcap.append(cdict)

        except AttributeError as ae:
            pass
def getSnaps():
    for n in range(len(myvol)):
        vol = myvol[n]
        sdict = {'name': vol.name}
        try:
            for i in range(len(myvol)):
                if myvol[i].name == vol.name:
                    sdict.update({datetime.fromtimestamp(myvol[i].time / 1e3):
                                  round(myvol[i].space.snapshots / 1.074e+9, 4)})
            scap.append(sdict)

        except AttributeError as ae:
            pass
getTotals()
getSnaps()

# Shape output in dataframe for total_physical
tdf = pd.DataFrame(tcap).drop_duplicates().set_index('name')
mycol = tdf.columns[1]
toutdf = tdf.sort_values(mycol, ascending=False)

# Shape output for snapshot data
sdf = pd.DataFrame(scap).drop_duplicates().set_index('name')
mycol = sdf.columns[1]
soutdf = sdf.sort_values(mycol, ascending=False)


# Write everything out to our spreadsheet
with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
    toutdf.to_excel(writer, sheet_name='total_space')
    soutdf.to_excel(writer, sheet_name='snapshots')
