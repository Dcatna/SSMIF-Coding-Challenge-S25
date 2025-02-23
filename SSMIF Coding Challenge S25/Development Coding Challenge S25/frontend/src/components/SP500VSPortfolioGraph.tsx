import { useEffect, useState } from "react";
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, Line } from "recharts";

const SP500VSPortfolioGraph = () => {
    const [data, setData] = useState([])
    
    useEffect(() => {
        fetch("http://127.0.0.1:5000/S&P500VSPortfolio")
        .then(response => response.json())
        .then(rawData => {

            setData(rawData);

        })
        .catch(error => console.error("Error fetching holdings:", error));
    }, []);
    console.log(data)
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <XAxis dataKey="Date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <CartesianGrid strokeDasharray="3 3" />
        <Line type="monotone" dataKey="SP500PctChange" stroke="#8884d8" strokeWidth={3} dot={false} />
        <Line type="monotone" dataKey="PortfolioPctChange" stroke="#82ca9d" strokeWidth={3} dot={false} />

      </LineChart>
    </ResponsiveContainer>
  )
}

export default SP500VSPortfolioGraph