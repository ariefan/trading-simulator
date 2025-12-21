'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { formatCurrency } from '@/lib/utils';

interface Trade {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  exitPrice: number;
  entryTime: string;
  exitTime: string;
  pnl: number;
  pnlPercent: number;
  duration: string;
}

const MOCK_TRADES: Trade[] = [
  {
    id: '1',
    symbol: 'EURUSD',
    side: 'long',
    size: 0.5,
    entryPrice: 1.0820,
    exitPrice: 1.0876,
    entryTime: '2024-01-20 09:30',
    exitTime: '2024-01-20 14:45',
    pnl: 280,
    pnlPercent: 2.8,
    duration: '5h 15m',
  },
  {
    id: '2',
    symbol: 'GBPUSD',
    side: 'short',
    size: 0.3,
    entryPrice: 1.2700,
    exitPrice: 1.2654,
    entryTime: '2024-01-19 11:00',
    exitTime: '2024-01-20 08:30',
    pnl: 138,
    pnlPercent: 1.38,
    duration: '21h 30m',
  },
  {
    id: '3',
    symbol: 'USDJPY',
    side: 'long',
    size: 0.2,
    entryPrice: 149.50,
    exitPrice: 149.10,
    entryTime: '2024-01-19 08:00',
    exitTime: '2024-01-19 10:30',
    pnl: -53.6,
    pnlPercent: -0.54,
    duration: '2h 30m',
  },
  {
    id: '4',
    symbol: 'EURUSD',
    side: 'short',
    size: 0.4,
    entryPrice: 1.0850,
    exitPrice: 1.0890,
    entryTime: '2024-01-18 14:00',
    exitTime: '2024-01-18 16:30',
    pnl: -160,
    pnlPercent: -1.6,
    duration: '2h 30m',
  },
  {
    id: '5',
    symbol: 'AUDUSD',
    side: 'long',
    size: 0.5,
    entryPrice: 0.6540,
    exitPrice: 0.6578,
    entryTime: '2024-01-18 09:00',
    exitTime: '2024-01-18 13:00',
    pnl: 190,
    pnlPercent: 1.9,
    duration: '4h',
  },
  {
    id: '6',
    symbol: 'USDCHF',
    side: 'short',
    size: 0.3,
    entryPrice: 0.8850,
    exitPrice: 0.8823,
    entryTime: '2024-01-17 15:00',
    exitTime: '2024-01-18 08:00',
    pnl: 91.5,
    pnlPercent: 0.92,
    duration: '17h',
  },
];

export default function HistoryPage() {
  const [trades] = useState<Trade[]>(MOCK_TRADES);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const filteredTrades = trades.filter((trade) => {
    const matchesFilter =
      filter === 'all' ||
      (filter === 'wins' && trade.pnl > 0) ||
      (filter === 'losses' && trade.pnl < 0);
    const matchesSearch =
      !search ||
      trade.symbol.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const stats = {
    totalTrades: trades.length,
    wins: trades.filter((t) => t.pnl > 0).length,
    losses: trades.filter((t) => t.pnl < 0).length,
    totalPnl: trades.reduce((sum, t) => sum + t.pnl, 0),
    avgWin:
      trades.filter((t) => t.pnl > 0).reduce((sum, t) => sum + t.pnl, 0) /
        trades.filter((t) => t.pnl > 0).length || 0,
    avgLoss:
      trades.filter((t) => t.pnl < 0).reduce((sum, t) => sum + t.pnl, 0) /
        trades.filter((t) => t.pnl < 0).length || 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Trade History</h1>
        <p className="text-muted-foreground">
          View and analyze your past trades
        </p>
      </div>

      {/* Stats Summary */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total Trades</p>
            <p className="text-2xl font-bold">{stats.totalTrades}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Wins</p>
            <p className="text-2xl font-bold text-green-600">{stats.wins}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Losses</p>
            <p className="text-2xl font-bold text-red-600">{stats.losses}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total P&L</p>
            <p
              className={`text-2xl font-bold ${
                stats.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {stats.totalPnl >= 0 ? '+' : ''}
              {formatCurrency(stats.totalPnl)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Avg Win</p>
            <p className="text-2xl font-bold text-green-600">
              +{formatCurrency(stats.avgWin)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Avg Loss</p>
            <p className="text-2xl font-bold text-red-600">
              {formatCurrency(stats.avgLoss)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'secondary' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'wins' ? 'secondary' : 'outline'}
                size="sm"
                onClick={() => setFilter('wins')}
              >
                Wins
              </Button>
              <Button
                variant={filter === 'losses' ? 'secondary' : 'outline'}
                size="sm"
                onClick={() => setFilter('losses')}
              >
                Losses
              </Button>
            </div>
            <Input
              placeholder="Search by symbol..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="sm:max-w-xs"
            />
          </div>
        </CardContent>
      </Card>

      {/* Trade List */}
      <Card>
        <CardHeader>
          <CardTitle>Trades</CardTitle>
          <CardDescription>
            Showing {filteredTrades.length} of {trades.length} trades
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left text-sm text-muted-foreground">
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Side</th>
                  <th className="pb-3 font-medium">Size</th>
                  <th className="pb-3 font-medium">Entry</th>
                  <th className="pb-3 font-medium">Exit</th>
                  <th className="pb-3 font-medium">Entry Time</th>
                  <th className="pb-3 font-medium">Duration</th>
                  <th className="pb-3 font-medium text-right">P&L</th>
                </tr>
              </thead>
              <tbody>
                {filteredTrades.map((trade) => (
                  <tr key={trade.id} className="border-b last:border-0">
                    <td className="py-4 font-medium">{trade.symbol}</td>
                    <td className="py-4">
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${
                          trade.side === 'long'
                            ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                            : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                        }`}
                      >
                        {trade.side.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4">{trade.size} lots</td>
                    <td className="py-4 font-mono text-sm">
                      {trade.entryPrice.toFixed(
                        trade.symbol.includes('JPY') ? 2 : 4
                      )}
                    </td>
                    <td className="py-4 font-mono text-sm">
                      {trade.exitPrice.toFixed(
                        trade.symbol.includes('JPY') ? 2 : 4
                      )}
                    </td>
                    <td className="py-4 text-sm text-muted-foreground">
                      {trade.entryTime}
                    </td>
                    <td className="py-4 text-sm">{trade.duration}</td>
                    <td className="py-4 text-right">
                      <span
                        className={`font-medium ${
                          trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {trade.pnl >= 0 ? '+' : ''}
                        {formatCurrency(trade.pnl)}
                      </span>
                      <span className="text-xs text-muted-foreground ml-1">
                        ({trade.pnlPercent >= 0 ? '+' : ''}
                        {trade.pnlPercent.toFixed(2)}%)
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredTrades.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No trades found matching your criteria.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
