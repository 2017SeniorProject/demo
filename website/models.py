import py2neo
from py2neo import Graph, Node, Relationship
import requests
import json

#open Graph database
graph=Graph("localhost")  #depend on your authorization choice

class RecoEngine:
	def res_near_you(location):
		#send url to get your current location #can use better method to get the division automatically as well
		send_url = 'http://freegeoip.net/json'
		r = requests.get(send_url)
		j = json.loads(r.text)
		lati = j['latitude']
		longi = j['longitude']

		#query for the match your location with the restaurant
		query='''
		WITH point({latitude:{lat},longitude:{lon}}) AS mapcenter
		   MATCH (reco:Restaurant)-[:IN_DIVISION]->(b:Division{e_name:{division}}) 
		   WITH reco, distance (point({latitude: reco.latitude, longitude: reco.longitude}), mapcenter) AS distance 
		     //near you but we can just do the limit so that only shows
		   RETURN reco, distance
		   ORDER BY distance LIMIT 1000
		'''
		lat=24.8229533748
		lon=121.771853579
		division=location
		return graph.run(query,lat=lati,lon=longi,division=division)


	def res_by_month(location,month1):
		#input month, division, average
		month=int(month1)
		division="Jiaoxi Township"

		query='''
		match (d:Division{e_name:"Jiaoxi Township"})-[:IN_MONTH]->(m:Month{month:{month}}),
			(m)<-[:WRITTEN_IN]-(r:Review),
		    (r)-[:ABOUT]->(n:Restaurant)
		return avg(r.SDRate) as avg
		'''
		avg_data=graph.run(query,month=month,division=location).data()

		average=avg_data[0]['avg']

		#recommendation for restaurant by month: ranking the the restaurant by their review rating: most review above average of month
		query='''
		match (d:Division{e_name:{division}})-[:IN_MONTH]->(m:Month{month:{month}})
		match	(m)<-[:WRITTEN_IN]-(r:Review)
		match   (r)-[:ABOUT]->(reco:Restaurant) where r.SDRate>{average}
		return reco, count(r) as count order by count desc
		'''
		return graph.run(query,month=month,division=location,average=average)


	def res_general_rec(location,category):
		#category="其他小吃"
		#division="Jiaoxi Township"

		query='''
		match(reco:Restaurant)-[:IN_DIVISION]-(d:Division),
		(reco)-[:IN_CATEGORY]->(c:Category)
		where c.SDCategory={category} and
			d.e_name={division}
		return reco order by reco.SDRate desc limit 20
		'''
		return graph.run(query,category=category,division=location)

	def res_similiar_search(location1,category1):
		#category="其他小吃"
		#division="Jiaoxi Township"
		category=category1
		division=location1

		query='''
		match(n:Restaurant)-[:IN_DIVISION]-(d:Division),
		(n)-[:IN_CATEGORY]->(c:Category)
		where c.SDCategory={category} and
			d.e_name={division}
		with collect(n) as exclude,collect(c) as rec_cat
		match (reco)-[:IN_CATEGORY]->(c1:Category)
		where NOT reco IN exclude and
			 c1 IN rec_cat
		return reco order by reco.SDRate desc
		'''
		return graph.run(query,category=category,division=division)

	def res_relating_search(location1,category1):
		#input month, division from users(should be saved during the user session to do the recommendation)
		#category="其他小吃"
		#division="Luodong Township"
		category=category1
		division=location1

		# get the search data
		query='''
		match(n:Restaurant)-[:IN_DIVISION]-(d:Division),
		(n)-[:IN_CATEGORY]->(c:Category)
		where c.SDCategory={category} and
			d.e_name={division}
		return n.shopId    
		'''
		search=graph.run(query,category=category,division=division).data()

		#just get the first on in the list to travel around its neighbor to get recommendation  

		input1=search[0]['n.shopId']
		query='''
		match (n:Restaurant{shopId:{input1}}),
		path=(n)-[r:RELATE*1..2]-(reco)
		with reduce(common_au=0, r IN rels(path) | common_au+r.common_au) AS totalWeight,path,(n),(reco)
		return reco,totalWeight order by totalWeight desc limit 20
		'''
		return graph.run(query,input1=input1)