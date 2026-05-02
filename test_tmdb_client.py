from app.clients.tmdb_client import TMDbClient

client = TMDbClient()

result = client.search_movies("batman")

print(result.keys())
print(result.get("total_results"))
print(result["results"][0]["title"])
