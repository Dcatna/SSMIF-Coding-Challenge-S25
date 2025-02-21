import { useEffect, useState } from 'react'

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
interface TradeHistory {
    Date: string;
    Quantity: number;
    Ticker: string;
}

const TradeTable = () => {
    const [holdings, setHoldings] = useState<TradeHistory[]>([]);

      useEffect(() => {
        fetch("http://127.0.0.1:5000/trades")
        .then(response => response.json())
        .then(data => setHoldings(data.reverse()))
        .catch(error => console.error("Error fetching holdings:", error));
      }, []);


  return (
    <div className='border-2 border-black'>
        <h2 className="text-lg font-bold">All Trades</h2>
        <Table>
        <TableHeader>
            <TableRow>
                <TableHead>Ticker</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Date</TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {holdings.map((holding, idx) => (
                <TableRow key={idx}>
                    <TableCell>{holding.Ticker}</TableCell>
                    <TableCell>{holding.Quantity}</TableCell>
                    <TableCell>{holding.Date}</TableCell>
                </TableRow>
            ))}
        </TableBody>
        </Table>
    </div>
  )
}

export default TradeTable