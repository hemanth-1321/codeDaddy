"use client";

import { useState, useEffect } from "react";
import { signIn, signOut, useSession } from "next-auth/react";
import {
  Code2,
  Sparkles,
  Zap,
  Shield,
  GitBranch,
  Users,
  ArrowRight,
  Check,
  Github,
  Star,
} from "lucide-react";

export default function DashboardPage() {
  const { data: session } = useSession();
  const [scrollY, setScrollY] = useState(0);
  const [repos, setRepos] = useState<any[]>([]);
  const [installations, setInstallations] = useState<any[]>([]);
  const [hasInstallation, setHasInstallation] = useState(false);

  const APP_SLUG = "codedaddy-reviewer"; // 👈 your GitHub App slug

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const features = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "AI-Powered Reviews",
      description:
        "Get intelligent code reviews that catch bugs, suggest improvements, and enforce best practices automatically.",
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Lightning Fast",
      description:
        "Reviews completed in seconds, not hours. Keep your development velocity high without compromising quality.",
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Security First",
      description:
        "Detect vulnerabilities and security issues before they reach production. Stay compliant and secure.",
    },
    {
      icon: <GitBranch className="w-6 h-6" />,
      title: "Seamless Integration",
      description:
        "Works directly with your GitHub workflow. No configuration needed, just install and go.",
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Team Collaboration",
      description:
        "Share insights across your team. Learn from AI suggestions and improve code quality together.",
    },
    {
      icon: <Code2 className="w-6 h-6" />,
      title: "Multi-Language Support",
      description:
        "Supports all major programming languages with specialized analysis for each.",
    },
  ];

  const pricing = [
    {
      name: "Open Source",
      price: "Free",
      period: "forever",
      features: [
        "Unlimited public repos",
        "Basic code analysis",
        "Community support",
        "Standard response time",
      ],
    },
    {
      name: "Pro",
      price: "$29",
      period: "per month",
      popular: true,
      features: [
        "Unlimited private repos",
        "Advanced AI reviews",
        "Priority support",
        "Custom rules & configs",
        "Team analytics",
      ],
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "contact us",
      features: [
        "Self-hosted option",
        "Dedicated support",
        "SLA guarantees",
        "Advanced security",
        "Custom integrations",
        "Training sessions",
      ],
    },
  ];

  async function fetchInstallations() {
    const res = await fetch("http://localhost:8000/installations", {
      headers: { Authorization: `Bearer ${session?.accessToken}` },
    });
    const data = await res.json();
    setInstallations(data.installations || []);
    setHasInstallation((data.installations || []).length > 0); // 👈 update state
  }

  async function fetchRepos(installationId: string) {
    const res = await fetch(
      `http://localhost:8000/repos?installation_id=${installationId}`,
      {
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      }
    );
    const data = await res.json();
    setRepos(data.repositories || []);
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
        <div className="text-center p-6 bg-slate-900/50 backdrop-blur-md rounded-xl">
          <h1 className="text-3xl font-bold mb-4">Login to Code Daddy</h1>
          <button
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg transition text-white font-semibold"
            onClick={() => signIn("github")}
          >
            Sign in with GitHub
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-lg border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code2 className="w-8 h-8 text-purple-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Code Daddy
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="hover:text-purple-400 transition">
              Features
            </a>
            <a href="#pricing" className="hover:text-purple-400 transition">
              Pricing
            </a>
            <a href="#about" className="hover:text-purple-400 transition">
              About
            </a>
            <button className="px-6 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center gap-2">
              <Github className="w-5 h-5" />
              Install App
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 text-center">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Welcome, <span className="text-purple-400">{session.user?.name}</span>
        </h1>
        <p className="text-xl text-slate-300 mb-6">
          Manage your GitHub App installations and repositories from here.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-10">
          <button
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg transition text-white font-semibold"
            onClick={() => signOut()}
          >
            Logout
          </button>

          {!hasInstallation && (
            <a
              href={`https://github.com/apps/${APP_SLUG}/installations/new`}
              target="_blank"
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg font-semibold text-white transition"
            >
              Install GitHub App
            </a>
          )}
        </div>

        {/* Installations */}
        <div className="bg-slate-900/50 backdrop-blur-md rounded-xl p-6 max-w-4xl mx-auto mb-10">
          <h2 className="text-2xl font-bold mb-4">Your Installations</h2>
          <button
            className="px-4 py-2 bg-blue-500 hover:bg-blue-400 rounded-lg font-semibold mb-4"
            onClick={fetchInstallations}
          >
            Fetch Installations
          </button>
          <ul className="space-y-2">
            {installations.map((inst: any) => (
              <li
                key={inst.id}
                className="flex justify-between items-center bg-slate-800/50 p-2 rounded"
              >
                <span>{inst.account.login}</span>
                <button
                  className="px-3 py-1 bg-green-500 hover:bg-green-400 rounded"
                  onClick={() => fetchRepos(inst.id)}
                >
                  Get Repos
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Repositories */}
        <div className="bg-slate-900/50 backdrop-blur-md rounded-xl p-6 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Repositories</h2>
          <ul className="space-y-2">
            {repos.map((repo) => (
              <li key={repo.id} className="bg-slate-800/50 p-2 rounded">
                {repo.full_name}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-7xl mx-auto text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Features of <span className="text-purple-400">Code Daddy</span>
          </h2>
          <p className="text-xl text-slate-300">
            Powerful features that make code review effortless
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {features.map((feature, i) => (
            <div
              key={i}
              className="group p-6 bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl hover:border-purple-500/50 transition-all hover:scale-105 cursor-pointer"
            >
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center text-purple-400 mb-4 group-hover:bg-purple-500/30 transition">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Simple, transparent <span className="text-purple-400">pricing</span>
          </h2>
          <p className="text-xl text-slate-300">
            Choose the plan that's right for your team
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {pricing.map((plan, i) => (
            <div
              key={i}
              className={`relative p-8 rounded-2xl border ${
                plan.popular
                  ? "bg-gradient-to-br from-purple-900/50 to-pink-900/50 border-purple-500 transform scale-105"
                  : "bg-slate-800/50 border-slate-700"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}
              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-slate-400 ml-2">/ {plan.period}</span>
              </div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((f, j) => (
                  <li key={j} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-300">{f}</span>
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  plan.popular
                    ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500"
                    : "bg-slate-700 hover:bg-slate-600"
                }`}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800 text-center">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 justify-center md:justify-start">
            <Code2 className="w-6 h-6 text-purple-400" />
            <span className="font-bold">Code Daddy</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-400 justify-center md:justify-start">
            <a href="#" className="hover:text-purple-400 transition">
              Privacy
            </a>
            <a href="#" className="hover:text-purple-400 transition">
              Terms
            </a>
            <a href="#" className="hover:text-purple-400 transition">
              Docs
            </a>
            <a href="#" className="hover:text-purple-400 transition">
              Support
            </a>
          </div>
          <div className="text-sm text-slate-400">
            © 2025 Code Daddy. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
