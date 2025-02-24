import { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

export interface Holding {
    CurrentPrice: number;
    DailyChange: number;
    MarketValue: number;
    Quantity: number;
    Ticker: string;
    TotalChange: number;
    TotalCost: number;
    UnitCost: number;
  }

const StockTable = () => {
    const [holdings, setHoldings] = useState<Holding[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/current_holdings")
    .then(response => response.json())
    .then(data => setHoldings(data))
    .catch(error => console.error("Error fetching holdings:", error));
  }, []);


  return (
    <div className='border-2 border-black'>
    <h2 className="text-lg font-bold">Stock Holdings</h2>
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Ticker</TableHead>
          <TableHead>Quantity</TableHead>
          <TableHead>Day Change</TableHead>
          <TableHead>Total Change</TableHead>
          <TableHead>Market Value</TableHead>
          <TableHead>Unit Cost</TableHead>
          <TableHead>Current Price</TableHead>
          <TableHead>Total Cost</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {holdings.map((holding, index) => (
          <TableRow key={index}>
            <TableCell>{holding.Ticker}</TableCell>
            <TableCell>{holding.Quantity}</TableCell>
            <TableCell className={holding.DailyChange! < 0 ? "text-red-500" : "text-green-500"}>
              {holding.DailyChange?.toFixed(2)}
            </TableCell>
            <TableCell className={holding.TotalChange! < 0 ? "text-red-500" : "text-green-500"}>
              {holding.TotalChange?.toFixed(2)}
            </TableCell>
            <TableCell>${holding.MarketValue.toFixed(3)}</TableCell>
            <TableCell>{holding.UnitCost.toFixed(3)}</TableCell>
            <TableCell>{holding.CurrentPrice.toFixed(3)}</TableCell>
            <TableCell>{holding.TotalCost.toFixed(3)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </div>
  );
};

export default StockTable;
