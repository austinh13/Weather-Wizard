import { useEffect, useState } from "react";
import sunnyDay from "/SunnyDay.jpg"
export default function WeatherPage(){

    const [location, setLocation] = useState("Texas");
    const [weather, setWeather] = useState(null);
    const [input, setInput] = useState("");

    useEffect(() => {
    async function fetchWeather() {
      try {
        const url = `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${encodeURIComponent(
    location
    )}?unitGroup=us&key=${import.meta.env.VITE_API_KEY}&contentType=json`;


        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

        const data = await response.json();
        setWeather({
          address: data.resolvedAddress,
          ...data.currentConditions,
        });
      } catch (err) {   
        console.error("Error fetching weather:", err);
      }
    }
    fetchWeather();
    }, [location]);

    const getBackground = () => {
        if (!weather) return "";
        if (weather.precipprob === 0) {
        if (weather.temp >= 80) return `url(${sunnyDay})`;
        if (weather.temp >= 45) return `url(${spring})`;
        }
        return `url(${rainy_day})`;
    };

    // Handle Enter key
    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
        e.preventDefault();
        setLocation(input);
        setInput("");
        }
    };

    return(
        <div
  id="content"
  style={{
    backgroundImage: getBackground(),
  }}
>
  {/* Search */}
  <div className="searchDiv">
    <input
      type="text"
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onKeyDown={handleKeyDown}
      placeholder="Enter Location and Press Enter"
      className="searchBar"
    />
  </div>

  {/* Weather data */}
  {weather && (
    <div  id = "display">
      <h1 className="location">{weather.address}</h1>
      <div className="grid">
        <p>Temperature: {weather.temp}°F</p>
        <p>Feels like: {weather.feelslike}°F</p>
        <p>Rain: {weather.precip}%</p>
        <p>Humidity: {weather.humidity}%</p>
        <p>Windspeed: {weather.windspeed} mph</p>
        <p>UV Index: {weather.uvindex}</p>
        <p>Visibility: {weather.visibility} mi</p>
        <p>Sunset: {weather.sunset}</p>
      </div>
    </div>
  )}
</div>
    )
}