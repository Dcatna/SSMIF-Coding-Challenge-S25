import { useEffect, useState } from 'react';
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, CartesianGrid, Line, Legend } from 'recharts';

interface PortfolioValue {
  Date: string,
  PortfolioValue: number,
}


const PortfolioValueGraph = () => {
  const [portfolioData, setPortfolioData] = useState<PortfolioValue[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/portfolio_value")
      .then(response => response.json())
      .then(rawData => {
        // Optionally transform rawData if needed.
        // For now, assume rawData is in the correct format.
        setPortfolioData(rawData as PortfolioValue[]);
    
      })
      .catch(error => console.error("Error fetching portfolio value:", error));
  }, []);


  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={portfolioData}>
        <XAxis dataKey="Date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <CartesianGrid strokeDasharray="3 3" />
        <Line type="monotone" dataKey="PortfolioValue" stroke="#8884d8" strokeWidth={3} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PortfolioValueGraph;
