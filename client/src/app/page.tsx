"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useSession } from "next-auth/react";
import { toast } from "sonner";

export default function Page() {
  const { data: session } = useSession();


  const router = useRouter()
  return (
    <div className="min-h-screen overflow-y-auto">
      <div className="max-w-6xl mx-auto flex flex-col justify-center items-center px-6 py-20 md:py-32 text-center">
        {/* Hero Section */}
        <section className="space-y-6 w-full">
          <h1 className={`text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-tight text-left sm:text-center`}>
            Cut Code Review Time & Bugs in Half. <br className="hidden sm:block" />
            <span className="text-orange-500">Instantly.</span>
          </h1>


          <p className="leading-7 [&:not(:first-child)]:mt-6">
            AI-powered reviews built for teams who move fast — but don’t break things.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 mt-8 w-full sm:w-auto">
            <Button onClick={() => {
              if (!session) {
                toast.warning("Please login to continue")
              } else {
                router.push("/dashboard")
              }
            }} className="px-6 py-3 rounded-xl bg-orange-600 hover:bg-orange-500  font-medium transition w-full sm:w-auto">
              Get Started Free
            </Button>

          </div>
        </section>

        <h3 className="text-2xl font-extrabold  p-4 m-2 ">Benifits</h3>
        <section className="grid gap-4 w-full grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 m-4">


          <div className="dark:bg-[#171717] h-40 flex flex-col items-center justify-center col-span-1 sm:col-span-2 lg:col-span-2 rounded-2xl px-8 text-center  border border-[#171717]">
            <p className="text-2xl md:text-3xl font-bold text-left">
              The most installed AI App on GitHub
            </p>

          </div>

          <div className="dark:bg-[#171717] h-40 flex flex-col items-center justify-center col-span-1 sm:col-span-1 lg:col-span-1 rounded-2xl px-4 text-center border border-orange-500">
            <p className="text-xl font-semibold  mb-1">AI-Powered Reviews</p>

          </div>

          <div className="dark:bg-[#171717] h-40 flex flex-col items-center justify-center col-span-1 sm:col-span-1 lg:col-span-1 rounded-2xl px-4 text-center border border-[#894681]">
            <p className="text-xl font-semibold  mb-1">Cut Bugs in Half</p>

          </div>
        </section>


        <h3 className="text-2xl font-extrabold text-gray-400 p-4 m-2 ">Trusted By top companies</h3>

        <section className="w-full max-w-5xl">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 items-center justify-items-center opacity-60 hover:opacity-100 transition-opacity duration-300">

            {/* TechFlow Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-32 h-12" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="5" y="10" width="20" height="20" rx="4" fill="currentColor" />
                <text x="32" y="25" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="currentColor">TechFlow</text>
              </svg>
            </div>

            {/* Nexus Labs Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-32 h-12" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="15" cy="20" r="8" stroke="currentColor" strokeWidth="2" fill="none" />
                <circle cx="15" cy="20" r="3" fill="currentColor" />
                <text x="28" y="25" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="currentColor">Nexus</text>
              </svg>
            </div>

            {/* CodeForge Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-32 h-12" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 15L15 20L10 25" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M20 15L15 20L20 25" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                <text x="26" y="25" fontFamily="Arial, sans-serif" fontSize="15" fontWeight="bold" fill="currentColor">CodeForge</text>
              </svg>
            </div>

            {/* ByteWave Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-32 h-12" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 20 Q15 12, 22 20 T36 20" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" />
                <text x="40" y="25" fontFamily="Arial, sans-serif" fontSize="15" fontWeight="bold" fill="currentColor">ByteWave</text>
              </svg>
            </div>

            {/* Quantum Systems Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-36 h-12" viewBox="0 0 130 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12L18 20L12 28M18 12L12 20L18 28" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <text x="26" y="25" fontFamily="Arial, sans-serif" fontSize="14" fontWeight="bold" fill="currentColor">Quantum</text>
              </svg>
            </div>

            {/* Prism Tech Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-32 h-12" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <polygon points="15,12 10,28 20,28" fill="currentColor" />
                <text x="26" y="25" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="currentColor">Prism</text>
              </svg>
            </div>

            {/* Velocity Labs Logo */}
            <div className="flex items-center justify-center md:col-start-3">
              <svg className="w-36 h-12" viewBox="0 0 130 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 15L18 20L8 25" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                <text x="24" y="25" fontFamily="Arial, sans-serif" fontSize="15" fontWeight="bold" fill="currentColor">Velocity</text>
              </svg>
            </div>

            {/* Apex Digital Logo */}
            <div className="flex items-center justify-center">
              <svg className="w-32 h-12" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 28L10 18L15 8L20 18Z" fill="currentColor" />
                <text x="26" y="25" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="currentColor">Apex</text>
              </svg>
            </div>

          </div>
        </section>
        <section>
          <h1 className="scroll-m-20 text-center text-4xl font-extrabold tracking-tight text-balance mt-16 mb-8">AI Code Reviews</h1>

          <section className="w-full max-w-5xl">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Large card - spans 2 columns */}
              <div className="md:col-span-2 rounded-2xl border border-[#171717] dark:bg-[#171717] overflow-hidden group hover:border-orange-500 transition-colors duration-300 flex flex-col md:flex-row items-center">
                <div className="p-8 md:w-1/2 ">
                  <h3 className="text-3xl font-bold mb-4 text-left">Code reviews, reinvented.</h3>
                  <p className=" leading-relaxed text-left">
                    Meet <span className="font-semibold ">CodeDaddy ,</span>
                    Get detailed walkthroughs, pinpointed change summaries, and contextual insights that help you write cleaner, safer, and smarter code.
                  </p>
                </div>
                <div className="md:w-1/2 p-4 flex flex-col items-start justify-start">
                  <h2 className="scroll-m-20 border-b pb-2 text-xl font-semibold tracking-tight first:mt-0">
                    Walk through
                  </h2>
                  <Image
                    src="/walk.png"
                    alt="Code review interface"
                    width={600}
                    height={400}
                    className="w-full h-auto object-contain rounded-2xl mt-4"
                  />
                </div>

              </div>
              {/* Small card */}
              <div className="rounded-2xl border border-[#171717] dark:bg-[#171717] overflow-hidden group hover:border-purple-500 transition-colors duration-300">
                <div className="h-48 flex items-center justify-center p-2">
                  <Image
                    src="/poem1.png"
                    alt="AI-generated poem interface"
                    width={600}
                    height={400}
                    className="w-full h-auto object-contain rounded-xl border border-amber-50"
                  />
                </div>

                <div className="m-4 text-left">
                  <blockquote className="border-l-2 pl-2 italic text-sm">
                    CodeDaddy sometimes drops a fun AI poem because clean code deserves good vibes.
                  </blockquote>

                </div>

              </div>

              <div className="rounded-2xl border border-[#171717] dark:bg-[#171717] overflow-hidden group hover:border-purple-500 transition-colors duration-300">
                <div className="h-48 flex items-center justify-center p-2">
                  <Image
                    src="/summary.png"
                    alt="AI-generated poem interface"
                    width={600}
                    height={400}
                    className="w-full h-auto object-contain rounded-xl border border-amber-50"
                  />
                </div>

                <div className="m-4 text-left">
                  <h2 className="text-l font-bold mb-2">Simple PR summaries.</h2>
                  <p className="text-xs leading-relaxed text-left">
                    See the list of changed files and a one-line description.
                  </p>

                </div>

              </div>

              <div className="md:col-span-2 rounded-2xl border border-[#171717] dark:bg-[#171717] overflow-hidden group hover:border-orange-500 transition-colors duration-300 flex flex-col md:flex-row items-center">
                <div className="md:w-1/2 p-4 flex flex-col items-start justify-start">
                  <h2 className="scroll-m-20 border-b pb-2 text-xl font-semibold tracking-tight first:mt-0">
                    Walk through
                  </h2>
                  <Image
                    src="/review.png"
                    alt="Code review interface"
                    width={600}
                    height={400}
                    className="w-full h-auto object-contain rounded-2xl mt-4"
                  />
                </div>
                <div className="p-8 md:w-1/2 ">
                  <h3 className="text-3xl font-bold mb-4 text-left">Fast Reviews.</h3>
                  <p className=" leading-relaxed text-left">
                    Automated reviews in seconds, not hours. Keep your team moving at full speed with instant feedback.
                  </p>
                </div>


              </div>
            </div>
          </section>

        </section>
      </div>
    </div>
  );
}
