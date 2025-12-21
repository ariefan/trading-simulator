'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface Strategy {
  id: string;
  name: string;
  description: string;
  type: string;
  createdAt: string;
  lastBacktest?: {
    date: string;
    result: number;
  };
}

const MOCK_STRATEGIES: Strategy[] = [
  {
    id: '1',
    name: 'SMA Crossover',
    description: 'Simple moving average crossover strategy using 10 and 20 period SMAs',
    type: 'Trend Following',
    createdAt: '2024-01-15',
    lastBacktest: { date: '2024-01-20', result: 12.5 },
  },
  {
    id: '2',
    name: 'RSI Overbought/Oversold',
    description: 'Mean reversion strategy using RSI with 30/70 levels',
    type: 'Mean Reversion',
    createdAt: '2024-01-18',
    lastBacktest: { date: '2024-01-19', result: -3.2 },
  },
  {
    id: '3',
    name: 'MACD Signal Line',
    description: 'Momentum strategy based on MACD and signal line crossovers',
    type: 'Momentum',
    createdAt: '2024-01-20',
  },
];

const STRATEGY_TEMPLATES = [
  {
    name: 'SMA Crossover',
    code: `class SMACrossover(Strategy):
    fast_period = 10
    slow_period = 20

    def init(self):
        self.sma_fast = self.I(SMA, self.data.close, self.fast_period)
        self.sma_slow = self.I(SMA, self.data.close, self.slow_period)

    def next(self):
        if crossover(self.sma_fast, self.sma_slow):
            self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            self.sell()`,
  },
  {
    name: 'RSI Strategy',
    code: `class RSIStrategy(Strategy):
    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        self.rsi = self.I(RSI, self.data.close, self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold:
            self.buy()
        elif self.rsi[-1] > self.overbought:
            self.sell()`,
  },
  {
    name: 'MACD Strategy',
    code: `class MACDStrategy(Strategy):
    fast = 12
    slow = 26
    signal = 9

    def init(self):
        self.macd, self.signal_line, self.histogram = self.I(
            MACD, self.data.close, self.fast, self.slow, self.signal
        )

    def next(self):
        if crossover(self.macd, self.signal_line):
            self.buy()
        elif crossover(self.signal_line, self.macd):
            self.sell()`,
  },
];

export default function StrategiesPage() {
  const [strategies] = useState<Strategy[]>(MOCK_STRATEGIES);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(0);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    description: '',
    code: STRATEGY_TEMPLATES[0].code,
  });

  const handleCreateStrategy = () => {
    // TODO: Call API to create strategy
    console.log('Creating strategy:', newStrategy);
    setIsCreating(false);
    setNewStrategy({
      name: '',
      description: '',
      code: STRATEGY_TEMPLATES[0].code,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Trading Strategies</h1>
          <p className="text-muted-foreground">
            Create and manage your trading strategies
          </p>
        </div>
        <Button onClick={() => setIsCreating(true)}>
          Create Strategy
        </Button>
      </div>

      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Strategy</CardTitle>
            <CardDescription>
              Define your trading strategy using Python code
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Strategy Name</Label>
                <Input
                  id="name"
                  placeholder="My Strategy"
                  value={newStrategy.name}
                  onChange={(e) =>
                    setNewStrategy({ ...newStrategy, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template">Start from Template</Label>
                <select
                  id="template"
                  value={selectedTemplate}
                  onChange={(e) => {
                    const idx = Number(e.target.value);
                    setSelectedTemplate(idx);
                    setNewStrategy({
                      ...newStrategy,
                      code: STRATEGY_TEMPLATES[idx].code,
                    });
                  }}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                >
                  {STRATEGY_TEMPLATES.map((t, i) => (
                    <option key={i} value={i}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Brief description of your strategy"
                value={newStrategy.description}
                onChange={(e) =>
                  setNewStrategy({ ...newStrategy, description: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <Label>Strategy Code</Label>
              <div className="relative">
                <textarea
                  value={newStrategy.code}
                  onChange={(e) =>
                    setNewStrategy({ ...newStrategy, code: e.target.value })
                  }
                  className="w-full h-80 p-4 font-mono text-sm rounded-md border border-input bg-muted/50 resize-none"
                  spellCheck={false}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Define your strategy by extending the Strategy base class. Use init() to set up
                indicators and next() to define trading logic.
              </p>
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsCreating(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateStrategy}>Create Strategy</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Strategy List */}
      <div className="grid gap-4">
        {strategies.map((strategy) => (
          <Card key={strategy.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">{strategy.name}</h3>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-muted">
                      {strategy.type}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {strategy.description}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Created: {new Date(strategy.createdAt).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  {strategy.lastBacktest && (
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Last Backtest</p>
                      <p
                        className={`font-semibold ${
                          strategy.lastBacktest.result >= 0
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {strategy.lastBacktest.result >= 0 ? '+' : ''}
                        {strategy.lastBacktest.result.toFixed(1)}%
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                    <Button size="sm">Backtest</Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {strategies.length === 0 && !isCreating && (
        <Card className="py-12">
          <CardContent className="text-center">
            <div className="text-6xl mb-4">📈</div>
            <h3 className="text-xl font-semibold mb-2">No Strategies Yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first trading strategy to get started
            </p>
            <Button onClick={() => setIsCreating(true)}>Create Strategy</Button>
          </CardContent>
        </Card>
      )}

      {/* Strategy Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Reference</CardTitle>
          <CardDescription>
            Available indicators and methods for your strategies
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <h4 className="font-semibold mb-2">Available Indicators</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li><code className="text-primary">SMA(data, period)</code> - Simple Moving Average</li>
                <li><code className="text-primary">EMA(data, period)</code> - Exponential Moving Average</li>
                <li><code className="text-primary">RSI(data, period)</code> - Relative Strength Index</li>
                <li><code className="text-primary">MACD(data, fast, slow, signal)</code> - MACD</li>
                <li><code className="text-primary">BB(data, period, std)</code> - Bollinger Bands</li>
                <li><code className="text-primary">ATR(high, low, close, period)</code> - Average True Range</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Trading Methods</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li><code className="text-primary">self.buy(size, sl, tp)</code> - Open long position</li>
                <li><code className="text-primary">self.sell(size, sl, tp)</code> - Open short position</li>
                <li><code className="text-primary">self.position</code> - Current position (if any)</li>
                <li><code className="text-primary">self.data.close[-1]</code> - Current close price</li>
                <li><code className="text-primary">crossover(a, b)</code> - True when a crosses above b</li>
                <li><code className="text-primary">crossunder(a, b)</code> - True when a crosses below b</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
