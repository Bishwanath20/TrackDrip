from flask import Flask, render_template_string, request
import folium
import requests
import polyline  # For decoding route geometry from OSRM

app = Flask(__name__)

# All Indian state capitals and major temples
locations = {
    "Sphoorthy": [17.282125, 78.553701],
    "LB Nagar": [17.346349, 78.549999],
    "Hitech City": [17.444107, 78.377383],
    "Parade Ground": [17.446316, 78.497734],
    "Secunderabad": [17.446544, 78.484822],
    "Hyderabad": [17.385044, 78.486671],
    "Tirupati": [13.6288, 79.4192],
    "Srikalahasti": [13.7491, 79.6981],
    "Rameshwaram": [9.2886, 79.3129],
    "Brihadeeswarar": [10.7833, 79.1319],
    "Gokarna": [14.5489, 74.3181],
    "Puri": [19.8135, 85.8312],
    "Konark": [19.8876, 86.0945],
    "Shirdi": [19.7666, 74.4777],
    "Trimbakeshwar": [19.9406, 73.5305],
    "Siddhivinayak Temple": [19.0169, 72.8305],
    "Pune": [18.5204, 73.8567],
    "Sabarimala": [9.4280, 77.0610],
    "Padmanabhaswamy": [8.4825, 76.9488],
    "Kashi": [25.3176, 82.9739],
    "Krishna Janmabhoomi": [27.4925, 77.6737],
    "Ayodhya": [26.7994, 82.2040],
    "Somnath": [20.8880, 70.4012],
    "Dwarka": [22.2394, 68.9678],
    "Kalighat": [22.5183, 88.3385],
    "Mayapur Iskcon": [23.4422, 88.3748],
    "Akshardham": [28.6127, 77.2773],
    "Lotus Temple": [28.5535, 77.2588],
    "Golden Temple": [31.6200, 74.8765],
    "Delhi": [28.6139, 77.2090],
    "Puducherry": [11.9139, 79.8145],
    "Chandigarh": [30.7333, 76.7794],
    "Lakshadweep": [10.5667, 72.6417],
    "Andaman and Nicobar Islands": [11.7401, 92.6586],
    "Dadra and Nagar Haveli":[ 20.27903342965116, 73.0052751738977],
    "Daman and Diu": [20.4133, 72.8467],
    "Ladakh": [34.1526, 77.5770],
    "Hyderabad": [17.385044, 78.486671],
    "Amaravati": [16.5417, 80.5150],
    "Itanagar": [27.0844, 93.6053],
    "Dispur": [26.1445, 91.7362],
    "Patna": [25.5941, 85.1376],
    "Raipur": [21.2514, 81.6296],
    "Panaji": [15.4909, 73.8278],
    "Gandhinagar": [23.2156, 72.6369],
    "Chandigarh": [30.7333, 76.7794],
    "Shimla": [31.1048, 77.1734],
    "Ranchi": [23.3441, 85.3096],
    "Bengaluru": [12.9716, 77.5946],
    "Thiruvananthapuram": [8.5241, 76.9366],
    "Bhopal": [23.2599, 77.4126],
    "Mumbai": [19.0760, 72.8777],
    "Imphal": [24.8170, 93.9368],
    "Shillong": [25.5788, 91.8933],
    "Aizawl": [23.7271, 92.7176],
    "Kohima": [25.6701, 94.1077],
    "Bhubaneswar": [20.2961, 85.8245],
    "Jaipur": [26.9124, 75.7873],
    "Gangtok": [27.3314, 88.6138],
    "Chennai": [13.0827, 80.2707],
    "Agartala": [23.8315, 91.2868],
    "Lucknow": [26.8467, 80.9462],
    "Dehradun": [30.3165, 78.0322],
    "Kolkata": [22.5726, 88.3639],
    "Leh": [34.1526, 77.5770],
    "Srinagar": [34.0837, 74.7973],
    "Jammu": [32.7266, 74.8570],
}

@app.route('/')
def index():
    start = request.args.get('start_location', 'Sphoorthy')
    destination = request.args.get('destination')
    start_coords = locations.get(start, locations['Sphoorthy'])
    map = folium.Map(location=start_coords, zoom_start=6)

    folium.Marker(start_coords, popup=f"Start: {start}").add_to(map)
    total_distance = None

    if destination in locations:
        dest_coords = locations[destination]
        start_lon, start_lat = start_coords[1], start_coords[0]
        dest_lon, dest_lat = dest_coords[1], dest_coords[0]

        # OSRM API call
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{dest_lon},{dest_lat}?overview=full&geometries=polyline"
        response = requests.get(url).json()

        if 'routes' in response:
            main_coords = polyline.decode(response['routes'][0]['geometry'])
            folium.PolyLine(main_coords, color="green", weight=3).add_to(map)
            total_distance = round(response['routes'][0]['distance'] / 1000, 2)
            folium.Marker(dest_coords, popup=f"{destination} ({total_distance} km)").add_to(map)

    return render_template_string("""
        <html>
            <head><title>Route Visualizer</title></head>
            <body>
                <h2>TrackDrip</h2>
                <form method="get">
                    <input type="text" name="start_location" placeholder="Start Location" value="{{ start }}">
                    <input type="text" name="destination" placeholder="Destination" value="{{ destination }}">
                    <button type="submit">Show Route</button>
                </form>
                {% if total_distance %}
                    <p>Total Distance: {{ total_distance }} km</p>
                {% endif %}
                <div style="height: 80vh;">{{ map_html|safe }}</div>
            </body>
        </html>
    """, start=start, destination=destination, total_distance=total_distance, map_html=map._repr_html_())

if __name__ == '__main__':
    app.run(debug=True)
