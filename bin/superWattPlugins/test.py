from influxdb import InfluxDBClient
query = 'SELECT OutputActivePower FROM superWatt_QPIGS WHERE time >= now() - 24h'
query2 = 'SELECT PVInputActivePower FROM superWatt_QPIGS WHERE time >= now() - 24h'
client = InfluxDBClient(host="192.168.1.230", port=8086, database="superWatt")
result = client.query(query)
points = result.get_points()
nbValues=0
total=0.0
for point in points:
   nbValues+=1
   total+=point['OutputActivePower']
moy=total/nbValues
print(moy)
print("Consommation journaliere en kWh : "+str(moy*24/1000))

result = client.query(query2)
points = result.get_points()
nbValues=0
total=0.0
for point in points:
   nbValues+=1
   total+=point['PVInputActivePower']
moy=total/nbValues
print(moy)
print("Production journaliere en kWh : "+str(moy*24/1000))
