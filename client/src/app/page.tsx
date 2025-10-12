"use client";

export default function Page() {
  return (
    <div className="min-h-screen overflow-y-auto">
      <div className="max-w-6xl mx-auto flex flex-col justify-center items-center px-6 py-20 md:py-32 text-center">
        {/* Hero Section */}
        <section className="space-y-6 w-full">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-tight">
            Cut Code Review Time & Bugs in Half. <br className="hidden sm:block" />
            <span className="text-orange-500">Instantly.</span>
          </h1>

          <p className="text-gray-400 text-base sm:text-lg md:text-xl max-w-2xl mx-auto px-2">
            AI-powered reviews built for teams who move fast — but don’t break things.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 mt-8 w-full sm:w-auto">
            <button className="px-6 py-3 rounded-xl bg-orange-600 hover:bg-orange-500  font-medium transition w-full sm:w-auto">
              Get Started Free
            </button>
       
          </div>
        </section>

        <h3 className="text-2xl font-extrabold text-gray-400 p-4 m-2 ">Benifits</h3> 
      <section className="grid gap-4 w-full grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 m-4">
 

        <div className="dark:bg-[#171717] h-40 flex flex-col items-center justify-center col-span-1 sm:col-span-2 lg:col-span-2 rounded-2xl px-8 text-center  border border-[#171717]">
          <p className="text-2xl md:text-3xl font-bold">
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



      </div>
    </div>
  );
}
