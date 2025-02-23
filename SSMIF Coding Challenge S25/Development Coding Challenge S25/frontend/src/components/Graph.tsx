import { useEffect, useState } from 'react';
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, Line } from 'recharts';

const Graph = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/sector_breakdown")
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
        <Line type="monotone" dataKey="Technology" stroke="#8884d8" dot={false} strokeWidth={3}/>
        <Line type="monotone" dataKey="Healthcare" stroke="#82ca9d" dot={false} strokeWidth={3}/>
        <Line type="monotone" dataKey="Financial Services" stroke="#ffc658" dot={false} strokeWidth={3}/>
        <Line type="monotone" dataKey="Communication Services" stroke="#ff7300" dot={false} strokeWidth={3}/>
        <Line type="monotone" dataKey="Consumer Defensive" stroke="#00c49f" dot={false} strokeWidth={3}/>
        <Line type="monotone" dataKey="Other" stroke="#999999" dot={false} strokeWidth={3}/>

      </LineChart>
    </ResponsiveContainer>
  );
};

export default Graph;
