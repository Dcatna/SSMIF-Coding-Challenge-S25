import { useEffect, useState } from "react";
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, Line } from "recharts";

function SharpeGraph() {
    const [data, setData] = useState([]);
    
      useEffect(() => {
        fetch("http://127.0.0.1:5000/sharperatio")
        .then(response => response.json())
        .then(data => setData(data))
        .catch(error => console.error("Error fetching holdings:", error));
      }, []);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <XAxis dataKey="Date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <CartesianGrid strokeDasharray="3 3" />
        <Line type="monotone" dataKey="SharpeRatio" stroke="#8884d8" strokeWidth={3} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default SharpeGraph