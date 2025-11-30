"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useSession } from "next-auth/react";
import { toast } from "sonner";
import {
  ArrowRight,
  CheckCircle2,
  Zap,
  Bug,
  Github,
  Terminal,
  Bot,
  Code2,
} from "lucide-react";

export default function Page() {
  const { data: session } = useSession();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-black text-zinc-100 selection:bg-orange-500/30">
      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[20%] w-[500px] h-[500px] bg-orange-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[20%] w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-20 md:py-32 flex flex-col items-center">
        {/* --- Hero Section --- */}
        <section className="flex flex-col items-center text-center space-y-8 max-w-4xl mb-24">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900/50 border border-zinc-800 text-sm text-zinc-400 mb-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
            </span>
            v2.0 is now live
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.1]">
            Cut Code Review Time <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-100 to-zinc-500">
              & Bugs in Half.
            </span>
            <span className="block text-orange-500 mt-2">Instantly.</span>
          </h1>

         <p className="text-lg md:text-xl text-zinc-400 max-w-2xl leading-relaxed">
  AI-powered reviews built for teams who move fast — but don&apos;t break things. Get detailed walkthroughs and pinpointed change summaries.
</p>


          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto pt-4">
            <Button
              onClick={() => {
                if (!session) {
                  toast.warning("Please login to continue");
                } else {
                  router.push("/dashboard");
                }
              }}
              className="h-12 px-8 text-base rounded-full bg-[#ff6b35] hover:bg-[#ff8f65] text-white font-medium transition-all shadow-[0_0_20px_-5px_rgba(255,107,53,0.5)] hover:shadow-[0_0_30px_-5px_rgba(255,107,53,0.6)]"
            >
              Get Started Free
            </Button>
            <Button
              variant="outline"
              className="h-12 px-8 text-base rounded-full border-zinc-800 bg-zinc-900/50 text-zinc-300 hover:bg-zinc-800 hover:text-white"
            >
              View Demo
            </Button>
          </div>
        </section>

        {/* --- Social Proof --- */}
        <section className="w-full max-w-5xl mb-32">
          <p className="text-center text-sm font-medium text-zinc-500 mb-8 uppercase tracking-widest">
            Trusted by engineering teams at
          </p>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 items-center justify-items-center opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
            {[
              { name: "TechFlow", icon: Terminal },
              { name: "Nexus", icon: Zap },
              { name: "CodeForge", icon: Code2 },
              { name: "ByteWave", icon: Github },
              { name: "Quantum", icon: Bot },
              { name: "Velocity", icon: CheckCircle2 },
            ].map((company, i) => (
              <div
                key={i}
                className="flex items-center gap-2 group cursor-default"
              >
                <company.icon className="w-6 h-6 text-zinc-300 group-hover:text-orange-500 transition-colors" />
                <span className="font-bold text-lg text-zinc-300 group-hover:text-white transition-colors">
                  {company.name}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* --- Bento Grid Benefits --- */}
        <section className="w-full max-w-6xl mb-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Why CodeDaddy?
            </h2>
            <p className="text-zinc-400">
              Everything you need to ship faster and safer.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Stat Card 1 */}
            <div className="p-8 rounded-3xl bg-zinc-900/30 border border-zinc-800 hover:border-orange-500/50 transition-colors group">
              <div className="h-12 w-12 bg-orange-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Github className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-4xl font-bold text-white mb-2">#1</h3>
              <p className="text-zinc-400 font-medium">
                Most installed AI App on GitHub
              </p>
            </div>

            {/* Stat Card 2 */}
            <div className="p-8 rounded-3xl bg-zinc-900/30 border border-zinc-800 hover:border-purple-500/50 transition-colors group">
              <div className="h-12 w-12 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-purple-500" />
              </div>
              <h3 className="text-4xl font-bold text-white mb-2">10x</h3>
              <p className="text-zinc-400 font-medium">Faster code reviews</p>
            </div>

            {/* Stat Card 3 */}
            <div className="p-8 rounded-3xl bg-zinc-900/30 border border-zinc-800 hover:border-blue-500/50 transition-colors group">
              <div className="h-12 w-12 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Bug className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-4xl font-bold text-white mb-2">50%</h3>
              <p className="text-zinc-400 font-medium">
                Reduction in production bugs
              </p>
            </div>
          </div>
        </section>

        {/* --- Feature Showcase --- */}
        <section className="w-full max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Large Feature Card (Left) */}
            <div className="md:col-span-2 rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-zinc-700 transition-colors">
              <div className="flex flex-col md:flex-row h-full">
                <div className="p-8 md:w-1/2 flex flex-col justify-center">
                  <h3 className="text-2xl md:text-3xl font-bold mb-4">
                    Code reviews, reinvented.
                  </h3>
                  <p className="text-zinc-400 leading-relaxed mb-6">
                    Get detailed walkthroughs, pinpointed change summaries, and
                    contextual insights that help you write cleaner code.
                  </p>
                  <div className="flex items-center gap-2 text-orange-500 font-medium text-sm">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Context-aware feedback</span>
                  </div>
                </div>
                <div className="md:w-1/2 bg-zinc-900/50 border-t md:border-t-0 md:border-l border-zinc-800 relative">
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-900/90 to-transparent z-10" />
                  <div className="p-6 h-full flex items-center justify-center">
                    {/* Replace src with your actual image path */}
                    <div className="relative w-full aspect-square md:aspect-auto md:h-64 rounded-xl overflow-hidden shadow-2xl border border-zinc-700/50">
                      <Image
                        src="/walk.png"
                        alt="Walkthrough Interface"
                        fill
                        className="object-cover object-top"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Small Feature Card (Right Top) */}
            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-purple-500/50 transition-colors">
              <div className="p-6 h-full flex flex-col">
                <div className="h-40 relative w-full mb-6 rounded-xl overflow-hidden border border-zinc-800 group-hover:scale-[1.02] transition-transform duration-500">
                  <Image
                    src="/poem1.png"
                    alt="AI Poem"
                    fill
                    className="object-cover"
                  />
                </div>
                <h3 className="text-xl font-bold mb-2">Fun AI Poems</h3>
                <p className="text-zinc-400 text-sm">
                  Because clean code deserves good vibes.
                </p>
              </div>
            </div>

            {/* Small Feature Card (Left Bottom) */}
            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-blue-500/50 transition-colors">
              <div className="p-6 h-full flex flex-col">
                <div className="h-40 relative w-full mb-6 rounded-xl overflow-hidden border border-zinc-800 group-hover:scale-[1.02] transition-transform duration-500">
                  <Image
                    src="/summary.png"
                    alt="Summary"
                    fill
                    className="object-cover object-top"
                  />
                </div>
                <h3 className="text-xl font-bold mb-2">Instant Summaries</h3>
                <p className="text-zinc-400 text-sm">
                  Understand complex PRs in seconds with auto-generated
                  summaries.
                </p>
              </div>
            </div>

            {/* Large Feature Card (Right Bottom) */}
            <div className="md:col-span-2 rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-zinc-700 transition-colors">
              <div className="flex flex-col md:flex-row-reverse h-full">
                <div className="p-8 md:w-1/2 flex flex-col justify-center">
                  <h3 className="text-2xl md:text-3xl font-bold mb-4">
                    Fast Reviews.
                  </h3>
                  <p className="text-zinc-400 leading-relaxed mb-6">
                    Automated reviews in seconds, not hours. Keep your team
                    moving at full speed with instant feedback loops.
                  </p>
                  <Button
                    variant="link"
                    className="text-white p-0 h-auto justify-start hover:text-orange-500 group/link"
                  >
                    See how it works{" "}
                    <ArrowRight className="w-4 h-4 ml-1 group-hover/link:translate-x-1 transition-transform" />
                  </Button>
                </div>
                <div className="md:w-1/2 bg-zinc-900/50 border-t md:border-t-0 md:border-r border-zinc-800 relative">
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-900/90 to-transparent z-10" />
                  <div className="p-6 h-full flex items-center justify-center">
                    <div className="relative w-full aspect-square md:aspect-auto md:h-64 rounded-xl overflow-hidden shadow-2xl border border-zinc-700/50">
                      <Image
                        src="/review.png"
                        alt="Review Interface"
                        fill
                        className="object-cover object-top"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* --- Footer CTA --- */}
        <section className="mt-32 text-center">
          <h2 className="text-3xl font-bold mb-6">
            Ready to ship better code?
          </h2>
          <Button
            onClick={() =>
              !session
                ? toast.warning("Please login")
                : router.push("/dashboard")
            }
            className="h-12 px-8 rounded-full bg-white text-black hover:bg-zinc-200 font-bold"
          >
            Start for Free
          </Button>
        </section>
      </div>
    </div>
  );
}
