"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
// Removed Image import
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
  FileText,
  ListChecks,
  Cpu,
} from "lucide-react";

export default function Page() {
  const { data: session } = useSession();
  const router = useRouter();

  const handleAuthAction = () => {
    if (!session) {
      toast.warning("Please login to continue");
    } else {
      router.push("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-black text-zinc-100 selection:bg-orange-500/30 overflow-hidden">
      {/* Background Gradients - Made slightly more prominent to fill space */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[10%] w-[600px] h-[600px] bg-orange-500/10 rounded-full blur-[150px]" />
        <div className="absolute bottom-[-20%] right-[10%] w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-20 md:py-32 flex flex-col items-center">
        {/* --- Hero Section --- */}
        <section className="flex flex-col items-center text-center space-y-8 max-w-4xl mb-24">
         

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.1]">
            Cut Code Review Time <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-100 to-zinc-500">
              & Bugs in Half.
            </span>
            <span className="block text-orange-500 mt-2">Instantly.</span>
          </h1>

          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl leading-relaxed">
            AI-powered reviews built for teams who move fast — but don&apos;t
            break things. Get detailed walkthroughs and pinpointed change
            summaries.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto pt-4">
            <Button
              onClick={handleAuthAction}
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
            <p className="text-zinc-400 text-lg">
              Everything you need to ship faster and safer.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Stat Card 1 */}
            <div className="p-8 rounded-3xl bg-zinc-900/30 border border-zinc-800 hover:border-orange-500/50 transition-colors group relative overflow-hidden">
               <div className="absolute right-0 top-0 opacity-5 transform translate-x-1/3 -translate-y-1/3 transition-transform group-hover:scale-110">
                  <Github size={200} />
               </div>
              <div className="h-12 w-12 bg-orange-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform relative z-10">
                <Github className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-4xl font-bold text-white mb-2 relative z-10">#1</h3>
              <p className="text-zinc-400 font-medium relative z-10">
                Most installed AI App on GitHub
              </p>
            </div>

            {/* Stat Card 2 */}
            <div className="p-8 rounded-3xl bg-zinc-900/30 border border-zinc-800 hover:border-purple-500/50 transition-colors group relative overflow-hidden">
                <div className="absolute right-0 top-0 opacity-5 transform translate-x-1/3 -translate-y-1/3 transition-transform group-hover:scale-110">
                  <Zap size={200} />
               </div>
              <div className="h-12 w-12 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform relative z-10">
                <Zap className="w-6 h-6 text-purple-500" />
              </div>
              <h3 className="text-4xl font-bold text-white mb-2 relative z-10">10x</h3>
              <p className="text-zinc-400 font-medium relative z-10">Faster code reviews</p>
            </div>

            {/* Stat Card 3 */}
            <div className="p-8 rounded-3xl bg-zinc-900/30 border border-zinc-800 hover:border-blue-500/50 transition-colors group relative overflow-hidden">
                 <div className="absolute right-0 top-0 opacity-5 transform translate-x-1/3 -translate-y-1/3 transition-transform group-hover:scale-110">
                  <Bug size={200} />
               </div>
              <div className="h-12 w-12 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform relative z-10">
                <Bug className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-4xl font-bold text-white mb-2 relative z-10">50%</h3>
              <p className="text-zinc-400 font-medium relative z-10">
                Reduction in production bugs
              </p>
            </div>
          </div>
        </section>

        {/* --- Feature Showcase (Redesigned without images) --- */}
        <section className="w-full max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 grid-rows-[auto_auto]">
            {/* Large Feature Card 1 (Left) */}
            <div className="md:col-span-2 row-span-2 rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-orange-500/30 transition-colors relative p-8 md:p-12 flex flex-col justify-between min-h-[400px]">
              <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              
              {/* Abstract Background Icon */}
              <Code2 className="absolute right-8 bottom-8 w-64 h-64 text-zinc-800/30 -rotate-12 pointer-events-none" />

              <div className="relative z-10 max-w-lg">
                  <div className="h-12 w-12 bg-orange-500/10 rounded-2xl flex items-center justify-center mb-6">
                    <Cpu className="w-6 h-6 text-orange-500" />
                  </div>
                <h3 className="text-3xl md:text-4xl font-bold mb-6">
                  Code reviews, reinvented.
                </h3>
                <p className="text-zinc-400 leading-relaxed mb-8 text-lg">
                  Get detailed walkthroughs, pinpointed change summaries, and
                  contextual insights that help you write cleaner code without the noise.
                </p>
                
                <div className="space-y-4">
                     <div className="flex items-center gap-3 text-zinc-200 font-medium">
                        <CheckCircle2 className="w-5 h-5 text-orange-500" />
                        <span>Context-aware AI feedback</span>
                    </div>
                    <div className="flex items-center gap-3 text-zinc-200 font-medium">
                        <CheckCircle2 className="w-5 h-5 text-orange-500" />
                        <span>Automated security checks</span>
                    </div>
                     <div className="flex items-center gap-3 text-zinc-200 font-medium">
                        <CheckCircle2 className="w-5 h-5 text-orange-500" />
                        <span>Performance optimization tips</span>
                    </div>
                </div>
              </div>
            </div>

            {/* Small Feature Card 1 (Top Right) */}
            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-purple-500/50 transition-colors relative">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="p-8 h-full flex flex-col relative z-10">
                <div className="mb-6">
                     <div className="h-10 w-10 bg-purple-500/10 rounded-xl flex items-center justify-center mb-4">
                        <FileText className="w-5 h-5 text-purple-500" />
                    </div>
                    <h3 className="text-xl font-bold mb-2">Fun AI Poems</h3>
                    <p className="text-zinc-400 text-sm">
                    Because clean code deserves good vibes.
                    </p>
                </div>
                {/* Faux Code Block Visual */}
                 <div className="mt-auto bg-zinc-950/50 border border-zinc-800/50 rounded-lg p-4 text-xs font-mono text-purple-300/70 select-none">
  <p>{`// A poem for your PR`}</p>
  <p className="text-zinc-500">{`function deploy() {`}</p>
  <p className="pl-4">{`Your Daddy reviews code with care and grace,`}</p>
  <p className="pl-4">{`A new calculator finds its rightful place.`}</p>
  <p className="pl-4">{`With numbers and ops, logic takes hold,`}</p>
  <p className="pl-4">{`A module robust, stories untold.`}</p>
  <p className="text-zinc-500">{`}`}</p>
</div>

              </div>
            </div>

            {/* Small Feature Card 2 (Bottom Right) */}
            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-blue-500/50 transition-colors relative">
                 <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="p-8 h-full flex flex-col relative z-10">
                 <div className="mb-6">
                    <div className="h-10 w-10 bg-blue-500/10 rounded-xl flex items-center justify-center mb-4">
                        <ListChecks className="w-5 h-5 text-blue-500" />
                    </div>
                    <h3 className="text-xl font-bold mb-2">Instant Summaries</h3>
                    <p className="text-zinc-400 text-sm">
                    Understand complex PRs in seconds with auto-generated summaries.
                    </p>
                </div>
                 {/* Faux Summary Visual */}
                 <div className="mt-auto space-y-2">
                    {[
                        "Refactored authentication middleware",
                        "Fixed race condition in user API",
                        "Updated dependency versions"
                    ].map((item, i) => (
                        <div key={i} className="flex items-center gap-2 bg-zinc-950/50 border border-zinc-800/50 rounded-lg p-2 text-xs text-zinc-300">
                            <CheckCircle2 className="w-3 h-3 text-blue-500 flex-shrink-0" />
                            <span className="truncate">{item}</span>
                        </div>
                    ))}
                 </div>
              </div>
            </div>

            {/* Large Feature Card 2 (Bottom Full Width) */}
            <div className="md:col-span-3 rounded-3xl border border-zinc-800 bg-zinc-900/30 overflow-hidden group hover:border-zinc-700 transition-colors relative p-8 md:p-12 flex flex-col md:flex-row items-center justify-between">
               <div className="absolute inset-0 bg-gradient-to-r from-zinc-900 via-transparent to-zinc-900 z-0 pointer-events-none" />
               <Zap className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] text-zinc-800/20 pointer-events-none z-0" />

                <div className="md:w-2/3 relative z-10">
                  <h3 className="text-2xl md:text-4xl font-bold mb-4">
                    Lightning Fast Reviews.
                  </h3>
                  <p className="text-zinc-400 leading-relaxed mb-6 text-lg max-w-xl">
                    Automated reviews in seconds, not hours. Keep your team
                    moving at full speed with instant feedback loops that integrate directly into your workflow.
                  </p>
                </div>
                 <div className="md:w-1/3 flex justify-start md:justify-end relative z-10">
                  <Button
                    onClick={handleAuthAction}
                    className="h-14 px-8 text-lg rounded-full bg-white text-black hover:bg-zinc-200 font-bold group/btn"
                  >
                    Start Speeding Up
                    <ArrowRight className="w-5 h-5 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                  </Button>
                </div>
            </div>
          </div>
        </section>

        {/* --- Footer CTA --- */}
        <section className="mt-32 text-center mb-20">
          <h2 className="text-3xl md:text-5xl font-bold mb-8">
            Ready to ship better code?
          </h2>
        
        </section>
      </div>
    </div>
  );
}