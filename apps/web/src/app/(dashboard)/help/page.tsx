'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const FAQS = [
  {
    question: 'What is paper trading?',
    answer:
      'Paper trading is a simulated trading environment where you can practice trading strategies using virtual money without risking real capital. It helps you learn and test strategies before trading with real funds.',
  },
  {
    question: 'How does backtesting work?',
    answer:
      'Backtesting allows you to test your trading strategies on historical data. You define your strategy rules, select a time period, and the system simulates how your strategy would have performed in the past.',
  },
  {
    question: 'What currency pairs are available?',
    answer:
      'We support major forex pairs including EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, and NZD/USD. More pairs will be added in future updates.',
  },
  {
    question: 'How do I create a trading strategy?',
    answer:
      'Go to the Strategies page and click "Create Strategy". You can start from a template or write your own Python code. Use the Strategy base class and define init() and next() methods for your trading logic.',
  },
  {
    question: 'What is leverage and how does it work?',
    answer:
      'Leverage allows you to control a larger position with a smaller amount of capital. For example, 1:100 leverage means you can control $100,000 with just $1,000. While leverage can amplify gains, it also amplifies losses.',
  },
  {
    question: 'How is P&L calculated?',
    answer:
      'Profit and Loss (P&L) is calculated based on the difference between entry and exit prices, multiplied by your position size. For forex, this is typically measured in pips (the fourth decimal place for most pairs).',
  },
];

const GLOSSARY = [
  { term: 'Pip', definition: 'The smallest price move in a currency pair, usually 0.0001' },
  { term: 'Lot', definition: 'A standard unit of trading volume. 1 lot = 100,000 units' },
  { term: 'Spread', definition: 'The difference between bid and ask prices' },
  { term: 'Margin', definition: 'The collateral required to open and maintain positions' },
  { term: 'Drawdown', definition: 'The peak-to-trough decline in account value' },
  { term: 'Sharpe Ratio', definition: 'Risk-adjusted return metric comparing returns to volatility' },
  { term: 'Win Rate', definition: 'Percentage of trades that are profitable' },
  { term: 'Profit Factor', definition: 'Ratio of gross profit to gross loss' },
];

export default function HelpPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold">Help Center</h1>
        <p className="text-muted-foreground">
          Learn how to use the trading simulator effectively
        </p>
      </div>

      {/* Getting Started */}
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            A quick guide to start using the platform
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 border rounded-lg">
              <div className="text-2xl mb-2">1</div>
              <h3 className="font-semibold mb-1">Explore the Dashboard</h3>
              <p className="text-sm text-muted-foreground">
                Get an overview of your account, recent activity, and market conditions.
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="text-2xl mb-2">2</div>
              <h3 className="font-semibold mb-1">Create a Strategy</h3>
              <p className="text-sm text-muted-foreground">
                Define your trading rules using our Python-based strategy builder.
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="text-2xl mb-2">3</div>
              <h3 className="font-semibold mb-1">Backtest Your Strategy</h3>
              <p className="text-sm text-muted-foreground">
                Test your strategy on historical data to see how it would perform.
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="text-2xl mb-2">4</div>
              <h3 className="font-semibold mb-1">Start Paper Trading</h3>
              <p className="text-sm text-muted-foreground">
                Execute trades in real-time simulation with virtual money.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FAQ */}
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {FAQS.map((faq, index) => (
            <div key={index} className="border-b last:border-0 pb-4 last:pb-0">
              <h3 className="font-semibold mb-2">{faq.question}</h3>
              <p className="text-sm text-muted-foreground">{faq.answer}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Glossary */}
      <Card>
        <CardHeader>
          <CardTitle>Trading Glossary</CardTitle>
          <CardDescription>
            Common trading terms and definitions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {GLOSSARY.map((item, index) => (
              <div
                key={index}
                className="flex items-start gap-4 p-2 rounded-lg hover:bg-muted/50"
              >
                <span className="font-semibold min-w-32">{item.term}</span>
                <span className="text-muted-foreground">{item.definition}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Strategy Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Development Guide</CardTitle>
          <CardDescription>
            How to write custom trading strategies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Basic Strategy Structure</h3>
            <pre className="p-4 bg-muted rounded-lg text-sm overflow-x-auto">
{`class MyStrategy(Strategy):
    # Define parameters
    fast_period = 10
    slow_period = 20

    def init(self):
        # Initialize indicators
        self.sma_fast = self.I(SMA, self.data.close, self.fast_period)
        self.sma_slow = self.I(SMA, self.data.close, self.slow_period)

    def next(self):
        # Define trading logic (called for each bar)
        if crossover(self.sma_fast, self.sma_slow):
            self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            self.sell()`}
            </pre>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Available Indicators</h3>
            <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
              <li>SMA (Simple Moving Average)</li>
              <li>EMA (Exponential Moving Average)</li>
              <li>RSI (Relative Strength Index)</li>
              <li>MACD (Moving Average Convergence Divergence)</li>
              <li>Bollinger Bands</li>
              <li>ATR (Average True Range)</li>
              <li>Stochastic Oscillator</li>
              <li>ADX (Average Directional Index)</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Trading Methods</h3>
            <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
              <li><code>self.buy(size=None, sl=None, tp=None)</code> - Open a long position</li>
              <li><code>self.sell(size=None, sl=None, tp=None)</code> - Open a short position</li>
              <li><code>self.position</code> - Access current position</li>
              <li><code>self.data.close[-1]</code> - Current closing price</li>
              <li><code>crossover(a, b)</code> - Returns True when a crosses above b</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Contact */}
      <Card>
        <CardHeader>
          <CardTitle>Need More Help?</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            This is an educational platform designed to help you learn forex trading.
            If you have questions or feedback, please reach out.
          </p>
          <div className="flex gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              GitHub Repository
            </a>
            <a
              href="mailto:support@example.com"
              className="text-primary hover:underline"
            >
              Contact Support
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
