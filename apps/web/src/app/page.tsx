import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { BarChart2, TrendingUp, Bot } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold">Forex Simulator</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/auth/signin">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/auth/signin">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1">
        <section className="container mx-auto px-4 py-24 text-center">
          <h1 className="mb-6 text-5xl font-bold tracking-tight">
            Master Forex Trading
            <br />
            <span className="text-primary">Without the Risk</span>
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
            Practice forex trading with virtual money, backtest your strategies on historical data,
            and learn with AI-powered insights. Perfect for beginners and experienced traders alike.
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/auth/signin">
              <Button size="lg">Start Trading</Button>
            </Link>
            <Link href="/about">
              <Button size="lg" variant="outline">
                Learn More
              </Button>
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="border-t bg-muted/50 py-24">
          <div className="container mx-auto px-4">
            <h2 className="mb-12 text-center text-3xl font-bold">Key Features</h2>
            <div className="grid gap-8 md:grid-cols-3">
              <FeatureCard
                title="Backtesting Engine"
                description="Test your trading strategies on years of historical forex data. See exactly how your strategy would have performed."
                icon={<BarChart2 className="h-10 w-10 text-primary" />}
              />
              <FeatureCard
                title="Paper Trading"
                description="Trade with virtual money in real-time market conditions. No risk, all the learning experience."
                icon={<TrendingUp className="h-10 w-10 text-primary" />}
              />
              <FeatureCard
                title="AI Insights"
                description="Get AI-powered analysis, pattern recognition, and trading signals to enhance your learning."
                icon={<Bot className="h-10 w-10 text-primary" />}
              />
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-24">
          <div className="container mx-auto px-4">
            <div className="grid gap-8 text-center md:grid-cols-4">
              <StatCard value="7+" label="Major Currency Pairs" />
              <StatCard value="10+ Years" label="Historical Data" />
              <StatCard value="$100K" label="Virtual Starting Capital" />
              <StatCard value="100:1" label="Leverage Options" />
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Forex Trading Simulator - Educational Platform</p>
          <p className="mt-2">
            This is a simulation platform for educational purposes only. Not financial advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  title,
  description,
  icon,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
      <div className="mb-4">{icon}</div>
      <h3 className="mb-2 text-xl font-semibold">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-4xl font-bold text-primary">{value}</div>
      <div className="mt-1 text-muted-foreground">{label}</div>
    </div>
  );
}
